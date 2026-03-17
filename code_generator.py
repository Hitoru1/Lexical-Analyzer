"""
KUCODE Code Generator
=====================
Translates AST (validated by semantic analyzer) into executable Python code.
Uses the visitor pattern over AST nodes.
"""

from __future__ import annotations
from typing import List, Optional

from ast_nodes import (
    Program, GroupDef, GroupMember, WorldwideDecl, FuncDef, Parameter,
    VarDecl, FixedDecl, ListDecl,
    Assignment, CompoundAssign, Increment, Decrement,
    IfChain, ElifBranch, SelectStmt, OptionBlock,
    EachLoop, DuringLoop, FuncCallStmt, ReturnStmt, ShowStmt, DisplayStmt, ReadStmt,
    BinaryOp, UnaryOp, Literal, Identifier, FuncCall,
    ListAccess, MemberAccess, SizeCall, ListLiteral1D, ListLiteral2D,
    Expr
)
from semantic_analyzer import ASTVisitor, SymbolTable


# Default values for group member types
_TYPE_DEFAULTS = {
    'num': '0',
    'decimal': '0.0',
    'bigdecimal': '0.0',
    'bool': 'False',
    'text': '""',
    'letter': '""',
}

# KUCODE operator → Python operator mapping
_OP_MAP = {
    '&&': 'and',
    '||': 'or',
    '!': 'not',
}


class CodeGenerator(ASTVisitor):
    """Walks the AST and emits Python source code."""

    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table
        self.lines: List[str] = []
        self._indent_level: int = 0
        self._select_counter: int = 0
        self._var_types: dict = {}  # name → datatype (populated as decls are visited)

    def generate(self, ast: Program) -> str:
        """Generate Python code from the AST. Returns the complete Python source."""
        self.visit(ast)
        return '\n'.join(self.lines) + '\n'

    # ── Helpers ──────────────────────────────────────────────

    def _emit_line(self, line: str) -> None:
        self.lines.append('    ' * self._indent_level + line)

    def _emit_blank(self) -> None:
        self.lines.append('')

    def _indent(self) -> None:
        self._indent_level += 1

    def _dedent(self) -> None:
        self._indent_level -= 1

    def _get_worldwide_names(self) -> List[str]:
        """Get all worldwide variable names from the global scope."""
        names = []
        if self.symbol_table.scopes:
            for name, sym in self.symbol_table.scopes[0].items():
                if sym.is_worldwide:
                    names.append(name)
        return names

    def _map_op(self, op: str) -> str:
        """Map KUCODE operator to Python operator."""
        return _OP_MAP.get(op, op)

    def _is_negative_step(self, step_expr: Expr) -> Optional[bool]:
        """Determine step direction. True=negative, False=positive, None=unknown."""
        if isinstance(step_expr, Literal):
            try:
                return float(step_expr.value) < 0
            except (ValueError, TypeError):
                return None
        if isinstance(step_expr, UnaryOp) and step_expr.op == '-':
            return True
        return None

    def _get_var_type(self, name: str) -> str:
        """Look up variable type from local tracking dict."""
        return self._var_types.get(name, 'text')

    def _visit_stmts(self, stmts: list) -> None:
        """Visit a list of statements."""
        for stmt in stmts:
            self.visit(stmt)

    # ── Program Structure ────────────────────────────────────

    def visit_Program(self, node: Program) -> None:
        self._emit_line('# KUCODE Generated Code')
        self._emit_blank()

        # Groups
        for group in node.groups:
            self.visit(group)
            self._emit_blank()

        # Worldwide declarations
        for decl in node.worldwide_decls:
            self.visit(decl)
        if node.worldwide_decls:
            self._emit_blank()

        # Function definitions
        for func in node.functions:
            self.visit(func)
            self._emit_blank()

        # Start block (main)
        self._visit_stmts(node.start_body)

    def visit_GroupDef(self, node: GroupDef) -> None:
        self._emit_line(f'class {node.name}:')
        self._indent()
        self._emit_line('def __init__(self):')
        self._indent()
        if node.members:
            for member in node.members:
                default = _TYPE_DEFAULTS.get(member.datatype, 'None')
                self._emit_line(f'self.{member.name} = {default}')
        else:
            self._emit_line('pass')
        self._dedent()
        self._dedent()

    def visit_WorldwideDecl(self, node: WorldwideDecl) -> None:
        self._var_types[node.name] = node.datatype
        if node.value is not None:
            val = self.visit(node.value)
            self._emit_line(f'{node.name} = {val}')
        else:
            default = _TYPE_DEFAULTS.get(node.datatype, 'None')
            self._emit_line(f'{node.name} = {default}')

    def visit_FuncDef(self, node: FuncDef) -> None:
        params = ', '.join(p.name for p in node.params)
        self._emit_line(f'def {node.name}({params}):')
        self._indent()

        # Register parameter types
        for p in node.params:
            self._var_types[p.name] = p.datatype

        # Emit global declarations for worldwide variables
        worldwide_names = self._get_worldwide_names()
        if worldwide_names:
            self._emit_line(f'global {", ".join(worldwide_names)}')

        # Local declarations
        for decl in node.local_decls:
            self.visit(decl)

        # Body
        self._visit_stmts(node.body)

        # Return statement
        if node.return_stmt is not None:
            self.visit(node.return_stmt)

        # Empty function guard
        if not node.local_decls and not node.body and node.return_stmt is None:
            self._emit_line('pass')

        self._dedent()

    # ── Declarations ─────────────────────────────────────────

    def visit_VarDecl(self, node: VarDecl) -> None:
        self._var_types[node.name] = node.datatype
        if node.is_group_typed:
            self._emit_line(f'{node.name} = {node.datatype}()')
        elif node.value is not None:
            val = self.visit(node.value)
            self._emit_line(f'{node.name} = {val}')
        else:
            default = _TYPE_DEFAULTS.get(node.datatype, 'None')
            self._emit_line(f'{node.name} = {default}')

    def visit_FixedDecl(self, node: FixedDecl) -> None:
        self._var_types[node.name] = node.datatype
        val = self.visit(node.value)
        self._emit_line(f'{node.name} = {val}')

    def visit_ListDecl(self, node: ListDecl) -> None:
        self._var_types[node.name] = node.datatype
        if node.value is not None:
            val = self.visit(node.value)
            self._emit_line(f'{node.name} = {val}')
        else:
            self._emit_line(f'{node.name} = []')

    # ── Statements ───────────────────────────────────────────

    def visit_Assignment(self, node: Assignment) -> None:
        target = self.visit(node.target)
        value = self.visit(node.value)
        self._emit_line(f'{target} = {value}')

    def visit_CompoundAssign(self, node: CompoundAssign) -> None:
        target = self.visit(node.target)
        value = self.visit(node.value)
        self._emit_line(f'{target} {node.op} {value}')

    def visit_Increment(self, node: Increment) -> None:
        target = self.visit(node.target)
        self._emit_line(f'{target} += 1')

    def visit_Decrement(self, node: Decrement) -> None:
        target = self.visit(node.target)
        self._emit_line(f'{target} -= 1')

    def visit_IfChain(self, node: IfChain) -> None:
        cond = self.visit(node.condition)
        self._emit_line(f'if {cond}:')
        self._indent()
        if node.body:
            self._visit_stmts(node.body)
        else:
            self._emit_line('pass')
        self._dedent()

        for elif_branch in node.elif_branches:
            cond = self.visit(elif_branch.condition)
            self._emit_line(f'elif {cond}:')
            self._indent()
            if elif_branch.body:
                self._visit_stmts(elif_branch.body)
            else:
                self._emit_line('pass')
            self._dedent()

        if node.else_body is not None:
            self._emit_line('else:')
            self._indent()
            if node.else_body:
                self._visit_stmts(node.else_body)
            else:
                self._emit_line('pass')
            self._dedent()

    def visit_SelectStmt(self, node: SelectStmt) -> None:
        self._select_counter += 1
        flag = f'_sel_done_{self._select_counter}'
        self._emit_line(f'{flag} = False')

        for option in node.options:
            val = self.visit(option.value)
            self._emit_line(f'if not {flag} and {node.variable} == {val}:')
            self._indent()
            if option.body:
                self._visit_stmts(option.body)
            else:
                self._emit_line('pass')
            if option.control_flow == 'stop':
                self._emit_line(f'{flag} = True')
            self._dedent()

        if node.fallback is not None:
            self._emit_line(f'if not {flag}:')
            self._indent()
            if node.fallback:
                self._visit_stmts(node.fallback)
            else:
                self._emit_line('pass')
            self._dedent()

    def visit_EachLoop(self, node: EachLoop) -> None:
        from_val = self.visit(node.from_expr)
        to_val = self.visit(node.to_expr)

        if node.step_expr is None:
            # Default step is 1 (positive)
            self._emit_line(
                f'for {node.variable} in range({from_val}, {to_val} + 1):')
        else:
            is_neg = self._is_negative_step(node.step_expr)
            step_val = self.visit(node.step_expr)

            if is_neg is True:
                self._emit_line(
                    f'for {node.variable} in range({from_val}, {to_val} - 1, {step_val}):')
            elif is_neg is False:
                self._emit_line(
                    f'for {node.variable} in range({from_val}, {to_val} + 1, {step_val}):')
            else:
                # Unknown direction — runtime check
                step_temp = f'_step_{node.variable}'
                self._emit_line(f'{step_temp} = {step_val}')
                self._emit_line(
                    f'for {node.variable} in range({from_val}, '
                    f'{to_val} + (1 if {step_temp} > 0 else -1), {step_temp}):')

        self._indent()
        if node.body:
            self._visit_stmts(node.body)
        else:
            self._emit_line('pass')
        self._dedent()

    def visit_DuringLoop(self, node: DuringLoop) -> None:
        cond = self.visit(node.condition)
        self._emit_line(f'while {cond}:')
        self._indent()
        if node.body:
            self._visit_stmts(node.body)
        else:
            self._emit_line('pass')
        self._dedent()

    def visit_FuncCallStmt(self, node: FuncCallStmt) -> None:
        call_expr = self.visit(node.call)
        self._emit_line(call_expr)

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        if node.value is not None:
            val = self.visit(node.value)
            self._emit_line(f'return {val}')
        else:
            self._emit_line('return')

    def visit_ShowStmt(self, node: ShowStmt) -> None:
        args = ', '.join(self.visit(arg) for arg in node.args)
        self._emit_line(f'print({args}, flush=True)')

    def visit_DisplayStmt(self, node: DisplayStmt) -> None:
        args = ', '.join(self.visit(arg) for arg in node.args)
        self._emit_line(f'print({args}, sep="", end="", flush=True)')

    def visit_ReadStmt(self, node: ReadStmt) -> None:
        var_type = self._get_var_type(node.variable)
        if var_type == 'num':
            self._emit_line(f'{node.variable} = int(input())')
        elif var_type in ('decimal', 'bigdecimal'):
            self._emit_line(f'{node.variable} = float(input())')
        elif var_type == 'letter':
            self._emit_line(f'{node.variable} = input()[0]')
        elif var_type == 'bool':
            self._emit_line(
                f"{node.variable} = input().strip() in ('Yes', '1', 'true')")
        else:  # text or fallback
            self._emit_line(f'{node.variable} = input()')

    # ── Expressions (return str) ─────────────────────────────

    def visit_BinaryOp(self, node: BinaryOp) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self._map_op(node.op)
        return f'({left} {op} {right})'

    def visit_UnaryOp(self, node: UnaryOp) -> str:
        operand = self.visit(node.operand)
        op = self._map_op(node.op)
        if op == 'not':
            return f'(not {operand})'
        return f'({op}{operand})'

    def visit_Literal(self, node: Literal) -> str:
        if node.token_type in ('string_lit', 'char_lit'):
            # Lexer keeps surrounding quotes in value — strip them, then re-wrap
            raw = node.value
            if len(raw) >= 2 and raw[0] in ('"', "'") and raw[-1] in ('"', "'"):
                raw = raw[1:-1]
            if node.token_type == 'string_lit':
                return f'"{raw}"'
            else:
                return f"'{raw}'"
        if node.value == 'Yes':
            return 'True'
        if node.value == 'No':
            return 'False'
        return node.value

    def visit_Identifier(self, node: Identifier) -> str:
        return node.name

    def visit_FuncCall(self, node: FuncCall) -> str:
        args = ', '.join(self.visit(arg) for arg in node.args)
        return f'{node.name}({args})'

    def visit_ListAccess(self, node: ListAccess) -> str:
        idx1 = self.visit(node.index1)
        if node.index2 is not None:
            idx2 = self.visit(node.index2)
            return f'{node.name}[{idx1}][{idx2}]'
        return f'{node.name}[{idx1}]'

    def visit_MemberAccess(self, node: MemberAccess) -> str:
        return f'{node.object_name}.{node.member}'

    def visit_SizeCall(self, node: SizeCall) -> str:
        if node.dimension is not None and node.dimension == '0':
            return f'len({node.list_name}[0])'
        return f'len({node.list_name})'

    def visit_ListLiteral1D(self, node: ListLiteral1D) -> str:
        elems = ', '.join(self.visit(e) for e in node.elements)
        return f'[{elems}]'

    def visit_ListLiteral2D(self, node: ListLiteral2D) -> str:
        rows = ', '.join(self.visit(row) for row in node.rows)
        return f'[{rows}]'
