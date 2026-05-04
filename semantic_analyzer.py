
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

from ast_nodes import (
    ASTNode, Expr, Stmt,
    Program, GroupDef, GroupMember, WorldwideDecl, WorldwideListDecl, FuncDef, Parameter,
    VarDecl, FixedDecl, ListDecl,
    Assignment, CompoundAssign, Increment, Decrement,
    IfChain, ElifBranch, SelectStmt, OptionBlock,
    EachLoop, DuringLoop, FuncCallStmt, ReturnStmt, ShowStmt, DisplayStmt, ReadStmt,
    BinaryOp, UnaryOp, Literal, Identifier, FuncCall,
    ListAccess, MemberAccess, IndexedMemberAccess,
    SizeCall, TextLenCall, CharAtCall, OrdCall, ListLiteral1D, ListLiteral2D,
)


# TYPE-SYSTEM CONSTANTS


NUMERIC_TYPES = {'num', 'decimal', 'bigdecimal'}
BOOL_TYPE = 'bool'
TEXT_TYPE = 'text'
CHAR_TYPE = 'letter'
PRIMITIVE_TYPES = NUMERIC_TYPES | {BOOL_TYPE, TEXT_TYPE, CHAR_TYPE}
NUMERIC_OR_BOOL = NUMERIC_TYPES | {BOOL_TYPE}   # truthy-coercion domain
RETURN_TYPES = PRIMITIVE_TYPES | {'empty'}

ARITHMETIC_OPS = {'+', '-', '*', '/', '//', '%', '**'}
RELATIONAL_OPS = {'>', '<', '>=', '<='}
EQUALITY_OPS = {'==', '!='}
LOGICAL_OPS = {'&&', '||', '!'}
COMPOUND_ASSIGN = {'+=', '-=', '*=', '/=', '//=', '%=', '**='}


# DATA STRUCTURE


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
    # 'variable' | 'function' | 'group' | 'parameter' | 'list'
    kind: str
    data_type: str                     # primitive type name, group name, or return type
    is_fixed: bool = False
    is_worldwide: bool = False
    is_list: bool = False
    list_dim: int = 0                  # 1 or 2
    list_size: int = 0                 # element count for 1D; row count for 2D
    list_col_count: int = 0            # column count for 2D
    params: List[Tuple[str, str]] = field(
        default_factory=list)   # [(type, name), ...]
    return_type: str = ''
    group_members: Dict[str, str] = field(
        default_factory=dict)   # {member_name: type}
    used: bool = False
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
                scope[name].used = True
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


# TYPE HELPERS


def infer_literal_type(token_type: str, value: str = '') -> str:
    if token_type == 'decimal_lit':
        frac_digits = 0
        if '.' in str(value):
            frac_digits = len(str(value).split('.')[1])
        if frac_digits <= 11:
            return 'decimal'
        elif frac_digits <= 16:
            return 'bigdecimal'
        else:
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
    return dtype in ('num', 'bool', 'unknown')


_NUMERIC_RANK: dict = {'num': 0, 'decimal': 1, 'bigdecimal': 2}


def type_compatible(declared: str, expr: str) -> bool:
    if declared == 'unknown' or expr == 'unknown':
        return True
    if declared == expr:
        return True
    if expr == BOOL_TYPE and declared in NUMERIC_TYPES:
        return True
    if declared == BOOL_TYPE and expr in NUMERIC_TYPES:
        return True
    if declared in _NUMERIC_RANK and expr in _NUMERIC_RANK:
        return _NUMERIC_RANK[expr] <= _NUMERIC_RANK[declared]
    return False


def result_type_of_op(op: str, left: str, right: str) -> str:
    if op in ARITHMETIC_OPS:
        for wide in ('bigdecimal', 'decimal'):
            if left == wide or right == wide:
                return wide
        return 'num'
    if op in RELATIONAL_OPS | EQUALITY_OPS | LOGICAL_OPS:
        return 'bool'
    return 'unknown'


# AST VISITOR BASE


class ASTVisitor:
    def visit(self, node):
        if node is None:
            return None
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return None


# PASS 1 — DECLARATION COLLECTOR


class DeclarationCollector(ASTVisitor):
    """Walks Program top-level to collect groups, worldwide vars, and
    function signatures into the global scope."""

    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table
        self.errors: List[SemanticError] = []

    def _error(self, message: str, node: ASTNode = None) -> None:
        ln = node.line if node else 0
        col = node.col if node else 0
        self.errors.append(SemanticError(message, ln, col))

    def visit_Program(self, node: Program):
        for group in node.groups:
            self.visit(group)
        for ww in node.worldwide_decls:
            self.visit(ww)
        for func in node.functions:
            self._collect_function_signature(func)

    def visit_GroupDef(self, node: GroupDef):
        members: Dict[str, str] = {}
        for m in node.members:
            members[m.name] = m.datatype
        sym = Symbol(
            name=node.name, kind='group', data_type=node.name,
            group_members=members, line=node.line, col=node.col
        )
        if not self.symbol_table.declare(sym):
            self._error(f"Duplicate group definition '{node.name}'", node)

    def visit_WorldwideDecl(self, node: WorldwideDecl):
        sym = Symbol(
            name=node.name, kind='variable', data_type=node.datatype,
            is_fixed=node.is_fixed, is_worldwide=True,
            line=node.line, col=node.col
        )
        if not self.symbol_table.declare(sym):
            self._error(f"Duplicate worldwide variable '{node.name}'", node)

    def visit_WorldwideListDecl(self, node: WorldwideListDecl):
        if node.is_group_typed:
            group_sym = self.symbol_table.lookup(node.datatype)
            if group_sym is None or group_sym.kind != 'group':
                self._error(
                    f"Undefined group type '{node.datatype}'", node)
            sym = Symbol(
                name=node.name, kind='list', data_type=node.datatype,
                is_list=True, is_worldwide=True,
                list_dim=1, list_size=node.group_list_size, list_col_count=0,
                line=node.line, col=node.col
            )
            if not self.symbol_table.declare(sym):
                self._error(f"Duplicate worldwide list '{node.name}'", node)
            return

        # Determine dimensions from the value node shape
        list_dim = 1
        elem_count = 0
        col_count = 0
        if isinstance(node.value, ListLiteral2D):
            list_dim = 2
            elem_count = len(node.value.rows)
            col_count = len(
                node.value.rows[0].elements) if node.value.rows else 0
        elif isinstance(node.value, ListLiteral1D):
            elem_count = len(node.value.elements)

        sym = Symbol(
            name=node.name, kind='list', data_type=node.datatype,
            is_list=True, is_worldwide=True,
            list_dim=list_dim, list_size=elem_count, list_col_count=col_count,
            line=node.line, col=node.col
        )
        if not self.symbol_table.declare(sym):
            self._error(f"Duplicate worldwide list '{node.name}'", node)

    def _collect_function_signature(self, node: FuncDef):
        params = [(p.datatype, p.name) for p in node.params]
        sym = Symbol(
            name=node.name, kind='function', data_type=node.return_type,
            return_type=node.return_type, params=params,
            line=node.line, col=node.col
        )
        if not self.symbol_table.declare(sym):
            self._error(f"Duplicate function definition '{node.name}'", node)


# PASS 2 — SEMANTIC CHECKER + TAC EMITTER


class SemanticChecker(ASTVisitor):
    """Full tree walk: semantic checks + TAC emission."""

    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        self.quadruples: List[Quadruple] = []

        self._temp_count = 0
        self._label_count = 0

        self.current_function: Optional[Symbol] = None
        self._has_return: bool = False
        self._loop_depth: int = 0

    # ── Error / location helpers ──────────────────────────────

    def _error(self, message: str, node: ASTNode = None) -> None:
        ln = node.line if node else 0
        col = node.col if node else 0
        self.errors.append(SemanticError(message, ln, col))

    def _exit_scope_with_unused_check(self) -> None:
        """Check for unused variables in the current scope, then pop it."""
        current = self.symbol_table.scopes[-1]
        for name, sym in current.items():
            if sym.kind in ('variable', 'list') and not sym.used:
                self.warnings.append(
                    f"Warning: Variable '{name}' declared at line {sym.line} is never used"
                )
        self.symbol_table.exit_scope()

    def _check_name_conflicts(
        self, vname: str, node: ASTNode, label: str = 'Variable'
    ) -> None:
        global_sym = self.symbol_table.lookup_global(vname)
        if global_sym is not None and global_sym.is_worldwide:
            qualifier = 'fixed worldwide' if global_sym.is_fixed else 'worldwide'
            self._error(
                f"{label} '{vname}' conflicts with {qualifier} variable "
                f"'{vname}'; worldwide variables cannot be shadowed or redeclared",
                node
            )
            return
        outer_sym = self.symbol_table.lookup_in_enclosing_local(vname)
        if outer_sym is not None:
            qualifier = 'fixed ' if outer_sym.is_fixed else ''
            self._error(
                f"{label} '{vname}' shadows {qualifier}variable '{vname}' "
                f"declared in an enclosing scope",
                node
            )

    # ── TAC utilities ─────────────────────────────────────────

    def _new_temp(self) -> str:
        self._temp_count += 1
        return f'_t{self._temp_count}'

    def _new_label(self) -> str:
        self._label_count += 1
        return f'L{self._label_count}'

    def _emit(self, op: str, arg1: str = '_', arg2: str = '_',
              result: str = '_') -> int:
        self.quadruples.append(Quadruple(op, arg1, arg2, result))
        return len(self.quadruples) - 1

    def _emit_num_check(self, place: str, ctx: str) -> None:
        """Runtime overflow guard for num results."""
        self._emit('num_check', place, ctx, '_')

    def _emit_label(self, label: str) -> None:
        self._emit('label', label)

    def _backpatch(self, indices: List[int], label: str) -> None:
        for i in indices:
            if 0 <= i < len(self.quadruples):
                self.quadruples[i].result = label

    # ── Program structure visitors ────────────────────────────

    def visit_Program(self, node: Program):
        # Groups already collected in Pass 1; walk them for body-level checks
        for group in node.groups:
            self.visit(group)
        for ww in node.worldwide_decls:
            self.visit(ww)
        for func in node.functions:
            self.visit(func)
        # Start block
        self._emit_label('start')
        self.symbol_table.enter_scope()
        for stmt in node.start_body:
            self.visit(stmt)
        self._exit_scope_with_unused_check()
        self._emit('halt')

    def visit_GroupDef(self, node: GroupDef):
        # Members already registered in Pass 1; nothing else needed
        pass

    def visit_WorldwideDecl(self, node: WorldwideDecl):
        place, expr_type = self.visit(node.value)
        sym = self.symbol_table.lookup(node.name)
        if sym:
            if not type_compatible(node.datatype, expr_type):
                self._error(
                    f"Type mismatch: cannot assign '{expr_type}' to "
                    f"'{node.datatype}' worldwide variable '{node.name}'",
                    node
                )
            self._emit('=', place, '_', node.name)

    def visit_WorldwideListDecl(self, node: WorldwideListDecl):
        if node.is_group_typed:
            self._emit('group_list_create', node.datatype,
                       str(node.group_list_size), node.name)
            return
        # Reuse the same list-visiting logic as visit_ListDecl
        list_place, list_dim, elem_count, col_count = self._visit_val_list(
            node.value, node.datatype)
        # Symbol already registered by Pass 1 — just emit TAC
        self._emit('list_assign', list_place, str(list_dim), node.name)

    def visit_FuncDef(self, node: FuncDef):
        self._emit('func_begin', node.name)

        func_sym = self.symbol_table.lookup(node.name)

        self.symbol_table.enter_scope()
        prev_function = self.current_function
        prev_has_return = self._has_return
        self.current_function = func_sym
        self._has_return = False

        # Declare parameters in function scope
        for p in node.params:
            p_sym = Symbol(name=p.name, kind='parameter', data_type=p.datatype)
            self._check_name_conflicts(p.name, node, label='Parameter')
            if not self.symbol_table.declare(p_sym):
                self._error(
                    f"Duplicate parameter name '{p.name}' in '{node.name}'",
                    node
                )
            self._emit('param_receive', p.name, p.datatype)

        # Local declarations
        for decl in node.local_decls:
            self.visit(decl)

        # Body statements
        for stmt in node.body:
            self.visit(stmt)

        # Optional return
        if node.return_stmt is not None:
            self._visit_return_in_function(
                node.return_stmt, node.return_type, node)

        # Semantic Rule IV-5,7: non-empty function must have a return
        if node.return_type != 'empty' and not self._has_return:
            self._error(
                f"Function '{node.name}' has return type '{node.return_type}' "
                f"must return a value; use 'give <stmt_value>;'",
                node
            )

        self.current_function = prev_function
        self._has_return = prev_has_return
        self._exit_scope_with_unused_check()

        self._emit('func_end', node.name)

    def _visit_return_in_function(self, ret: ReturnStmt, func_rtype: str, func_node: ASTNode):
        if ret.value is None:
            # give;  — early exit with no value
            if func_rtype != 'empty':
                self._error(
                    f"Function with return type '{func_rtype}' must "
                    f"return a value; use 'give <stmt_value>;' not 'give;'",
                    func_node
                )
            else:
                self._emit('return')
            self._has_return = True
        else:
            place, expr_type = self.visit(ret.value)
            if func_rtype == 'empty':
                self._error(
                    "Function with 'empty' return type cannot return a value",
                    func_node
                )
            elif not type_compatible(func_rtype, expr_type):
                self._error(
                    f"Return type mismatch: function '{func_rtype}' "
                    f"but 'give' expression has type '{expr_type}'",
                    func_node
                )
            self._emit('return', place)
            self._has_return = True

    # ── Declaration visitors ──────────────────────────────────

    def visit_VarDecl(self, node: VarDecl):
        if self._loop_depth > 0:
            self._error(
                f"Variable '{node.name}' cannot be declared inside a loop body; "
                f"declare it before the loop",
                node
            )
            return

        if node.is_group_typed:
            # Group-typed variable: GroupType varName;
            group_sym = self.symbol_table.lookup(node.datatype)
            if group_sym is None or group_sym.kind != 'group':
                self._error(
                    f"Undefined group type '{node.datatype}'", node
                )
            sym = Symbol(
                name=node.name, kind='variable', data_type=node.datatype,
                line=node.line, col=node.col
            )
            self._check_name_conflicts(node.name, node)
            if not self.symbol_table.declare(sym):
                self._error(
                    f"Variable '{node.name}' already declared in this scope",
                    node
                )
            self._emit('=', f'{node.datatype}()', '_', node.name)
            return

        # Primitive-typed variable: type name = expr;
        place, expr_type = self.visit(node.value)
        sym = Symbol(
            name=node.name, kind='variable', data_type=node.datatype,
            line=node.line, col=node.col
        )
        self._check_name_conflicts(node.name, node)
        if not self.symbol_table.declare(sym):
            existing = self.symbol_table.lookup_current_scope(node.name)
            if existing and existing.is_fixed:
                self._error(
                    f"Cannot redeclare fixed variable '{node.name}'", node
                )
            else:
                self._error(
                    f"Variable '{node.name}' already declared in this scope",
                    node
                )

        if not type_compatible(node.datatype, expr_type):
            self._error(
                f"Type mismatch: cannot assign '{expr_type}' to "
                f"'{node.datatype}' variable '{node.name}'",
                node
            )

        self._emit('=', place, '_', node.name)
        if node.datatype == 'num':
            self._emit_num_check(node.name, 'assign')

    def visit_FixedDecl(self, node: FixedDecl):
        if self._loop_depth > 0:
            self._error(
                f"Fixed variable '{node.name}' cannot be declared inside a loop body; "
                f"declare it before the loop",
                node
            )
            return

        place, expr_type = self.visit(node.value)
        sym = Symbol(
            name=node.name, kind='variable', data_type=node.datatype,
            is_fixed=True, line=node.line, col=node.col
        )
        self._check_name_conflicts(node.name, node, label='Fixed variable')
        if not self.symbol_table.declare(sym):
            existing = self.symbol_table.lookup_current_scope(node.name)
            if existing and existing.is_fixed:
                self._error(
                    f"Cannot redeclare fixed variable '{node.name}'", node
                )
            else:
                self._error(
                    f"Variable '{node.name}' already declared in this scope",
                    node
                )

        if not type_compatible(node.datatype, expr_type):
            self._error(
                f"Type mismatch: cannot assign '{expr_type}' to "
                f"fixed '{node.datatype}' variable '{node.name}'",
                node
            )

        self._emit('=', place, '_', node.name)

    def visit_ListDecl(self, node: ListDecl):
        if self._loop_depth > 0:
            self._error(
                f"List '{node.name}' cannot be declared inside a loop body; "
                f"declare it before the loop",
                node
            )
            return

        list_place, list_dim, elem_count, col_count = self._visit_val_list(
            node.value, node.datatype)
        sym = Symbol(
            name=node.name, kind='list', data_type=node.datatype,
            is_list=True, list_dim=list_dim,
            list_size=elem_count, list_col_count=col_count,
            line=node.line, col=node.col
        )
        self._check_name_conflicts(node.name, node)
        if not self.symbol_table.declare(sym):
            self._error(
                f"Variable '{node.name}' already declared in this scope",
                node
            )
        self._emit('list_assign', list_place, str(list_dim), node.name)

    def _visit_val_list(self, val_list, expected_type: str) -> Tuple[str, int, int, int]:
        if isinstance(val_list, ListLiteral2D):
            return self._visit_list_2d(val_list, expected_type)
        elif isinstance(val_list, ListLiteral1D):
            elems = self._visit_list_1d(val_list, expected_type)
            temp = self._new_temp()
            self._emit('list_1d', str(len(elems)), '_', temp)
            return temp, 1, len(elems), 0
        return '_', 1, 0, 0

    def _visit_list_1d(self, node: ListLiteral1D, expected_type: str) -> List[str]:
        elems: List[str] = []
        for i, elem in enumerate(node.elements):
            place, etype = self.visit(elem)
            self._check_list_elem_type(expected_type, etype, i)
            elems.append(place)
            self._emit('list_elem', place, str(i))
        return elems

    def _visit_list_2d(self, node: ListLiteral2D, expected_type: str) -> Tuple[str, int, int, int]:
        rows: List[List[str]] = []
        col_count = -1
        for row_idx, row_node in enumerate(node.rows):
            row_elems = self._visit_list_1d(row_node, expected_type)
            rows.append(row_elems)
            if col_count < 0:
                col_count = len(row_elems)
            elif len(row_elems) != col_count:
                self._error(
                    f"2D list row {row_idx + 1} has {len(row_elems)} element(s), "
                    f"expected {col_count} (from the first row)"
                )
        actual_col_count = col_count if col_count >= 0 else 0
        temp = self._new_temp()
        self._emit(
            'list_2d', str(len(rows)),
            str(actual_col_count), temp
        )
        return temp, 2, len(rows), actual_col_count

    def _check_list_elem_type(self, expected: str, got: str, idx: int) -> None:
        if not type_compatible(expected, got):
            self._error(
                f"List element [{idx}]: expected '{expected}', got '{got}'"
            )

    # ── Statement visitors ────────────────────────────────────

    def visit_Assignment(self, node: Assignment):
        target, target_type, target_sym = self._resolve_assignable(node.target)

        if target_sym and target_sym.is_fixed:
            self._error(f"Cannot reassign fixed variable '{target}'", node)

        place, expr_type = self.visit(node.value)
        if not type_compatible(target_type, expr_type):
            self._error(
                f"Type mismatch: cannot assign '{expr_type}' "
                f"to '{target_type}' variable '{target}'",
                node
            )
        self._emit('=', place, '_', target)
        if target_type == 'num':
            self._emit_num_check(target, 'assign')

    def visit_CompoundAssign(self, node: CompoundAssign):
        target, target_type, target_sym = self._resolve_assignable(node.target)

        if target_sym and target_sym.is_fixed:
            self._error(f"Cannot reassign fixed variable '{target}'", node)

        place, expr_type = self.visit(node.value)
        if target_type not in NUMERIC_OR_BOOL and target_type != 'unknown':
            self._error(
                f"Operator '{node.op}' requires a numeric or bool operand, "
                f"got '{target_type}'",
                node
            )
        base_op = node.op[:-1]   # strip trailing '='
        temp = self._new_temp()
        self._emit(base_op, target, place, temp)
        if target_type == 'num' and base_op in ('+', '-', '*', '**'):
            self._emit_num_check(temp, node.op)
        self._emit('=', temp, '_', target)
        if target_type == 'num':
            self._emit_num_check(target, 'assign')

    def visit_Increment(self, node: Increment):
        target, target_type, target_sym = self._resolve_assignable(node.target)

        if target_sym and target_sym.is_fixed:
            self._error(f"Cannot reassign fixed variable '{target}'", node)

        if target_type not in NUMERIC_OR_BOOL and target_type != 'unknown':
            self._error(
                f"Operator '++' requires a numeric or bool operand, "
                f"got '{target_type}'",
                node
            )
        temp = self._new_temp()
        self._emit('+', target, '1', temp)
        self._emit('=', temp, '_', target)
        if target_type == 'num':
            self._emit_num_check(target, '++')

    def visit_Decrement(self, node: Decrement):
        target, target_type, target_sym = self._resolve_assignable(node.target)

        if target_sym and target_sym.is_fixed:
            self._error(f"Cannot reassign fixed variable '{target}'", node)

        if target_type not in NUMERIC_OR_BOOL and target_type != 'unknown':
            self._error(
                f"Operator '--' requires a numeric or bool operand, "
                f"got '{target_type}'",
                node
            )
        temp = self._new_temp()
        self._emit('-', target, '1', temp)
        self._emit('=', temp, '_', target)
        if target_type == 'num':
            self._emit_num_check(target, '--')

    def _resolve_assignable(self, target) -> Tuple[str, str, Optional[Symbol]]:
        """Resolve a LHS target expression to (place, type, symbol)."""
        if isinstance(target, Identifier):
            vname = target.name
            sym = self.symbol_table.lookup(vname)
            if sym is None:
                self._error(f"Undeclared variable '{vname}'", target)
                return vname, 'unknown', None
            return vname, sym.data_type, sym

        if isinstance(target, ListAccess):
            vname = target.name
            sym = self.symbol_table.lookup(vname)
            if sym is None:
                self._error(f"Undeclared variable '{vname}'", target)
                return vname, 'unknown', None

            idx_place, idx_type = self.visit(target.index1)
            if not is_valid_index_type(idx_type):
                self._error(
                    f"List index must be integer (num) or bool, "
                    f"got '{idx_type}'",
                    target
                )
            # Compile-time bounds checking for first index
            if sym.is_list and sym.list_size > 0:
                if isinstance(target.index1, Literal) and target.index1.token_type == 'num_lit':
                    try:
                        idx_val = int(target.index1.value)
                        max_idx = sym.list_size - 1
                        if idx_val < 0 or idx_val > max_idx:
                            self._error(
                                f"List index {idx_val} is out of bounds for '{vname}' "
                                f"(valid range: 0 to {max_idx})",
                                target
                            )
                    except ValueError:
                        pass
            if target.index2 is not None:
                # Dimension mismatch: 2 indices on a 1D list
                if sym.is_list and sym.list_dim == 1:
                    self._error(
                        f"'{vname}' is a 1D list but is being accessed with 2 indices",
                        target
                    )
                idx2_place, idx2_type = self.visit(target.index2)
                if not is_valid_index_type(idx2_type):
                    self._error(
                        f"List index must be integer (num) or bool, "
                        f"got '{idx2_type}'",
                        target
                    )
                # Compile-time bounds checking for second index (2D column)
                if sym.is_list and sym.list_col_count > 0:
                    if isinstance(target.index2, Literal) and target.index2.token_type == 'num_lit':
                        try:
                            idx2_val = int(target.index2.value)
                            max_col = sym.list_col_count - 1
                            if idx2_val < 0 or idx2_val > max_col:
                                self._error(
                                    f"Column index {idx2_val} is out of bounds for '{vname}' "
                                    f"(valid range: 0 to {max_col})",
                                    target
                                )
                        except ValueError:
                            pass
                return f'{vname}[{idx_place}][{idx2_place}]', sym.data_type, sym
            return f'{vname}[{idx_place}]', sym.data_type, sym

        if isinstance(target, MemberAccess):
            vname = target.object_name
            sym = self.symbol_table.lookup(vname)
            if sym is None:
                self._error(f"Undeclared variable '{vname}'", target)
                return f'{vname}.{target.member}', 'unknown', None
            group_sym = self.symbol_table.lookup(sym.data_type)
            if group_sym is None or group_sym.kind != 'group':
                self._error(f"'{vname}' is not a group instance", target)
                return f'{vname}.{target.member}', 'unknown', None
            if target.member not in group_sym.group_members:
                self._error(
                    f"Group '{sym.data_type}' has no member '{target.member}'",
                    target
                )
                return f'{vname}.{target.member}', 'unknown', None
            return f'{vname}.{target.member}', group_sym.group_members[target.member], sym

        if isinstance(target, IndexedMemberAccess):
            list_sym = self.symbol_table.lookup(target.list_name)
            if list_sym is None:
                self._error(
                    f"Undeclared variable '{target.list_name}'", target)
                return f'{target.list_name}[0].{target.member}', 'unknown', None
            if not list_sym.is_list:
                self._error(
                    f"'{target.list_name}' is not a list", target)
                return f'{target.list_name}[0].{target.member}', 'unknown', None
            group_sym = self.symbol_table.lookup(list_sym.data_type)
            if group_sym is None or group_sym.kind != 'group':
                self._error(
                    f"'{target.list_name}' is not a list of group instances",
                    target)
                return f'{target.list_name}[0].{target.member}', 'unknown', None
            if target.member not in group_sym.group_members:
                self._error(
                    f"Group '{list_sym.data_type}' has no member '{target.member}'",
                    target)
                return f'{target.list_name}[0].{target.member}', 'unknown', None
            index_place, index_type = self.visit(target.index)
            if not is_valid_index_type(index_type):
                self._error(
                    f"List index must be integer (num) or bool, got '{index_type}'",
                    target)
            if list_sym.list_size > 0 and isinstance(target.index, Literal) \
                    and target.index.token_type == 'num_lit':
                try:
                    idx_val = int(target.index.value)
                    max_idx = list_sym.list_size - 1
                    if idx_val < 0 or idx_val > max_idx:
                        self._error(
                            f"Index {idx_val} is out of bounds for "
                            f"'{target.list_name}' (valid range: 0 to {max_idx})",
                            target)
                except ValueError:
                    pass
            member_type = group_sym.group_members[target.member]
            return (f'{target.list_name}[{index_place}].{target.member}',
                    member_type, list_sym)

        return '_', 'unknown', None

    def visit_FuncCallStmt(self, node: FuncCallStmt):
        self.visit(node.call)

    def visit_ShowStmt(self, node: ShowStmt):
        args = []
        for arg in node.args:
            place, dtype = self.visit(arg)
            args.append((place, dtype))
        for arg_place, arg_dtype in args:
            self._emit('param', arg_place,
                       arg_dtype if arg_dtype == 'bool' else '_')
        self._emit('call', 'show', str(len(args)))

    def visit_DisplayStmt(self, node: DisplayStmt):
        args = []
        for arg in node.args:
            place, dtype = self.visit(arg)
            args.append((place, dtype))
        for arg_place, arg_dtype in args:
            self._emit('param', arg_place,
                       arg_dtype if arg_dtype == 'bool' else '_')
        self._emit('call', 'display', str(len(args)))

    def visit_ReadStmt(self, node: ReadStmt):
        sym = self.symbol_table.lookup(node.variable)
        if sym is None:
            self._error(f"Undeclared variable '{node.variable}'", node)
        elif sym.is_fixed:
            self._error(
                f"Cannot read into fixed variable '{node.variable}'", node
            )
        var_type = sym.data_type if sym else 'text'
        self._emit('read', node.variable, var_type)

    # ── Control statement visitors ────────────────────────────

    def visit_IfChain(self, node: IfChain):
        cond_place, cond_type = self.visit(node.condition)

        if not is_numeric_or_bool(cond_type) and cond_type != 'unknown':
            self._error(
                f"Condition must be boolean or numeric (truthy), "
                f"got '{cond_type}'",
                node
            )

        L_else = self._new_label()
        L_end = self._new_label()

        self._emit('if_false', cond_place, '_', L_else)

        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope_with_unused_check()

        self._emit('goto', '_', '_', L_end)
        self._emit_label(L_else)

        # elif branches
        for elif_br in node.elif_branches:
            ec_place, ec_type = self.visit(elif_br.condition)
            if not is_numeric_or_bool(ec_type) and ec_type != 'unknown':
                self._error(
                    f"Condition must be boolean or numeric (truthy), got '{ec_type}'",
                    elif_br
                )
            L_next = self._new_label()
            self._emit('if_false', ec_place, '_', L_next)

            self.symbol_table.enter_scope()
            for stmt in elif_br.body:
                self.visit(stmt)
            self._exit_scope_with_unused_check()

            self._emit('goto', '_', '_', L_end)
            self._emit_label(L_next)

        # else body
        if node.else_body is not None:
            self.symbol_table.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self._exit_scope_with_unused_check()

        self._emit_label(L_end)

    def visit_SelectStmt(self, node: SelectStmt):
        sym = self.symbol_table.lookup(node.variable)
        if sym is None:
            self._error(f"Undeclared variable '{node.variable}'", node)

        L_end = self._new_label()
        select_type = sym.data_type if sym else 'unknown'
        n = len(node.options)

        # Pre-generate all labels so skip can jump directly to the next option's body
        L_body = [self._new_label() for _ in node.options]
        L_next = [self._new_label() for _ in node.options]

        for i, opt in enumerate(node.options):
            lit_place, lit_type = self.visit(opt.value)
            if not type_compatible(select_type, lit_type):
                self._error(
                    f"Option value type '{lit_type}' does not match "
                    f"select variable type '{select_type}'",
                    opt
                )
            temp = self._new_temp()
            self._emit('==', node.variable, lit_place, temp)
            self._emit('if_false', temp, '_', L_next[i])

            self._emit_label(L_body[i])

            self.symbol_table.enter_scope()
            for stmt in opt.body:
                self.visit(stmt)
            self._exit_scope_with_unused_check()

            if opt.control_flow == 'stop':
                self._emit('goto', '_', '_', L_end)
            else:  # skip: jump directly to next option's body, bypassing its condition
                if i + 1 < n:
                    self._emit('goto', '_', '_', L_body[i + 1])
                # last option with skip: fall through to L_next[i] → fallback → L_end

            self._emit_label(L_next[i])

        if node.fallback is not None:
            self.symbol_table.enter_scope()
            for stmt in node.fallback:
                self.visit(stmt)
            self._exit_scope_with_unused_check()

        self._emit_label(L_end)

    def visit_EachLoop(self, node: EachLoop):
        vname = node.variable

        sym = self.symbol_table.lookup(vname)
        if sym is None:
            self._error(
                f"Loop variable '{vname}' must be declared before the "
                f"each loop",
                node
            )
        else:
            if sym.data_type not in ('num', 'unknown'):
                self._error(
                    f"Loop variable '{vname}' must be type num (integer), "
                    f"got '{sym.data_type}'",
                    node
                )
            if sym.is_fixed:
                self._error(
                    f"Loop variable '{vname}' is fixed and cannot be modified",
                    node
                )

        from_place, from_type = self.visit(node.from_expr)
        if from_type not in ('num', 'unknown'):
            self._error(
                f"'from' value must be integer (num), got '{from_type}'",
                node
            )

        to_place, to_type = self.visit(node.to_expr)
        if to_type not in ('num', 'unknown'):
            self._error(
                f"'to' value must be integer (num), got '{to_type}'",
                node
            )

        step_place = '1'
        step_is_negative = False
        if node.step_expr is not None:
            step_place, step_type = self.visit(node.step_expr)
            if step_type not in ('num', 'unknown'):
                self._error(
                    f"'step' value must be integer (num), got '{step_type}'",
                    node
                )
            if step_place.startswith('-'):
                step_is_negative = True

        self._emit('=', from_place, '_', vname)

        L_test = self._new_label()
        L_end = self._new_label()

        self._emit_label(L_test)

        temp_cond = self._new_temp()
        cond_op = '>=' if step_is_negative else '<='
        self._emit(cond_op, vname, to_place, temp_cond)
        self._emit('if_false', temp_cond, '_', L_end)

        self._loop_depth += 1
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope_with_unused_check()
        self._loop_depth -= 1

        temp_inc = self._new_temp()
        self._emit('+', vname, step_place, temp_inc)
        # Only update loop var if the next value is still within range.
        # This ensures the variable retains its last valid value after the loop.
        temp_check = self._new_temp()
        self._emit(cond_op, temp_inc, to_place, temp_check)
        self._emit('if_false', temp_check, '_', L_end)
        self._emit('=', temp_inc, '_', vname)
        self._emit('goto', '_', '_', L_test)
        self._emit_label(L_end)

    def visit_DuringLoop(self, node: DuringLoop):
        L_test = self._new_label()
        L_end = self._new_label()
        self._emit_label(L_test)

        cond_place, cond_type = self.visit(node.condition)

        if not is_numeric_or_bool(cond_type) and cond_type != 'unknown':
            self._error(
                f"Condition must be boolean or numeric (truthy), got '{cond_type}'",
                node
            )

        self._emit('if_false', cond_place, '_', L_end)

        self._loop_depth += 1
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope_with_unused_check()
        self._loop_depth -= 1

        self._emit('goto', '_', '_', L_test)
        self._emit_label(L_end)

    # ── Expression visitors ───────────────────────────────────
    # Each returns (place: str, dtype: str)

    def visit_BinaryOp(self, node: BinaryOp) -> Tuple[str, str]:
        left_place, left_type = self.visit(node.left)
        right_place, right_type = self.visit(node.right)
        op = node.op

        # Type checking per operator category
        if op in LOGICAL_OPS:
            left_bad = not is_numeric_or_bool(
                left_type) and left_type != 'unknown'
            right_bad = not is_numeric_or_bool(
                right_type) and right_type != 'unknown'
            if left_bad or right_bad:
                if left_bad and right_bad and left_type == right_type:
                    self._error(
                        f"Operator '{op}' is not valid for type '{left_type}'", node
                    )
                elif left_bad and right_bad:
                    self._error(
                        f"Operator '{op}' is not valid for types '{left_type}' and '{right_type}'", node
                    )
                elif left_bad:
                    self._error(
                        f"Operator '{op}' is not valid for type '{left_type}'", node
                    )
                else:
                    self._error(
                        f"Operator '{op}' is not valid for type '{right_type}'", node
                    )
                return '_', 'unknown'
            temp = self._new_temp()
            self._emit(op, left_place, right_place, temp)
            return temp, 'bool'

        if op in EQUALITY_OPS:
            if (left_type not in ('unknown',)
                    and right_type not in ('unknown',)
                    and left_type != right_type):
                if not (left_type in NUMERIC_OR_BOOL
                        and right_type in NUMERIC_OR_BOOL):
                    self._error(
                        f"Cannot compare '{left_type}' with "
                        f"'{right_type}' using '{op}'",
                        node
                    )
                    return '_', 'unknown'
            temp = self._new_temp()
            self._emit(op, left_place, right_place, temp)
            return temp, 'bool'

        if op in RELATIONAL_OPS:
            has_error = False
            if not is_numeric_or_bool(left_type) and left_type != 'unknown':
                self._error(
                    f"Operator '{op}' is not valid for type '{left_type}'", node
                )
                has_error = True
            if not is_numeric_or_bool(right_type) and right_type != 'unknown':
                self._error(
                    f"Operator '{op}' is not valid for type '{right_type}'", node
                )
                has_error = True
            if has_error:
                return '_', 'unknown'
            temp = self._new_temp()
            self._emit(op, left_place, right_place, temp)
            return temp, 'bool'

        if op in ('+', '-'):
            if left_type == TEXT_TYPE or right_type == TEXT_TYPE:
                if op == '+' and left_type == TEXT_TYPE and right_type == TEXT_TYPE:
                    temp = self._new_temp()
                    self._emit('+', left_place, right_place, temp)
                    return temp, TEXT_TYPE
                else:
                    if op == '-':
                        self._error(
                            f"Operator '-' is not valid for type 'text'", node
                        )
                    else:
                        other = right_type if left_type == TEXT_TYPE else left_type
                        self._error(
                            f"Cannot concatenate 'text' with '{other}'", node
                        )
                    return '_', 'unknown'
            elif left_type == CHAR_TYPE or right_type == CHAR_TYPE:
                self._error(
                    f"Operator '{op}' is not valid for type 'letter'", node
                )
                return '_', 'unknown'
            temp = self._new_temp()
            rtype = result_type_of_op(op, left_type, right_type)
            self._emit(op, left_place, right_place, temp)
            if rtype == 'num':
                self._emit_num_check(temp, op)
            return temp, rtype

        if op in ('*', '/', '%'):
            if left_type in (TEXT_TYPE, CHAR_TYPE) or right_type in (TEXT_TYPE, CHAR_TYPE):
                bad = left_type if left_type in (
                    TEXT_TYPE, CHAR_TYPE) else right_type
                self._error(
                    f"Operator '{op}' is not valid for type '{bad}'",
                    node
                )
                return '_', 'unknown'
            temp = self._new_temp()
            rtype = result_type_of_op(op, left_type, right_type)
            self._emit(op, left_place, right_place, temp)
            if op == '*' and rtype == 'num':
                self._emit_num_check(temp, '*')
            return temp, rtype

        if op == '**':
            has_error = False
            if not is_numeric_or_bool(left_type) and left_type != 'unknown':
                self._error(
                    f"Operator '**' is not valid for type '{left_type}'", node
                )
                has_error = True
            if not is_numeric_or_bool(right_type) and right_type != 'unknown':
                self._error(
                    f"Operator '**' is not valid for type '{right_type}'", node
                )
                has_error = True
            if has_error:
                return '_', 'unknown'
            temp = self._new_temp()
            rtype = result_type_of_op('**', left_type, right_type)
            self._emit('**', left_place, right_place, temp)
            if rtype == 'num':
                self._emit_num_check(temp, '**')
            return temp, rtype

        # Fallback
        temp = self._new_temp()
        self._emit(op, left_place, right_place, temp)
        return temp, 'unknown'

    def visit_UnaryOp(self, node: UnaryOp) -> Tuple[str, str]:
        place, dtype = self.visit(node.operand)

        if node.op == '-':
            if not is_numeric_or_bool(dtype) and dtype != 'unknown':
                self._error(
                    f"Unary '-' not valid for type '{dtype}'", node
                )
            temp = self._new_temp()
            self._emit('unary-', place, '_', temp)
            if dtype == 'num':
                self._emit_num_check(temp, 'unary-')
            return temp, dtype

        if node.op == '!':
            if not is_numeric_or_bool(dtype) and dtype != 'unknown':
                self._error(
                    f"Operator '!' not valid for type '{dtype}'", node
                )
            temp = self._new_temp()
            self._emit('!', place, '_', temp)
            return temp, 'bool'

        return place, dtype

    def visit_Literal(self, node: Literal) -> Tuple[str, str]:
        dtype = infer_literal_type(node.token_type, node.value)

        # Precision overflow check for decimal literals
        if node.token_type == 'decimal_lit' and '.' in str(node.value):
            frac_digits = len(str(node.value).split('.')[1])
            if frac_digits > 16:
                self._error(
                    f"Decimal literal '{node.value}' has {frac_digits} fractional "
                    f"digit(s); maximum precision is 16 (bigdecimal)",
                    node
                )

        if node.token_type in ('string_lit', 'char_lit'):
            place = node.value  # lexer already includes surrounding quotes
        else:
            place = str(node.value)
        return place, dtype

    def visit_Identifier(self, node: Identifier) -> Tuple[str, str]:
        sym = self.symbol_table.lookup(node.name)
        if sym is None:
            self._error(f"Undeclared variable '{node.name}'", node)
            return node.name, 'unknown'
        return node.name, sym.data_type

    def visit_FuncCall(self, node: FuncCall) -> Tuple[str, str]:
        args = []
        for arg in node.args:
            place, dtype = self.visit(arg)
            args.append((place, dtype))
        return self._emit_call(node.name, args, node)

    def visit_ListAccess(self, node: ListAccess) -> Tuple[str, str]:
        vname = node.name
        idx_place, idx_type = self.visit(node.index1)
        if not is_valid_index_type(idx_type):
            self._error(
                f"List index must be integer (num) or bool, "
                f"got '{idx_type}'",
                node
            )

        sym = self.symbol_table.lookup(vname)
        if sym is None:
            self._error(f"Undeclared variable '{vname}'", node)
            return '_', 'unknown'
        if not sym.is_list:
            self._error(f"'{vname}' is not a list", node)

        # Compile-time bounds checking for first index
        if sym.is_list and sym.list_size > 0:
            if isinstance(node.index1, Literal) and node.index1.token_type == 'num_lit':
                try:
                    idx_val = int(node.index1.value)
                    max_idx = sym.list_size - 1
                    if idx_val < 0 or idx_val > max_idx:
                        self._error(
                            f"List index {idx_val} is out of bounds for '{vname}' "
                            f"(valid range: 0 to {max_idx})",
                            node
                        )
                except ValueError:
                    pass

        if node.index2 is not None:
            # Dimension mismatch: 2 indices on a 1D list
            if sym.is_list and sym.list_dim == 1:
                self._error(
                    f"'{vname}' is a 1D list but is being accessed with 2 indices",
                    node
                )
            idx2_place, idx2_type = self.visit(node.index2)
            if not is_valid_index_type(idx2_type):
                self._error(
                    f"List index must be integer (num) or bool, "
                    f"got '{idx2_type}'",
                    node
                )
            # Compile-time bounds checking for second index (2D column)
            if sym.is_list and sym.list_col_count > 0:
                if isinstance(node.index2, Literal) and node.index2.token_type == 'num_lit':
                    try:
                        idx2_val = int(node.index2.value)
                        max_col = sym.list_col_count - 1
                        if idx2_val < 0 or idx2_val > max_col:
                            self._error(
                                f"Column index {idx2_val} is out of bounds for '{vname}' "
                                f"(valid range: 0 to {max_col})",
                                node
                            )
                    except ValueError:
                        pass
            temp = self._new_temp()
            self._emit('list_access', vname, f'{idx_place},{idx2_place}', temp)
            return temp, sym.data_type

        temp = self._new_temp()
        self._emit('list_access', vname, idx_place, temp)
        return temp, sym.data_type

    def visit_MemberAccess(self, node: MemberAccess) -> Tuple[str, str]:
        vname = node.object_name
        sym = self.symbol_table.lookup(vname)
        if sym is None:
            self._error(f"Undeclared variable '{vname}'", node)
            return '_', 'unknown'

        group_sym = self.symbol_table.lookup(sym.data_type)
        if group_sym is None or group_sym.kind != 'group':
            self._error(f"'{vname}' is not a group instance", node)
            return '_', 'unknown'
        if node.member not in group_sym.group_members:
            self._error(
                f"Group '{sym.data_type}' has no member '{node.member}'",
                node
            )
            return '_', 'unknown'

        temp = self._new_temp()
        self._emit('member_access', vname, node.member, temp)
        return temp, group_sym.group_members[node.member]

    def visit_IndexedMemberAccess(self, node: IndexedMemberAccess) -> Tuple[str, str]:
        list_sym = self.symbol_table.lookup(node.list_name)
        if list_sym is None:
            self._error(f"Undeclared variable '{node.list_name}'", node)
            return '_', 'unknown'
        if not list_sym.is_list:
            self._error(f"'{node.list_name}' is not a list", node)
            return '_', 'unknown'
        group_sym = self.symbol_table.lookup(list_sym.data_type)
        if group_sym is None or group_sym.kind != 'group':
            self._error(
                f"'{node.list_name}' is not a list of group instances", node)
            return '_', 'unknown'
        if node.member not in group_sym.group_members:
            self._error(
                f"Group '{list_sym.data_type}' has no member '{node.member}'",
                node)
            return '_', 'unknown'
        index_place, index_type = self.visit(node.index)
        if not is_valid_index_type(index_type):
            self._error(
                f"List index must be integer (num) or bool, got '{index_type}'",
                node)
        temp = self._new_temp()
        self._emit('member_access',
                   f'{node.list_name}[{index_place}]', node.member, temp)
        return temp, group_sym.group_members[node.member]

    def visit_SizeCall(self, node: SizeCall) -> Tuple[str, str]:
        sym = self.symbol_table.lookup(node.list_name)
        if sym is None:
            self._error(f"Undeclared variable '{node.list_name}'", node)
        elif not sym.is_list:
            self._error(
                f"size() can only be called on a list; "
                f"'{node.list_name}' is not a list",
                node
            )

        dim_arg = '_'
        if node.dimension is not None:
            dim_arg = node.dimension
            # Validate dimension value is exactly 0
            try:
                dim_val = int(dim_arg)
                if dim_val != 0:
                    self._error(
                        f"size() dimension must be 0 (for column count); got {dim_val}",
                        node
                    )
            except ValueError:
                self._error(
                    f"size() dimension must be an integer literal; got '{dim_arg}'",
                    node
                )
            if sym is not None and sym.is_list and sym.list_dim != 2:
                self._error(
                    f"size() with a dimension argument is only valid for 2D lists; "
                    f"'{node.list_name}' is a 1D list",
                    node
                )

        temp = self._new_temp()
        self._emit('size', node.list_name, dim_arg, temp)
        return temp, 'num'

    def visit_TextLenCall(self, node: TextLenCall) -> Tuple[str, str]:
        arg_place, arg_type = self.visit(node.argument)
        if arg_type not in ('text', 'letter'):
            self._error(
                f"textlen() argument must be of type text or letter; "
                f"got '{arg_type}'",
                node
            )
        temp = self._new_temp()
        self._emit('textlen', arg_place, '_', temp)
        return temp, 'num'

    def visit_CharAtCall(self, node: CharAtCall) -> Tuple[str, str]:
        src_place, src_type = self.visit(node.source)
        if src_type not in ('text', 'letter'):
            self._error(
                f"charat() first argument must be of type text or letter; "
                f"got '{src_type}'",
                node
            )
        idx_place, idx_type = self.visit(node.index)
        if idx_type not in ('num', 'bool'):
            self._error(
                f"charat() second argument (index) must be of type num or bool; "
                f"got '{idx_type}'",
                node
            )
        temp = self._new_temp()
        self._emit('charat', src_place, idx_place, temp)
        return temp, 'letter'

    def visit_OrdCall(self, node: OrdCall) -> Tuple[str, str]:
        arg_place, arg_type = self.visit(node.argument)
        if arg_type != 'letter':
            self._error(
                f"ord() argument must be of type letter; "
                f"got '{arg_type}'",
                node
            )
        temp = self._new_temp()
        self._emit('ord', arg_place, '_', temp)
        return temp, 'num'

    # ── Function call helper ──────────────────────────────────

    def _emit_call(
        self, fname: str, args: List[Tuple[str, str]], node: ASTNode = None
    ) -> Tuple[str, str]:
        func_sym = self.symbol_table.lookup(fname)

        if func_sym is None:
            self._error(f"Undeclared function '{fname}'", node)
            return '_', 'unknown'
        if func_sym.kind != 'function':
            self._error(f"'{fname}' is not a function", node)
            return '_', 'unknown'

        if len(args) != len(func_sym.params):
            self._error(
                f"Function '{fname}' expects {len(func_sym.params)} "
                f"argument(s), got {len(args)}",
                node
            )
        else:
            for i, ((arg_place, arg_type), (param_type, param_name)) in \
                    enumerate(zip(args, func_sym.params)):
                if not type_compatible(param_type, arg_type):
                    self._error(
                        f"Argument {i + 1} of '{fname}': expected "
                        f"'{param_type}', got '{arg_type}'",
                        node
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


# ═══════════════════════════════════════════════════════════════
# SEMANTIC ANALYZER (ORCHESTRATOR)
# ═══════════════════════════════════════════════════════════════

class SemanticAnalyzer:
    """
    Tree-walking semantic analyzer + TAC emitter for KUCODE.

    Input : Program AST node from the parser.
    Output: (List[Quadruple], List[SemanticError])
    """

    def __init__(self, ast: Program) -> None:
        self.ast = ast
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        self.quadruples: List[Quadruple] = []
        self.symbol_table = SymbolTable()

    def analyze(self) -> Tuple[List[Quadruple], List[SemanticError]]:
        """Run both passes and return (quadruples, errors)."""
        # Pass 1: collect declarations
        collector = DeclarationCollector(self.symbol_table)
        collector.visit(self.ast)

        # Pass 2: semantic checks + TAC emission
        checker = SemanticChecker(self.symbol_table)
        checker.visit(self.ast)

        self.quadruples = checker.quadruples
        self.errors = collector.errors + checker.errors

        # Check global scope for unused variables
        global_scope = self.symbol_table.scopes[0]
        for name, sym in global_scope.items():
            if sym.kind in ('variable', 'list') and not sym.used:
                checker.warnings.append(
                    f"Warning: Variable '{name}' declared at line {sym.line} is never used"
                )

        self.warnings = checker.warnings
        return self.quadruples, self.errors

    # ── Output / display helpers ──────────────────────────────

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
        if self.warnings:
            print("\n" + "-" * 60)
            print(f"WARNINGS  ({len(self.warnings)})")
            print("-" * 60)
            for w in self.warnings:
                print(f"  {w}")

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
