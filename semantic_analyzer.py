"""
KUCODE Semantic Analyzer
========================
Implements L-Attributed Syntax-Directed Definition (L-Attributed SDD) over the
LL(1) grammar via recursive descent.

Responsibilities:
  1. Semantic checks defined in semantic_rules.txt
  2. Three-Address Code (TAC) emission as Quadruples: (op, arg1, arg2, result)

Two-pass design:
  Pass 1 — linear scan to collect group types, worldwide variables, and
            function signatures (enables forward references).
  Pass 2 — full recursive descent mirroring the LL(1) grammar; semantic
            checking and TAC emission happen in tandem.

Usage:
    from semantic_analyzer import SemanticAnalyzer
    # tokens = filtered list from prepare_tokens_for_parser()
    analyzer = SemanticAnalyzer(tokens)
    quadruples, errors = analyzer.analyze()
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


# ═══════════════════════════════════════════════════════════════
# TYPE-SYSTEM CONSTANTS
# ═══════════════════════════════════════════════════════════════

NUMERIC_TYPES   = {'num', 'decimal', 'bigdecimal'}
BOOL_TYPE       = 'bool'
TEXT_TYPE       = 'text'
CHAR_TYPE       = 'letter'
PRIMITIVE_TYPES = NUMERIC_TYPES | {BOOL_TYPE, TEXT_TYPE, CHAR_TYPE}
NUMERIC_OR_BOOL = NUMERIC_TYPES | {BOOL_TYPE}   # truthy-coercion domain
RETURN_TYPES    = PRIMITIVE_TYPES | {'empty'}

ARITHMETIC_OPS  = {'+', '-', '*', '/', '%', '**'}
RELATIONAL_OPS  = {'>', '<', '>=', '<='}
EQUALITY_OPS    = {'==', '!='}
LOGICAL_OPS     = {'&&', '||', '!'}
COMPOUND_ASSIGN = {'+=', '-=', '*=', '/=', '%=', '**='}

# Tokens that can begin an argument / expression
EXPR_STARTERS = {
    'num_lit', 'decimal_lit', 'string_lit', 'char_lit',
    'Yes', 'No', 'identifier', '(', '-', '!', 'size'
}

# Tokens that can begin a statement
STMT_STARTERS = {
    'check', 'select', 'each', 'during',
    'identifier', 'show', 'read',
    'fixed', 'list',
    *PRIMITIVE_TYPES
}


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class SemanticError:
    message: str
    line: int = 0
    col: int = 0

    def __str__(self) -> str:
        return f"Semantic Error at Line {self.line}, Col {self.col}: {self.message}"


@dataclass
class Quadruple:
    """One TAC instruction: (op, arg1, arg2, result)"""
    op: str
    arg1: str = '_'
    arg2: str = '_'
    result: str = '_'

    def __str__(self) -> str:
        return f"({self.op}, {self.arg1}, {self.arg2}, {self.result})"


@dataclass
class Symbol:
    name: str
    kind: str                          # 'variable' | 'function' | 'group' | 'parameter' | 'list'
    data_type: str                     # primitive type name, group name, or return type
    is_fixed: bool = False
    is_worldwide: bool = False
    is_list: bool = False
    list_dim: int = 0                  # 1 or 2
    params: List[Tuple[str, str]] = field(default_factory=list)   # [(type, name), ...]
    return_type: str = ''
    group_members: Dict[str, str] = field(default_factory=dict)   # {member_name: type}
    line: int = 0
    col: int = 0


class SymbolTable:
    """Scope-stacked symbol table."""

    def __init__(self) -> None:
        # Index 0 = global scope; higher indices = deeper scopes
        self.scopes: List[Dict[str, Symbol]] = [{}]

    def enter_scope(self) -> None:
        self.scopes.append({})

    def exit_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, symbol: Symbol) -> bool:
        """Declare in the current (innermost) scope.
        Returns False if the name is already declared in the same scope."""
        current = self.scopes[-1]
        if symbol.name in current:
            return False
        current[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        """Search from innermost to outermost scope."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    def lookup_global(self, name: str) -> Optional[Symbol]:
        return self.scopes[0].get(name)

    def lookup_in_enclosing_local(self, name: str) -> Optional[Symbol]:
        """Search scopes between global and current (enclosing local scopes only).
        Excludes scope[0] (global) and scope[-1] (current)."""
        for scope in self.scopes[1:-1]:
            if name in scope:
                return scope[name]
        return None

    @property
    def depth(self) -> int:
        return len(self.scopes)


# ═══════════════════════════════════════════════════════════════
# TYPE HELPERS
# ═══════════════════════════════════════════════════════════════

def infer_literal_type(token_type: str, value: str = '') -> str:
    """
    Map a literal token type to its semantic data type.

    For decimal_lit, the inferred type depends on the number of digits
    after the decimal point:
      <= 11 digits  →  decimal
      12 – 16 digits →  bigdecimal
      > 16 digits   →  error (returned as 'bigdecimal' so analysis continues)
    """
    if token_type == 'decimal_lit':
        frac_digits = 0
        if '.' in str(value):
            frac_digits = len(str(value).split('.')[1])
        if frac_digits <= 11:
            return 'decimal'
        elif frac_digits <= 16:
            return 'bigdecimal'
        else:
            # > 16: will trigger an error in _literal(); return bigdecimal
            # so downstream type-checking can still proceed
            return 'bigdecimal'

    mapping = {
        'num_lit':    'num',
        'string_lit': 'text',
        'char_lit':   'letter',
        'Yes':        'bool',
        'No':         'bool',
    }
    return mapping.get(token_type, 'unknown')


def is_numeric(dtype: str) -> bool:
    return dtype in NUMERIC_TYPES


def is_numeric_or_bool(dtype: str) -> bool:
    return dtype in NUMERIC_OR_BOOL


def is_valid_index_type(dtype: str) -> bool:
    """Index expressions accept num or bool (bool coerces to 0/1)."""
    return dtype in ('num', 'bool', 'unknown')


# Numeric widening rank: higher rank = wider type.
# Widening (narrow → wide) is allowed; narrowing (wide → narrow) is not.
_NUMERIC_RANK: dict = {'num': 0, 'decimal': 1, 'bigdecimal': 2}


def type_compatible(declared: str, expr: str) -> bool:
    """
    Check whether expr_type is assignable to declared_type.

    Numeric type hierarchy (widening only):
      num  <  decimal  <  bigdecimal

    Bool ↔ numeric coercion:
      - num / decimal / bigdecimal ← bool   (Yes = 1, No = 0)
      - bool ← any numeric type             (non-zero = Yes, 0 = No)
        This includes decimal (e.g. bool a = 5.5; is valid)

    text  ← text only
    letter← letter only
    """
    if declared == 'unknown' or expr == 'unknown':
        return True
    if declared == expr:
        return True
    # bool → num / decimal / bigdecimal  (Yes = 1, No = 0)
    if expr == BOOL_TYPE and declared in NUMERIC_TYPES:
        return True
    # num / decimal / bigdecimal → bool  (truthy coercion, any numeric)
    if declared == BOOL_TYPE and expr in NUMERIC_TYPES:
        return True
    # Numeric widening: expr rank must be <= declared rank
    if declared in _NUMERIC_RANK and expr in _NUMERIC_RANK:
        return _NUMERIC_RANK[expr] <= _NUMERIC_RANK[declared]
    return False


def result_type_of_op(op: str, left: str, right: str) -> str:
    """Infer the result type of a binary operation."""
    if op in ARITHMETIC_OPS:
        for wide in ('bigdecimal', 'decimal'):
            if left == wide or right == wide:
                return wide
        return 'num'
    if op in RELATIONAL_OPS | EQUALITY_OPS | LOGICAL_OPS:
        return 'bool'
    return 'unknown'


# ═══════════════════════════════════════════════════════════════
# SEMANTIC ANALYZER
# ═══════════════════════════════════════════════════════════════

class SemanticAnalyzer:
    """
    L-Attributed SDD semantic analyzer + TAC emitter for KUCODE.

    Input : filtered token list produced by prepare_tokens_for_parser().
    Output: (List[Quadruple], List[SemanticError])
    """

    def __init__(self, tokens: list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None

        self.errors: List[SemanticError] = []
        self.quadruples: List[Quadruple] = []
        self.symbol_table = SymbolTable()

        self._temp_count = 0
        self._label_count = 0

        # Context tracking
        self.current_function: Optional[Symbol] = None
        self._has_return: bool = False

    # ──────────────────────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ──────────────────────────────────────────────────────────

    def analyze(self) -> Tuple[List[Quadruple], List[SemanticError]]:
        """Run both passes and return (quadruples, errors)."""
        self._pass1()
        # Reset position for Pass 2
        self.pos = 0
        self.current = self.tokens[0] if self.tokens else None
        self._pass2()
        return self.quadruples, self.errors

    # ──────────────────────────────────────────────────────────
    # TOKEN MANAGEMENT
    # ──────────────────────────────────────────────────────────

    def _advance(self) -> None:
        self.pos += 1
        self.current = (
            self.tokens[self.pos] if self.pos < len(self.tokens) else None
        )

    def _current_type(self) -> str:
        return self.current.type if self.current else '$'

    def _token_location(self, token=None) -> Tuple[int, int]:
        t = token if token is not None else self.current
        if t and hasattr(t, 'pos_start') and t.pos_start:
            return t.pos_start.ln + 1, t.pos_start.col + 1
        return 0, 0

    def _consume(self, expected_type: str):
        """
        Consume the current token if it matches expected_type.
        Records an error and advances anyway to prevent infinite loops.
        """
        tok = self.current
        if tok is None:
            self._error(f"Expected '{expected_type}', reached end of input")
            return tok
        if tok.type != expected_type:
            self._error(
                f"Expected '{expected_type}', got '{tok.type}'", tok
            )
            self._advance()
            return tok
        self._advance()
        return tok

    def _match(self, *types: str) -> bool:
        """Return True if current token type is in types."""
        return self._current_type() in types

    def _peek_next_type(self) -> str:
        """Return the type of the token one position ahead."""
        next_pos = self.pos + 1
        if next_pos < len(self.tokens):
            return self.tokens[next_pos].type
        return '$'

    def _error(self, message: str, token=None) -> None:
        ln, col = self._token_location(token)
        self.errors.append(SemanticError(message, ln, col))

    def _check_name_conflicts(
        self, vname: str, name_tok, label: str = 'Variable'
    ) -> None:
        """Emit an error if vname conflicts with a worldwide variable or
        shadows a variable in any enclosing local scope."""
        # Check worldwide conflict (any depth — worldwide can never be shadowed)
        global_sym = self.symbol_table.lookup_global(vname)
        if global_sym is not None and global_sym.is_worldwide:
            qualifier = 'fixed worldwide' if global_sym.is_fixed else 'worldwide'
            self._error(
                f"{label} '{vname}' conflicts with {qualifier} variable "
                f"'{vname}'; worldwide variables cannot be shadowed or redeclared",
                name_tok
            )
            return
        # Check enclosing local scope shadowing
        outer_sym = self.symbol_table.lookup_in_enclosing_local(vname)
        if outer_sym is not None:
            qualifier = 'fixed ' if outer_sym.is_fixed else ''
            self._error(
                f"{label} '{vname}' shadows {qualifier}variable '{vname}' "
                f"declared in an enclosing scope",
                name_tok
            )

    # ──────────────────────────────────────────────────────────
    # TAC UTILITIES
    # ──────────────────────────────────────────────────────────

    def _new_temp(self) -> str:
        self._temp_count += 1
        return f'_t{self._temp_count}'

    def _new_label(self) -> str:
        self._label_count += 1
        return f'L{self._label_count}'

    def _emit(self, op: str, arg1: str = '_', arg2: str = '_',
              result: str = '_') -> int:
        """Emit one quadruple and return its index."""
        self.quadruples.append(Quadruple(op, arg1, arg2, result))
        return len(self.quadruples) - 1

    def _emit_label(self, label: str) -> None:
        self._emit('label', label)

    def _backpatch(self, indices: List[int], label: str) -> None:
        """Fill in a label for a list of quadruple indices (backpatching)."""
        for i in indices:
            if 0 <= i < len(self.quadruples):
                self.quadruples[i].result = label

    # ──────────────────────────────────────────────────────────
    # PASS 1 — FORWARD DECLARATION COLLECTION
    # ──────────────────────────────────────────────────────────

    def _pass1(self) -> None:
        """
        Linear scan to collect into the global scope:
          • Group type definitions  (group Name { members })
          • worldwide variable declarations
          • Function signatures     (define ReturnType name ( params ))
        """
        toks = self.tokens
        n = len(toks)
        i = 0

        while i < n:
            t = toks[i]

            # ── Group definition ──────────────────────────────
            if t.type == 'group':
                if i + 1 < n and toks[i + 1].type == 'identifier':
                    group_name = toks[i + 1].value
                    ln, col = self._token_location(toks[i + 1])
                    members: Dict[str, str] = {}
                    j = i + 2
                    if j < n and toks[j].type == '{':
                        j += 1
                        while j < n and toks[j].type != '}':
                            if (toks[j].type in PRIMITIVE_TYPES
                                    and j + 1 < n
                                    and toks[j + 1].type == 'identifier'):
                                mtype = toks[j].type
                                mname = toks[j + 1].value
                                members[mname] = mtype
                                j += 2
                                if j < n and toks[j].type == ';':
                                    j += 1
                            else:
                                j += 1
                    sym = Symbol(
                        name=group_name, kind='group', data_type=group_name,
                        group_members=members, line=ln, col=col
                    )
                    if not self.symbol_table.declare(sym):
                        self._error(
                            f"Duplicate group definition '{group_name}'",
                            toks[i + 1]
                        )
                i += 1
                continue

            # ── worldwide declaration ─────────────────────────
            if t.type == 'worldwide':
                j = i + 1
                is_fixed = False
                if j < n and toks[j].type == 'fixed':
                    is_fixed = True
                    j += 1
                if j < n and toks[j].type in PRIMITIVE_TYPES:
                    dtype = toks[j].type
                    j += 1
                    if j < n and toks[j].type == 'identifier':
                        vname = toks[j].value
                        ln, col = self._token_location(toks[j])
                        sym = Symbol(
                            name=vname, kind='variable', data_type=dtype,
                            is_fixed=is_fixed, is_worldwide=True,
                            line=ln, col=col
                        )
                        if not self.symbol_table.declare(sym):
                            self._error(
                                f"Duplicate worldwide variable '{vname}'",
                                toks[j]
                            )
                i += 1
                continue

            # ── Function definition ───────────────────────────
            if t.type == 'define':
                j = i + 1
                if j < n and toks[j].type in RETURN_TYPES:
                    rtype = toks[j].type
                    j += 1
                    if j < n and toks[j].type == 'identifier':
                        fname = toks[j].value
                        ln, col = self._token_location(toks[j])
                        j += 1
                        params: List[Tuple[str, str]] = []
                        if j < n and toks[j].type == '(':
                            j += 1
                            while j < n and toks[j].type != ')':
                                if (toks[j].type in PRIMITIVE_TYPES
                                        and j + 1 < n
                                        and toks[j + 1].type == 'identifier'):
                                    params.append(
                                        (toks[j].type, toks[j + 1].value)
                                    )
                                    j += 2
                                    if j < n and toks[j].type == ',':
                                        j += 1
                                else:
                                    j += 1
                        sym = Symbol(
                            name=fname, kind='function', data_type=rtype,
                            return_type=rtype, params=params,
                            line=ln, col=col
                        )
                        if not self.symbol_table.declare(sym):
                            self._error(
                                f"Duplicate function definition '{fname}'",
                                toks[i + 2]
                            )
            i += 1

    # ──────────────────────────────────────────────────────────
    # PASS 2 — RECURSIVE DESCENT + TAC EMISSION
    # ──────────────────────────────────────────────────────────

    def _pass2(self) -> None:
        self._program()

    # ── Program structure ─────────────────────────────────────

    def _program(self) -> None:
        # <program> → <group_part>
        self._group_part()

    def _group_part(self) -> None:
        # <group_part> → <group_definitions> <group_part> | <worldwide_part>
        while self._match('group'):
            self._group_definitions()
        self._worldwide_part()

    def _group_definitions(self) -> None:
        # group identifier { <group_body> }
        self._consume('group')
        name_tok = self.current
        self._consume('identifier')
        self._consume('{')
        group_name = name_tok.value if name_tok else ''
        self._group_body(group_name)
        self._consume('}')

    def _group_body(self, group_name: str) -> None:
        # <group_body> → <group_member> <group_body_tail> | λ
        while self._match(*PRIMITIVE_TYPES):
            self._group_member()

    def _group_member(self) -> None:
        # <datatype> identifier ;
        self._datatype()
        self._consume('identifier')
        self._consume(';')
        # Members already registered in Pass 1; no extra action needed here.

    def _datatype(self) -> str:
        t = self._current_type()
        if t in PRIMITIVE_TYPES:
            self._advance()
            return t
        self._error(f"Expected a data type, got '{t}'")
        self._advance()
        return 'unknown'

    def _worldwide_part(self) -> None:
        # <worldwide_part> → <global_variable_declarations> <worldwide_part>
        #                  | <define_part>
        while self._match('worldwide'):
            self._global_variable_declarations()
        self._define_part()

    def _global_variable_declarations(self) -> None:
        # worldwide [fixed] <type> identifier = <stmt_value> ;
        self._consume('worldwide')
        is_fixed = False
        if self._match('fixed'):
            is_fixed = True
            self._advance()
        dtype = self._datatype()
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        self._consume('identifier')
        self._consume('=')
        place, expr_type = self._stmt_value()
        self._consume(';')

        sym = self.symbol_table.lookup(vname)
        if sym:
            # Semantic Rule II-1: type compatibility
            if not type_compatible(dtype, expr_type):
                self._error(
                    f"Type mismatch: cannot assign '{expr_type}' to "
                    f"'{dtype}' worldwide variable '{vname}'",
                    name_tok
                )
            self._emit('=', place, '_', vname)

    def _define_part(self) -> None:
        # <define_part> → <function_definitions> <define_part> | <start_block>
        while self._match('define'):
            self._function_definitions()
        self._start_block()

    def _start_block(self) -> None:
        # start { <statements> } finish
        self._consume('start')
        self._emit_label('start')
        self._consume('{')
        self.symbol_table.enter_scope()
        self._statements()
        self.symbol_table.exit_scope()
        self._consume('}')
        self._consume('finish')
        self._emit('halt')

    # ── Function definitions ──────────────────────────────────

    def _function_definitions(self) -> None:
        # define <return_type> identifier ( <parameter_list> ) { <local_declarations> <statements> <optional_return> }
        self._consume('define')
        rtype = self._return_type()
        name_tok = self.current
        fname = name_tok.value if name_tok else ''
        self._consume('identifier')
        self._consume('(')
        params = self._parameter_list()
        self._consume(')')
        self._consume('{')

        self._emit('func_begin', fname)

        func_sym = self.symbol_table.lookup(fname)

        # Enter function scope
        self.symbol_table.enter_scope()
        prev_function = self.current_function
        prev_has_return = self._has_return
        self.current_function = func_sym
        self._has_return = False

        # Declare parameters in function scope
        for ptype, pname in params:
            p_sym = Symbol(name=pname, kind='parameter', data_type=ptype)
            self._check_name_conflicts(pname, name_tok, label='Parameter')
            if not self.symbol_table.declare(p_sym):
                self._error(
                    f"Duplicate parameter name '{pname}' in '{fname}'",
                    name_tok
                )
            self._emit('param_receive', pname, ptype)

        self._local_declarations()
        self._statements()
        self._optional_return(rtype, name_tok)

        # Semantic Rule IV-5,7: non-empty function must have a return
        if rtype != 'empty' and not self._has_return:
            self._error(
                f"Function '{fname}' has return type '{rtype}' "
                f"but contains no 'give <value>' statement",
                name_tok
            )

        self.current_function = prev_function
        self._has_return = prev_has_return
        self.symbol_table.exit_scope()

        self._consume('}')
        self._emit('func_end', fname)

    def _return_type(self) -> str:
        t = self._current_type()
        if t in RETURN_TYPES:
            self._advance()
            return t
        self._error(f"Expected a return type, got '{t}'")
        self._advance()
        return 'empty'

    def _parameter_list(self) -> List[Tuple[str, str]]:
        # <parameter_list> → <parameter> <parameter_list_tail> | λ
        params: List[Tuple[str, str]] = []
        if self._match(*PRIMITIVE_TYPES):
            dtype, name = self._parameter()
            params.append((dtype, name))
            while self._match(','):
                self._advance()
                dtype, name = self._parameter()
                params.append((dtype, name))
        return params

    def _parameter(self) -> Tuple[str, str]:
        dtype = self._datatype()
        name_tok = self.current
        name = name_tok.value if name_tok else ''
        self._consume('identifier')
        return dtype, name

    def _optional_return(self, func_rtype: str, name_tok=None) -> None:
        # <optional_return> → give <return_tail> | λ
        if not self._match('give'):
            return

        self._consume('give')

        if self._match(';'):
            # give;  — early exit with no value
            self._consume(';')
            # Semantic Rule IV-4,6
            if func_rtype != 'empty':
                self._error(
                    f"Function with return type '{func_rtype}' must "
                    f"return a value; use 'give <expr>;' not 'give;'",
                    name_tok
                )
            else:
                self._emit('return')
            self._has_return = True
        else:
            # give <stmt_value>;
            place, expr_type = self._stmt_value()
            self._consume(';')
            # Semantic Rule IV-4
            if func_rtype == 'empty':
                self._error(
                    "Function with 'empty' return type cannot return a value",
                    name_tok
                )
            elif not type_compatible(func_rtype, expr_type):
                # Semantic Rule IV-8
                self._error(
                    f"Return type mismatch: function '{func_rtype}' "
                    f"but 'give' expression has type '{expr_type}'",
                    name_tok
                )
            self._emit('return', place)
            self._has_return = True

    # ── Local declarations ────────────────────────────────────

    def _local_declarations(self) -> None:
        # <local_declarations> → <declaration> <local_declarations> | λ
        # Consume declarations at the top of a function body.
        while True:
            t = self._current_type()
            if t in PRIMITIVE_TYPES or t in ('fixed', 'list'):
                self._declaration()
            elif t == 'identifier':
                # identifier identifier → group-typed declaration
                # identifier (         → function call (statement)
                # identifier = etc.    → assignment (statement)
                if self._peek_next_type() == 'identifier':
                    self._declaration()
                else:
                    break
            else:
                break

    def _declaration(self) -> None:
        t = self._current_type()
        if t == 'fixed':
            self._fixed_declaration()
        elif t == 'list':
            self._list_declaration()
        else:
            self._local_declaration()

    def _local_declaration(self) -> None:
        t = self._current_type()

        # Group-typed variable: GroupType varName ;
        if t == 'identifier':
            group_type_tok = self.current
            group_type = group_type_tok.value if group_type_tok else ''
            self._advance()
            name_tok = self.current
            vname = name_tok.value if name_tok else ''
            ln, col = self._token_location(name_tok)
            self._consume('identifier')
            self._consume(';')

            # Semantic Rule VII-3: group type must be declared
            group_sym = self.symbol_table.lookup(group_type)
            if group_sym is None or group_sym.kind != 'group':
                self._error(
                    f"Undefined group type '{group_type}'", group_type_tok
                )

            sym = Symbol(
                name=vname, kind='variable', data_type=group_type,
                line=ln, col=col
            )
            self._check_name_conflicts(vname, name_tok)
            # Semantic Rule I-2: no duplicate in same scope
            if not self.symbol_table.declare(sym):
                self._error(
                    f"Variable '{vname}' already declared in this scope",
                    name_tok
                )
            return

        # Primitive-typed variable: type identifier = expr ;
        dtype = self._datatype()
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        ln, col = self._token_location(name_tok)
        self._consume('identifier')
        self._consume('=')
        place, expr_type = self._stmt_value()
        self._consume(';')

        sym = Symbol(
            name=vname, kind='variable', data_type=dtype, line=ln, col=col
        )
        self._check_name_conflicts(vname, name_tok)
        # Semantic Rule I-2
        if not self.symbol_table.declare(sym):
            existing = self.symbol_table.lookup_current_scope(vname)
            if existing and existing.is_fixed:
                self._error(
                    f"Cannot redeclare fixed variable '{vname}'", name_tok
                )
            else:
                self._error(
                    f"Variable '{vname}' already declared in this scope",
                    name_tok
                )

        # Semantic Rule II-1
        if not type_compatible(dtype, expr_type):
            self._error(
                f"Type mismatch: cannot assign '{expr_type}' to "
                f"'{dtype}' variable '{vname}'",
                name_tok
            )

        self._emit('=', place, '_', vname)

    def _fixed_declaration(self) -> None:
        # fixed <type> identifier = expr ;
        self._consume('fixed')
        dtype = self._datatype()
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        ln, col = self._token_location(name_tok)
        self._consume('identifier')
        self._consume('=')
        place, expr_type = self._stmt_value()
        self._consume(';')

        sym = Symbol(
            name=vname, kind='variable', data_type=dtype,
            is_fixed=True, line=ln, col=col
        )
        self._check_name_conflicts(vname, name_tok, label='Fixed variable')
        # Semantic Rule III-1: fixed must be initialized (grammar ensures it)
        if not self.symbol_table.declare(sym):
            existing = self.symbol_table.lookup_current_scope(vname)
            if existing and existing.is_fixed:
                self._error(
                    f"Cannot redeclare fixed variable '{vname}'", name_tok
                )
            else:
                self._error(
                    f"Variable '{vname}' already declared in this scope",
                    name_tok
                )

        if not type_compatible(dtype, expr_type):
            self._error(
                f"Type mismatch: cannot assign '{expr_type}' to "
                f"fixed '{dtype}' variable '{vname}'",
                name_tok
            )

        self._emit('=', place, '_', vname)

    def _list_declaration(self) -> None:
        # list <type> identifier = <val_list> ;
        self._consume('list')
        dtype = self._datatype()
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        ln, col = self._token_location(name_tok)
        self._consume('identifier')
        self._consume('=')
        list_place, list_dim, _row_count = self._val_list(dtype)
        self._consume(';')

        sym = Symbol(
            name=vname, kind='list', data_type=dtype,
            is_list=True, list_dim=list_dim, line=ln, col=col
        )
        self._check_name_conflicts(vname, name_tok)
        if not self.symbol_table.declare(sym):
            self._error(
                f"Variable '{vname}' already declared in this scope",
                name_tok
            )

        self._emit('list_assign', list_place, str(list_dim), vname)

    # ── List value parsing ────────────────────────────────────

    def _val_list(self, expected_type: str) -> Tuple[str, int, int]:
        """
        Parse a list literal.  Returns (place, dimension, row_count).
        Uses 2-token lookahead to distinguish 1D vs 2D:
          [ [  →  2D
          [ x  →  1D
        """
        if not self._match('['):
            self._error("Expected '[' to begin list literal")
            return '_', 1, 0

        if self._peek_next_type() == '[':
            return self._val_list_2d(expected_type)

        # 1D
        elems = self._val_list_1d(expected_type)
        temp = self._new_temp()
        self._emit('list_1d', str(len(elems)), '_', temp)
        return temp, 1, len(elems)

    def _val_list_1d(self, expected_type: str) -> List[str]:
        """Parse a 1D list literal [ elem, ... ] and return element places."""
        self._consume('[')
        elems: List[str] = []
        if not self._match(']'):
            place, etype = self._arg_value()
            self._check_list_elem_type(expected_type, etype, len(elems))
            elems.append(place)
            self._emit('list_elem', place, str(len(elems) - 1))
            while self._match(','):
                self._advance()
                place, etype = self._arg_value()
                self._check_list_elem_type(expected_type, etype, len(elems))
                elems.append(place)
                self._emit('list_elem', place, str(len(elems) - 1))
        self._consume(']')
        return elems

    def _val_list_2d(self, expected_type: str) -> Tuple[str, int, int]:
        """Parse a 2D list literal [ [row], [row], ... ]."""
        self._consume('[')
        rows: List[List[str]] = []
        col_count = -1

        if not self._match(']'):
            row = self._val_list_1d(expected_type)
            rows.append(row)
            col_count = len(row)
            while self._match(','):
                self._advance()
                row = self._val_list_1d(expected_type)
                rows.append(row)
                # Semantic Rule V-2: all rows must have the same column count
                if len(row) != col_count:
                    self._error(
                        f"2D list row {len(rows)} has {len(row)} element(s), "
                        f"expected {col_count} (from the first row)"
                    )

        self._consume(']')
        temp = self._new_temp()
        self._emit(
            'list_2d', str(len(rows)),
            str(col_count if col_count >= 0 else 0), temp
        )
        return temp, 2, len(rows)

    def _check_list_elem_type(
        self, expected: str, got: str, idx: int
    ) -> None:
        # Semantic Rules V-1, V-3
        if not type_compatible(expected, got):
            self._error(
                f"List element [{idx}]: expected '{expected}', got '{got}'"
            )

    # ── Statements ────────────────────────────────────────────

    def _statements(self) -> None:
        # <statements> → <statement> <statements> | λ
        while self._match(*STMT_STARTERS):
            self._statement()

    def _option_statements(self) -> None:
        # Inside option blocks: stop/skip terminate the statement list
        while self._match(*STMT_STARTERS):
            self._statement()

    def _statement(self) -> None:
        t = self._current_type()

        if t in ('check', 'select', 'each', 'during'):
            self._control_statement()
        elif t in ('show', 'read'):
            self._io_statement()
        elif t in ('fixed', 'list', *PRIMITIVE_TYPES):
            self._declaration()
        elif t == 'identifier':
            next_t = self._peek_next_type()
            if next_t in ('=', '+=', '-=', '*=', '/=', '%=', '**=',
                          '++', '--', '[', '.'):
                self._assignment_statement()
            elif next_t == '(':
                self._function_call_as_statement()
            elif next_t == 'identifier':
                self._declaration()    # group-typed variable declaration
            else:
                self._error(
                    f"Unexpected '{next_t}' after identifier in statement"
                )
                self._advance()
        else:
            self._error(f"Unexpected token '{t}' in statement position")
            self._advance()

    # ── Assignment statement ──────────────────────────────────

    def _assignment_statement(self) -> None:
        target, target_type, target_sym = self._assignable()
        self._assignment_tail(target, target_type, target_sym)

    def _assignable(self) -> Tuple[str, str, Optional[Symbol]]:
        """Return (place, type, symbol) for the left-hand side."""
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        self._consume('identifier')

        sym = self.symbol_table.lookup(vname)
        # Semantic Rule I-1: must be declared
        if sym is None:
            self._error(f"Undeclared variable '{vname}'", name_tok)
            return vname, 'unknown', None

        # List index access
        if self._match('['):
            self._consume('[')
            idx_place, idx_type = self._index_value()
            self._consume(']')
            if not is_valid_index_type(idx_type):
                self._error(
                    f"List index must be integer (num) or bool, "
                    f"got '{idx_type}'"
                )
            if self._match('['):
                self._consume('[')
                idx2_place, idx2_type = self._index_value()
                self._consume(']')
                if not is_valid_index_type(idx2_type):
                    self._error(
                        f"List index must be integer (num) or bool, "
                        f"got '{idx2_type}'"
                    )
                return f'{vname}[{idx_place}][{idx2_place}]', sym.data_type, sym
            return f'{vname}[{idx_place}]', sym.data_type, sym

        # Group member access
        if self._match('.'):
            self._consume('.')
            member_tok = self.current
            mname = member_tok.value if member_tok else ''
            self._consume('identifier')
            # Semantic Rule VII-1,2
            group_sym = self.symbol_table.lookup(sym.data_type)
            if group_sym is None or group_sym.kind != 'group':
                self._error(
                    f"'{vname}' is not a group instance", name_tok
                )
                return f'{vname}.{mname}', 'unknown', None
            if mname not in group_sym.group_members:
                self._error(
                    f"Group '{sym.data_type}' has no member '{mname}'",
                    member_tok
                )
                return f'{vname}.{mname}', 'unknown', None
            return f'{vname}.{mname}', group_sym.group_members[mname], sym

        return vname, sym.data_type, sym

    def _assignment_tail(
        self,
        target: str,
        target_type: str,
        target_sym: Optional[Symbol]
    ) -> None:
        # Semantic Rule III-2: cannot reassign a fixed variable
        if target_sym and target_sym.is_fixed:
            self._error(f"Cannot reassign fixed variable '{target}'")

        t = self._current_type()

        if t == '=':
            self._advance()
            place, expr_type = self._stmt_value()
            self._consume(';')
            if not type_compatible(target_type, expr_type):
                self._error(
                    f"Type mismatch: cannot assign '{expr_type}' "
                    f"to '{target_type}' variable '{target}'"
                )
            self._emit('=', place, '_', target)

        elif t in COMPOUND_ASSIGN:
            op = t
            self._advance()
            place, expr_type = self._stmt_value()
            self._consume(';')
            if target_type not in NUMERIC_OR_BOOL and target_type != 'unknown':
                self._error(
                    f"Operator '{op}' requires a numeric or bool operand, "
                    f"got '{target_type}'"
                )
            base_op = op[:-1]   # strip trailing '='
            temp = self._new_temp()
            self._emit(base_op, target, place, temp)
            self._emit('=', temp, '_', target)

        elif t == '++':
            self._advance()
            self._consume(';')
            if target_type not in NUMERIC_OR_BOOL and target_type != 'unknown':
                self._error(
                    f"Operator '++' requires a numeric or bool operand, "
                    f"got '{target_type}'"
                )
            temp = self._new_temp()
            self._emit('+', target, '1', temp)
            self._emit('=', temp, '_', target)

        elif t == '--':
            self._advance()
            self._consume(';')
            if target_type not in NUMERIC_OR_BOOL and target_type != 'unknown':
                self._error(
                    f"Operator '--' requires a numeric or bool operand, "
                    f"got '{target_type}'"
                )
            temp = self._new_temp()
            self._emit('-', target, '1', temp)
            self._emit('=', temp, '_', target)

        else:
            self._error(f"Expected assignment operator, got '{t}'")

    # ── Function call as statement ────────────────────────────

    def _function_call_as_statement(self) -> None:
        self._expr_id()   # handles identifier ( arg_list ) → emits call
        self._consume(';')

    # ── I/O statements ────────────────────────────────────────

    def _io_statement(self) -> None:
        if self._match('show'):
            self._consume('show')
            self._consume('(')
            args = self._arg_list()
            self._consume(')')
            self._consume(';')
            for arg_place, _ in args:
                self._emit('param', arg_place)
            self._emit('call', 'show', str(len(args)))

        elif self._match('read'):
            self._consume('read')
            self._consume('(')
            name_tok = self.current
            vname = name_tok.value if name_tok else ''
            self._consume('identifier')
            self._consume(')')
            self._consume(';')
            sym = self.symbol_table.lookup(vname)
            # Semantic Rule I-1
            if sym is None:
                self._error(f"Undeclared variable '{vname}'", name_tok)
            elif sym.is_fixed:
                self._error(
                    f"Cannot read into fixed variable '{vname}'", name_tok
                )
            self._emit('read', vname)

    # ── Control statements ────────────────────────────────────

    def _control_statement(self) -> None:
        t = self._current_type()
        if t == 'check':
            self._check_structure()
        elif t == 'select':
            self._select_statement()
        elif t == 'each':
            self._each_loop()
        elif t == 'during':
            self._during_loop()

    def _check_structure(self) -> None:
        # check ( <cond_value> ) { <statements> } <otherwise_chain>
        self._consume('check')
        self._consume('(')
        cond_place, cond_type = self._cond_value()
        self._consume(')')

        if not is_numeric_or_bool(cond_type) and cond_type != 'unknown':
            self._error(
                f"Condition must be boolean or numeric (truthy), "
                f"got '{cond_type}'"
            )

        L_else = self._new_label()
        L_end  = self._new_label()

        self._emit('if_false', cond_place, '_', L_else)

        self._consume('{')
        self.symbol_table.enter_scope()
        self._statements()
        self.symbol_table.exit_scope()
        self._consume('}')

        self._emit('goto', '_', '_', L_end)
        self._emit_label(L_else)

        self._otherwise_chain(L_end)

        self._emit_label(L_end)

    def _otherwise_chain(self, L_end: str) -> None:
        if self._match('otherwisecheck'):
            self._consume('otherwisecheck')
            self._consume('(')
            cond_place, cond_type = self._cond_value()
            self._consume(')')

            if not is_numeric_or_bool(cond_type) and cond_type != 'unknown':
                self._error(
                    f"Condition must be boolean or numeric, got '{cond_type}'"
                )

            L_else = self._new_label()
            self._emit('if_false', cond_place, '_', L_else)

            self._consume('{')
            self.symbol_table.enter_scope()
            self._statements()
            self.symbol_table.exit_scope()
            self._consume('}')

            self._emit('goto', '_', '_', L_end)
            self._emit_label(L_else)
            self._otherwise_chain(L_end)

        elif self._match('otherwise'):
            self._consume('otherwise')
            self._consume('{')
            self.symbol_table.enter_scope()
            self._statements()
            self.symbol_table.exit_scope()
            self._consume('}')

    def _select_statement(self) -> None:
        # select ( identifier ) { <option_blocks> <optional_fallback> }
        self._consume('select')
        self._consume('(')
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        self._consume('identifier')
        self._consume(')')
        self._consume('{')

        sym = self.symbol_table.lookup(vname)
        if sym is None:
            self._error(f"Undeclared variable '{vname}'", name_tok)

        L_end = self._new_label()
        self._option_blocks(vname, L_end)
        self._optional_fallback(L_end)

        self._consume('}')
        self._emit_label(L_end)

    def _option_blocks(self, select_var: str, L_end: str) -> None:
        # <option_blocks> → <option_block> <option_blocks> | λ
        while self._match('option'):
            self._option_block(select_var, L_end)

    def _option_block(self, select_var: str, L_end: str) -> None:
        # option <literal> : <option_statements> <control_flow> ;
        self._consume('option')
        lit_place, _lit_type = self._literal()
        self._consume(':')

        L_next = self._new_label()
        temp = self._new_temp()
        # Emit: if select_var != lit_value, jump to next option
        self._emit('==', select_var, lit_place, temp)
        self._emit('if_false', temp, '_', L_next)

        self.symbol_table.enter_scope()
        self._option_statements()
        self.symbol_table.exit_scope()

        cf = self._control_flow()
        self._consume(';')

        if cf == 'stop':
            self._emit('goto', '_', '_', L_end)
        # skip → fall-through (no goto emitted)

        self._emit_label(L_next)

    def _control_flow(self) -> str:
        t = self._current_type()
        if t == 'stop':
            self._advance()
            return 'stop'
        elif t == 'skip':
            self._advance()
            return 'skip'
        else:
            self._error(f"Expected 'stop' or 'skip', got '{t}'")
            return 'stop'

    def _optional_fallback(self, L_end: str) -> None:
        # <optional_fallback> → fallback: <statements> | λ
        if self._match('fallback'):
            self._consume('fallback')
            self._consume(':')
            self.symbol_table.enter_scope()
            self._statements()
            self.symbol_table.exit_scope()

    # ── Iterative statements ──────────────────────────────────

    def _each_loop(self) -> None:
        # each identifier from <from_primary> to <to_primary> [step <step_primary>] { <statements> }
        self._consume('each')
        var_tok = self.current
        vname = var_tok.value if var_tok else ''
        self._consume('identifier')

        # Semantic Rule VI-1
        sym = self.symbol_table.lookup(vname)
        if sym is None:
            self._error(
                f"Loop variable '{vname}' must be declared before the "
                f"each loop",
                var_tok
            )
        else:
            if sym.data_type not in ('num', 'unknown'):
                self._error(
                    f"Loop variable '{vname}' must be type num (integer), "
                    f"got '{sym.data_type}'",
                    var_tok
                )
            if sym.is_fixed:
                self._error(
                    f"Loop variable '{vname}' is fixed and cannot be modified",
                    var_tok
                )

        self._consume('from')
        from_place, from_type = self._from_primary()
        # Semantic Rule VIII-2: from/to/step must be num (integer) only
        if from_type not in ('num', 'unknown'):
            self._error(
                f"'from' value must be integer (num), got '{from_type}'"
            )

        self._consume('to')
        to_place, to_type = self._to_primary()
        if to_type not in ('num', 'unknown'):
            self._error(
                f"'to' value must be integer (num), got '{to_type}'"
            )

        # Optional step
        step_place = '1'
        step_is_negative = False
        if self._match('step'):
            self._consume('step')
            step_place, step_type = self._step_primary()
            if step_type not in ('num', 'unknown'):
                self._error(
                    f"'step' value must be integer (num), got '{step_type}'"
                )
            # Semantic Rule VI-3: negative step warning
            if step_place.startswith('-'):
                step_is_negative = True

        # TAC: initialise loop variable
        self._emit('=', from_place, '_', vname)

        L_test = self._new_label()
        L_end  = self._new_label()

        self._emit_label(L_test)

        # Loop condition
        temp_cond = self._new_temp()
        cond_op = '>=' if step_is_negative else '<='
        self._emit(cond_op, vname, to_place, temp_cond)
        self._emit('if_false', temp_cond, '_', L_end)

        self._consume('{')
        self.symbol_table.enter_scope()
        self._statements()
        self.symbol_table.exit_scope()
        self._consume('}')

        # Increment / decrement
        temp_inc = self._new_temp()
        self._emit('+', vname, step_place, temp_inc)
        self._emit('=', temp_inc, '_', vname)
        self._emit('goto', '_', '_', L_test)
        self._emit_label(L_end)

    def _during_loop(self) -> None:
        # during ( <cond_value> ) { <statements> }
        self._consume('during')
        self._consume('(')

        L_test = self._new_label()
        L_end  = self._new_label()
        self._emit_label(L_test)

        cond_place, cond_type = self._cond_value()
        self._consume(')')

        if not is_numeric_or_bool(cond_type) and cond_type != 'unknown':
            self._error(
                f"Loop condition must be boolean or numeric, got '{cond_type}'"
            )

        self._emit('if_false', cond_place, '_', L_end)

        self._consume('{')
        self.symbol_table.enter_scope()
        self._statements()
        self.symbol_table.exit_scope()
        self._consume('}')

        self._emit('goto', '_', '_', L_test)
        self._emit_label(L_end)

    # ──────────────────────────────────────────────────────────
    # EXPRESSION HIERARCHY (L-Attributed SDD)
    # Each method returns (place: str, dtype: str).
    # stmt_value, arg_value, and cond_value all share the same hierarchy.
    # ──────────────────────────────────────────────────────────

    def _stmt_value(self) -> Tuple[str, str]:
        return self._expr_or()

    def _arg_value(self) -> Tuple[str, str]:
        return self._expr_or()

    def _cond_value(self) -> Tuple[str, str]:
        return self._expr_or()

    # ── OR ────────────────────────────────────────────────────

    def _expr_or(self) -> Tuple[str, str]:
        left_place, left_type = self._expr_and()
        while self._match('||'):
            self._advance()
            right_place, right_type = self._expr_and()
            self._check_logical_operands('||', left_type, right_type)
            temp = self._new_temp()
            self._emit('||', left_place, right_place, temp)
            left_place, left_type = temp, 'bool'
        return left_place, left_type

    # ── AND ───────────────────────────────────────────────────

    def _expr_and(self) -> Tuple[str, str]:
        left_place, left_type = self._expr_eq()
        while self._match('&&'):
            self._advance()
            right_place, right_type = self._expr_eq()
            self._check_logical_operands('&&', left_type, right_type)
            temp = self._new_temp()
            self._emit('&&', left_place, right_place, temp)
            left_place, left_type = temp, 'bool'
        return left_place, left_type

    # ── Equality ──────────────────────────────────────────────

    def _expr_eq(self) -> Tuple[str, str]:
        left_place, left_type = self._expr_rel()
        while self._match('==', '!='):
            op = self._current_type()
            self._advance()
            right_place, right_type = self._expr_rel()
            # Semantic Rule II-6: equality allowed on any type
            # but both sides should be the same type or coercible
            if (left_type not in ('unknown',)
                    and right_type not in ('unknown',)
                    and left_type != right_type):
                if not (left_type in NUMERIC_OR_BOOL
                        and right_type in NUMERIC_OR_BOOL):
                    self._error(
                        f"Cannot compare '{left_type}' with "
                        f"'{right_type}' using '{op}'"
                    )
            temp = self._new_temp()
            self._emit(op, left_place, right_place, temp)
            left_place, left_type = temp, 'bool'
        return left_place, left_type

    # ── Relational ────────────────────────────────────────────

    def _expr_rel(self) -> Tuple[str, str]:
        left_place, left_type = self._expr_add()
        while self._match('>', '<', '>=', '<='):
            op = self._current_type()
            self._advance()
            right_place, right_type = self._expr_add()
            # Semantic Rule II-7: relational ops only on numeric/bool
            if not is_numeric_or_bool(left_type) and left_type != 'unknown':
                self._error(
                    f"Operator '{op}' not valid for type '{left_type}'"
                )
            if not is_numeric_or_bool(right_type) and right_type != 'unknown':
                self._error(
                    f"Operator '{op}' not valid for type '{right_type}'"
                )
            temp = self._new_temp()
            self._emit(op, left_place, right_place, temp)
            left_place, left_type = temp, 'bool'
        return left_place, left_type

    # ── Addition / Subtraction ────────────────────────────────

    def _expr_add(self) -> Tuple[str, str]:
        left_place, left_type = self._expr_mult()
        while self._match('+', '-'):
            op = self._current_type()
            self._advance()
            right_place, right_type = self._expr_mult()

            # Text only supports + (concatenation)
            if left_type == TEXT_TYPE or right_type == TEXT_TYPE:
                if op == '+':
                    temp = self._new_temp()
                    self._emit('+', left_place, right_place, temp)
                    left_place, left_type = temp, TEXT_TYPE
                else:
                    self._error(
                        f"Operator '{op}' is not valid on text values"
                    )
            # Semantic Rule II-4: no arithmetic on letter
            # (TEXT_TYPE is already handled above; only CHAR_TYPE reaches here)
            elif left_type == CHAR_TYPE or right_type == CHAR_TYPE:
                self._error(
                    f"Operator '{op}' is not valid on letter values"
                )
            else:
                temp = self._new_temp()
                rtype = result_type_of_op(op, left_type, right_type)
                self._emit(op, left_place, right_place, temp)
                left_place, left_type = temp, rtype
        return left_place, left_type

    # ── Multiplication / Division / Modulus ───────────────────

    def _expr_mult(self) -> Tuple[str, str]:
        left_place, left_type = self._expr_exp()
        while self._match('*', '/', '%'):
            op = self._current_type()
            self._advance()
            right_place, right_type = self._expr_exp()
            if left_type in (TEXT_TYPE, CHAR_TYPE) or right_type in (TEXT_TYPE, CHAR_TYPE):
                bad = left_type if left_type in (TEXT_TYPE, CHAR_TYPE) else right_type
                self._error(
                    f"Operator '{op}' is not valid on "
                    f"{'text' if bad == TEXT_TYPE else 'letter'} values"
                )
            temp = self._new_temp()
            rtype = result_type_of_op(op, left_type, right_type)
            self._emit(op, left_place, right_place, temp)
            left_place, left_type = temp, rtype
        return left_place, left_type

    # ── Exponentiation (right-associative) ───────────────────

    def _expr_exp(self) -> Tuple[str, str]:
        base_place, base_type = self._expr_unary()
        if self._match('**'):
            self._advance()
            exp_place, exp_type = self._expr_exp()   # right-recursive
            if not is_numeric_or_bool(base_type) and base_type != 'unknown':
                self._error(
                    f"Operator '**' not valid for type '{base_type}'"
                )
            temp = self._new_temp()
            rtype = result_type_of_op('**', base_type, exp_type)
            self._emit('**', base_place, exp_place, temp)
            return temp, rtype
        return base_place, base_type

    # ── Unary ─────────────────────────────────────────────────

    def _expr_unary(self) -> Tuple[str, str]:
        if self._match('-'):
            self._advance()
            place, dtype = self._expr_post()
            if not is_numeric_or_bool(dtype) and dtype != 'unknown':
                self._error(
                    f"Unary '-' not valid for type '{dtype}'"
                )
            temp = self._new_temp()
            self._emit('unary-', place, '_', temp)
            return temp, dtype

        if self._match('!'):
            self._advance()
            place, dtype = self._expr_post()
            if not is_numeric_or_bool(dtype) and dtype != 'unknown':
                self._error(
                    f"Operator '!' not valid for type '{dtype}'"
                )
            temp = self._new_temp()
            self._emit('!', place, '_', temp)
            return temp, 'bool'

        return self._expr_post()

    # ── Post / Primary ────────────────────────────────────────

    def _expr_post(self) -> Tuple[str, str]:
        return self._expr_prim()

    def _expr_prim(self) -> Tuple[str, str]:
        t = self._current_type()

        if t == '(':
            self._consume('(')
            place, dtype = self._expr_or()
            self._consume(')')
            return place, dtype

        if t in ('num_lit', 'decimal_lit', 'string_lit', 'char_lit',
                 'Yes', 'No'):
            return self._literal()

        if t == 'size':
            return self._size_call()

        if t == 'identifier':
            return self._expr_id()

        self._error(f"Expected an expression, got '{t}'")
        if self.current:
            self._advance()
        return '_', 'unknown'

    def _literal(self) -> Tuple[str, str]:
        t = self._current_type()
        val = self.current.value if self.current else ''
        self._advance()
        dtype = infer_literal_type(t, val)

        # Precision overflow check for decimal literals
        if t == 'decimal_lit' and '.' in str(val):
            frac_digits = len(str(val).split('.')[1])
            if frac_digits > 16:
                self._error(
                    f"Decimal literal '{val}' has {frac_digits} fractional "
                    f"digit(s); maximum precision is 16 (bigdecimal)"
                )

        if t == 'string_lit':
            place = f'"{val}"'
        elif t == 'char_lit':
            place = f"'{val}'"
        else:
            place = str(val)
        return place, dtype

    def _expr_id(self) -> Tuple[str, str]:
        """Handles: identifier | identifier(args) | identifier[i] | identifier.member"""
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        self._consume('identifier')

        # Function call as expression
        if self._match('('):
            self._consume('(')
            args = self._arg_list()
            self._consume(')')
            return self._emit_call(vname, args, name_tok)

        # List index access
        if self._match('['):
            self._consume('[')
            idx_place, idx_type = self._index_value()
            self._consume(']')
            if not is_valid_index_type(idx_type):
                self._error(
                    f"List index must be integer (num) or bool, "
                    f"got '{idx_type}'"
                )

            sym = self.symbol_table.lookup(vname)
            if sym is None:
                self._error(f"Undeclared variable '{vname}'", name_tok)
                return '_', 'unknown'
            # Semantic Rule V-5: must be a list
            if not sym.is_list:
                self._error(f"'{vname}' is not a list", name_tok)

            if self._match('['):
                self._consume('[')
                idx2_place, idx2_type = self._index_value()
                self._consume(']')
                if not is_valid_index_type(idx2_type):
                    self._error(
                        f"List index must be integer (num) or bool, "
                        f"got '{idx2_type}'"
                    )
                temp = self._new_temp()
                self._emit('list_access', vname, f'{idx_place},{idx2_place}', temp)
                return temp, sym.data_type

            temp = self._new_temp()
            self._emit('list_access', vname, idx_place, temp)
            return temp, sym.data_type

        # Group member access
        if self._match('.'):
            self._consume('.')
            member_tok = self.current
            mname = member_tok.value if member_tok else ''
            self._consume('identifier')

            sym = self.symbol_table.lookup(vname)
            if sym is None:
                self._error(f"Undeclared variable '{vname}'", name_tok)
                return '_', 'unknown'

            # Semantic Rule VII-1,2
            group_sym = self.symbol_table.lookup(sym.data_type)
            if group_sym is None or group_sym.kind != 'group':
                self._error(
                    f"'{vname}' is not a group instance", name_tok
                )
                return '_', 'unknown'
            if mname not in group_sym.group_members:
                self._error(
                    f"Group '{sym.data_type}' has no member '{mname}'",
                    member_tok
                )
                return '_', 'unknown'

            temp = self._new_temp()
            self._emit('member_access', vname, mname, temp)
            return temp, group_sym.group_members[mname]

        # Plain variable read
        sym = self.symbol_table.lookup(vname)
        # Semantic Rule I-1: must be declared before use
        if sym is None:
            self._error(f"Undeclared variable '{vname}'", name_tok)
            return vname, 'unknown'
        return vname, sym.data_type

    # ── Function call helper ──────────────────────────────────

    def _emit_call(
        self, fname: str, args: List[Tuple[str, str]], name_tok=None
    ) -> Tuple[str, str]:
        """Validate and emit a function call. Returns (place, return_type)."""
        func_sym = self.symbol_table.lookup(fname)

        # Semantic Rule IV-1: function must be declared
        if func_sym is None:
            self._error(f"Undeclared function '{fname}'", name_tok)
            return '_', 'unknown'
        if func_sym.kind != 'function':
            self._error(f"'{fname}' is not a function", name_tok)
            return '_', 'unknown'

        # Semantic Rule IV-2: argument count must match
        if len(args) != len(func_sym.params):
            self._error(
                f"Function '{fname}' expects {len(func_sym.params)} "
                f"argument(s), got {len(args)}",
                name_tok
            )
        else:
            # Semantic Rule IV-3: argument types must match
            for i, ((arg_place, arg_type), (param_type, param_name)) in \
                    enumerate(zip(args, func_sym.params)):
                if not type_compatible(param_type, arg_type):
                    self._error(
                        f"Argument {i + 1} of '{fname}': expected "
                        f"'{param_type}', got '{arg_type}'",
                        name_tok
                    )

        for arg_place, _ in args:
            self._emit('param', arg_place)

        rtype = func_sym.return_type

        if rtype != 'empty':
            temp = self._new_temp()
            self._emit('call', fname, str(len(args)), temp)
            return temp, rtype

        self._emit('call', fname, str(len(args)))
        return '_', 'empty'

    def _arg_list(self) -> List[Tuple[str, str]]:
        """Parse comma-separated argument list. Returns [(place, type), ...]."""
        args: List[Tuple[str, str]] = []
        if self._match(*EXPR_STARTERS):
            place, dtype = self._arg_value()
            args.append((place, dtype))
            while self._match(','):
                self._advance()
                place, dtype = self._arg_value()
                args.append((place, dtype))
        return args

    # ── size() built-in ───────────────────────────────────────

    def _size_call(self) -> Tuple[str, str]:
        self._consume('size')
        self._consume('(')
        name_tok = self.current
        vname = name_tok.value if name_tok else ''
        self._consume('identifier')

        sym = self.symbol_table.lookup(vname)
        # Semantic Rule V-5
        if sym is None:
            self._error(f"Undeclared variable '{vname}'", name_tok)
        elif not sym.is_list:
            self._error(
                f"size() can only be called on a list; "
                f"'{vname}' is not a list",
                name_tok
            )

        dim_arg = '_'
        if self._match(','):
            self._advance()
            dim_tok = self.current
            dim_arg = dim_tok.value if dim_tok else '0'
            self._consume('num_lit')

        self._consume(')')
        temp = self._new_temp()
        self._emit('size', vname, dim_arg, temp)
        return temp, 'num'

    # ── Index expression (numeric sub-language) ───────────────

    def _index_value(self) -> Tuple[str, str]:
        return self._index_add()

    def _index_add(self) -> Tuple[str, str]:
        left, ltype = self._index_mult()
        while self._match('+', '-'):
            op = self._current_type()
            self._advance()
            right, rtype = self._index_mult()
            temp = self._new_temp()
            self._emit(op, left, right, temp)
            left, ltype = temp, 'num'
        return left, ltype

    def _index_mult(self) -> Tuple[str, str]:
        left, ltype = self._index_exp()
        while self._match('*', '/', '%'):
            op = self._current_type()
            self._advance()
            right, rtype = self._index_exp()
            temp = self._new_temp()
            self._emit(op, left, right, temp)
            left, ltype = temp, 'num'
        return left, ltype

    def _index_exp(self) -> Tuple[str, str]:
        base, btype = self._index_unary()
        if self._match('**'):
            self._advance()
            exp, etype = self._index_exp()
            temp = self._new_temp()
            self._emit('**', base, exp, temp)
            return temp, 'num'
        return base, btype

    def _index_unary(self) -> Tuple[str, str]:
        if self._match('-'):
            self._advance()
            place, dtype = self._index_prim()
            temp = self._new_temp()
            self._emit('unary-', place, '_', temp)
            return temp, 'num'
        return self._index_prim()

    def _index_prim(self) -> Tuple[str, str]:
        t = self._current_type()
        if t == '(':
            self._consume('(')
            place, dtype = self._index_value()
            self._consume(')')
            return place, dtype
        if t == 'num_lit':
            val = self.current.value
            self._advance()
            return str(val), 'num'
        if t == 'decimal_lit':
            val = self.current.value
            self._advance()
            self._error(
                f"List index must be integer (num) or bool, "
                f"got decimal literal '{val}'"
            )
            return str(val), 'decimal'
        if t == 'size':
            return self._size_call()
        if t == 'identifier':
            return self._expr_id()
        self._error(f"Expected index expression, got '{t}'")
        if self.current:
            self._advance()
        return '_', 'num'

    # ── Loop range primaries (numeric only) ───────────────────

    def _from_primary(self) -> Tuple[str, str]:
        return self._range_primary()

    def _to_primary(self) -> Tuple[str, str]:
        return self._range_primary()

    def _step_primary(self) -> Tuple[str, str]:
        return self._range_primary()

    def _range_primary(self) -> Tuple[str, str]:
        t = self._current_type()
        if t == 'num_lit':
            val = self.current.value
            self._advance()
            return str(val), 'num'
        if t == 'decimal_lit':
            val = self.current.value
            self._advance()
            return str(val), 'decimal'
        if t == 'size':
            return self._size_call()
        if t == 'identifier':
            return self._expr_id()
        self._error(f"Expected numeric value for loop range, got '{t}'")
        if self.current:
            self._advance()
        return '_', 'num'

    # ── Semantic check helpers ────────────────────────────────

    def _check_logical_operands(
        self, op: str, left: str, right: str
    ) -> None:
        if not is_numeric_or_bool(left) and left != 'unknown':
            self._error(
                f"Operator '{op}' not valid for type '{left}'"
            )
        if not is_numeric_or_bool(right) and right != 'unknown':
            self._error(
                f"Operator '{op}' not valid for type '{right}'"
            )

    # ──────────────────────────────────────────────────────────
    # OUTPUT / DISPLAY HELPERS
    # ──────────────────────────────────────────────────────────

    def print_quadruples(self) -> None:
        print("\n" + "=" * 60)
        print("THREE-ADDRESS CODE  (Quadruples)")
        print("=" * 60)
        print(f"{'#':<5} {'op':<14} {'arg1':<16} {'arg2':<16} {'result'}")
        print("-" * 60)
        for i, q in enumerate(self.quadruples):
            print(
                f"{i:<5} {q.op:<14} {q.arg1:<16} {q.arg2:<16} {q.result}"
            )

    def print_errors(self) -> None:
        print("\n" + "=" * 60)
        if self.errors:
            print(f"SEMANTIC ERRORS  ({len(self.errors)})")
            print("=" * 60)
            for e in self.errors:
                print(e)
        else:
            print("SEMANTIC ANALYSIS: No errors found.")
            print("=" * 60)

    def print_symbol_table(self) -> None:
        print("\n" + "=" * 60)
        print("GLOBAL SYMBOL TABLE")
        print("=" * 60)
        global_scope = self.symbol_table.scopes[0]
        for name, sym in global_scope.items():
            extra = ''
            if sym.kind == 'function':
                params = ', '.join(f"{t} {n}" for t, n in sym.params)
                extra = f"  params=({params})  returns={sym.return_type}"
            elif sym.kind == 'group':
                members = ', '.join(
                    f"{t} {n}" for n, t in sym.group_members.items()
                )
                extra = f"  members={{{members}}}"
            elif sym.is_list:
                extra = f"  dim={sym.list_dim}"
            fixed_tag = '  [fixed]' if sym.is_fixed else ''
            ww_tag = '  [worldwide]' if sym.is_worldwide else ''
            print(
                f"  {name:<20} {sym.kind:<12} {sym.data_type:<14}"
                f"{fixed_tag}{ww_tag}{extra}"
            )
