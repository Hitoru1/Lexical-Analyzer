"""
KUCODE Code Generator (TAC-Based)
=================================
Translates TAC quadruples (from the semantic analyzer) into executable Python code.
Uses block-dispatch loop to handle goto/label control flow.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Tuple

from semantic_analyzer import Quadruple, SymbolTable


# KUCODE operator → Python operator mapping
_OP_MAP = {
    '&&': 'and',
    '||': 'or',
}

# Default values for group member types
_TYPE_DEFAULTS = {
    'num': '0',
    'decimal': '0.0',
    'bigdecimal': '0.0',
    'bool': '0',
    'text': '""',
    'letter': '""',
}

# Arithmetic / comparison operators that translate directly
_BINARY_OPS = {'+', '-', '*', '/', '//', '%', '**',
               '==', '!=', '>', '<', '>=', '<='}


class TACCodeGenerator:
    """Reads TAC quadruples and emits Python source code."""

    def __init__(self, quadruples: List[Quadruple],
                 symbol_table: SymbolTable) -> None:
        self.quads = quadruples
        self.symbol_table = symbol_table
        self.lines: List[str] = []
        self._indent_level: int = 0

    # ── Public API ────────────────────────────────────────────

    def generate(self) -> str:
        """Generate Python code from TAC quadruples. Returns complete source."""
        preamble, functions, main_block = self._segment_quadruples()

        self._emit_line('# KUCODE Generated Code')
        self._emit_blank()

        # Group class definitions (from symbol table, TAC has no group opcode)
        self._emit_groups()

        # Runtime list-building stack must exist before the preamble uses it
        self._emit_line('_elems = []')

        # Worldwide variable assignments
        if preamble:
            self._emit_quads_straight(preamble)
            self._emit_blank()

        # Function definitions
        for func_quads in functions:
            self._emit_function(func_quads)
            self._emit_blank()

        # Runtime param-passing stack (list stack is re-initialised in main block below)
        self._emit_line('_params = []')
        self._emit_line('_elems = []')

        # Main block (start...halt)
        if main_block:
            self._emit_block(main_block)

        return '\n'.join(self.lines) + '\n'

    # ── Segmentation ──────────────────────────────────────────

    def _segment_quadruples(self) -> Tuple[List[Quadruple],
                                           List[List[Quadruple]],
                                           List[Quadruple]]:
        """Split quads into (preamble, [function_blocks], main_block)."""
        preamble: List[Quadruple] = []
        functions: List[List[Quadruple]] = []
        main_block: List[Quadruple] = []

        i = 0
        n = len(self.quads)

        # Preamble: everything before first func_begin or label start
        while i < n:
            q = self.quads[i]
            if q.op == 'func_begin':
                break
            if q.op == 'label' and q.arg1 == 'start':
                break
            preamble.append(q)
            i += 1

        # Functions: func_begin ... func_end blocks
        while i < n and self.quads[i].op == 'func_begin':
            func_block: List[Quadruple] = []
            func_block.append(self.quads[i])
            i += 1
            while i < n and self.quads[i].op != 'func_end':
                func_block.append(self.quads[i])
                i += 1
            if i < n:  # func_end
                func_block.append(self.quads[i])
                i += 1
            functions.append(func_block)

        # Main block: label start ... halt
        while i < n:
            main_block.append(self.quads[i])
            i += 1

        return preamble, functions, main_block

    # ── Group class emission ──────────────────────────────────

    def _emit_groups(self) -> None:
        """Emit Python class definitions for KUCODE groups from symbol table."""
        if not self.symbol_table.scopes:
            return
        global_scope = self.symbol_table.scopes[0]
        for name, sym in global_scope.items():
            if sym.kind == 'group':
                self._emit_line(f'class {name}:')
                self._indent()
                self._emit_line('def __init__(self):')
                self._indent()
                if sym.group_members:
                    for member_name, member_type in sym.group_members.items():
                        default = _TYPE_DEFAULTS.get(member_type, 'None')
                        self._emit_line(f'self.{member_name} = {default}')
                else:
                    self._emit_line('pass')
                self._dedent()
                self._dedent()
                self._emit_blank()

    # ── Function emission ─────────────────────────────────────

    def _emit_function(self, quads: List[Quadruple]) -> None:
        """Emit a Python function definition from func_begin...func_end quads."""
        # First quad is func_begin
        func_name = quads[0].arg1

        # Collect param_receive quads to build parameter list
        params: List[str] = []
        body_start = 1
        for j in range(1, len(quads)):
            if quads[j].op == 'param_receive':
                params.append(quads[j].arg1)
                body_start = j + 1
            else:
                break

        self._emit_line(f'def {func_name}({", ".join(params)}):')
        self._indent()

        # Emit global declarations for worldwide variables
        worldwide_names = self._get_worldwide_names()
        if worldwide_names:
            self._emit_line(f'global {", ".join(worldwide_names)}')

        # Runtime stacks for param passing and list building
        needs_params = any(q.op in ('param', 'call') for q in quads)
        needs_elems = any(q.op in ('list_elem', 'list_1d', 'list_2d')
                          for q in quads)
        if needs_params:
            self._emit_line('_params = []')
        if needs_elems:
            self._emit_line('_elems = []')

        # Body: everything between param_receive and func_end
        body = quads[body_start:]
        # Remove trailing func_end
        if body and body[-1].op == 'func_end':
            body = body[:-1]

        if body:
            self._emit_block(body)
        else:
            self._emit_line('pass')

        self._dedent()

    # ── Block emission (dispatch loop or straight-line) ───────

    def _emit_block(self, quads: List[Quadruple]) -> None:
        """Emit a block of quads, using dispatch loop if needed."""
        has_control_flow = any(
            q.op in ('goto', 'if_false', 'label', 'halt') for q in quads
        )

        if not has_control_flow:
            self._emit_quads_straight(quads)
            return

        # Build blocks: split by labels
        blocks = self._build_blocks(quads)

        if not blocks:
            return

        # Get the first block label
        first_label = blocks[0][0]

        self._emit_line(f'_block = "{first_label}"')
        self._emit_line('while True:')
        self._indent()

        for i, (label, block_quads) in enumerate(blocks):
            keyword = 'if' if i == 0 else 'elif'
            self._emit_line(f'{keyword} _block == "{label}":')
            self._indent()
            self._emit_quads_in_block(block_quads, blocks, i)
            self._dedent()

        self._dedent()

    def _build_blocks(self, quads: List[Quadruple]) -> List[Tuple[str, List[Quadruple]]]:
        """Split quads into labeled blocks: [(label, [quads_until_next_label])]."""
        blocks: List[Tuple[str, List[Quadruple]]] = []
        current_label: Optional[str] = None
        current_quads: List[Quadruple] = []

        for q in quads:
            if q.op == 'label':
                # Save previous block if it exists
                if current_label is not None:
                    blocks.append((current_label, current_quads))
                current_label = q.arg1
                current_quads = []
            else:
                if current_label is None:
                    # Quads before any label — create a synthetic entry block
                    current_label = '__entry'
                current_quads.append(q)

        # Save last block
        if current_label is not None:
            blocks.append((current_label, current_quads))

        return blocks

    def _emit_quads_in_block(self, quads: List[Quadruple],
                             all_blocks: List[Tuple[str, List[Quadruple]]],
                             block_idx: int) -> None:
        """Emit quads within a dispatch block, handling fall-through."""
        emitted_any = False
        for j, q in enumerate(quads):
            emitted = self._emit_single_quad(q)
            if emitted:
                emitted_any = True

        # Determine if last instruction already transfers control
        needs_fallthrough = True
        if quads:
            last = quads[-1]
            if last.op in ('goto', 'halt', 'return'):
                needs_fallthrough = False

        # Add fall-through to next block if needed
        if needs_fallthrough:
            next_idx = block_idx + 1
            if next_idx < len(all_blocks):
                next_label = all_blocks[next_idx][0]
                self._emit_line(f'_block = "{next_label}"')
            else:
                self._emit_line('break')

    # ── Straight-line emission (no control flow) ──────────────

    def _emit_quads_straight(self, quads: List[Quadruple]) -> None:
        """Emit quads as straight-line Python code (no dispatch loop)."""
        for q in quads:
            self._emit_single_quad(q)

    # ── Single quad → Python ──────────────────────────────────

    def _emit_single_quad(self, q: Quadruple) -> bool:
        """Emit Python for one quadruple. Returns True if a line was emitted."""
        op = q.op

        # ── Assignment ──
        if op == '=':
            val = self._translate_value(q.arg1)
            self._emit_line(f'{q.result} = {val}')
            return True

        # ── Binary arithmetic / comparison ──
        if op in _BINARY_OPS:
            left = self._translate_value(q.arg1)
            right = self._translate_value(q.arg2)
            self._emit_line(f'{q.result} = ({left} {op} {right})')
            return True

        # ── Logical operators ──
        if op == '&&':
            left = self._translate_value(q.arg1)
            right = self._translate_value(q.arg2)
            self._emit_line(f'{q.result} = ({left} and {right})')
            return True

        if op == '||':
            left = self._translate_value(q.arg1)
            right = self._translate_value(q.arg2)
            self._emit_line(f'{q.result} = ({left} or {right})')
            return True

        # ── Unary operators ──
        if op == 'unary-':
            val = self._translate_value(q.arg1)
            self._emit_line(f'{q.result} = (-{val})')
            return True

        if op == '!':
            val = self._translate_value(q.arg1)
            self._emit_line(f'{q.result} = (not {val})')
            return True

        # ── Control flow ──
        if op == 'if_false':
            val = self._translate_value(q.arg1)
            self._emit_line(f'if not {val}:')
            self._indent()
            self._emit_line(f'_block = "{q.result}"')
            self._emit_line('continue')
            self._dedent()
            return True

        if op == 'goto':
            self._emit_line(f'_block = "{q.result}"')
            self._emit_line('continue')
            return True

        if op == 'halt':
            self._emit_line('break')
            return True

        # ── label is consumed during block building ──
        if op == 'label':
            return False

        # ── Function boundaries (consumed during segmentation) ──
        if op in ('func_begin', 'func_end', 'param_receive'):
            return False

        # ── Parameter passing ──
        if op == 'param':
            val = self._translate_value(q.arg1)
            if q.arg2 == 'bool':
                self._emit_line(f"_params.append('Yes' if {val} else 'No')")
            else:
                self._emit_line(f'_params.append({val})')
            return True

        # ── Function / built-in calls ──
        if op == 'call':
            return self._emit_call(q)

        # ── Return ──
        if op == 'return':
            if q.arg1 != '_':
                val = self._translate_value(q.arg1)
                self._emit_line(f'return {val}')
            else:
                self._emit_line('return')
            return True

        # ── Read (input) ──
        if op == 'read':
            return self._emit_read(q)

        # ── List operations ──
        if op == 'list_elem':
            self._emit_line(f'_elems.append({self._translate_value(q.arg1)})')
            return True

        if op == 'list_1d':
            count = int(q.arg1)
            self._emit_line(f'{q.result} = _elems[-{count}:]')
            self._emit_line(f'_elems = _elems[:-{count}]')
            return True

        if op == 'list_2d':
            row_count = int(q.arg1)
            col_count = int(q.arg2)
            total = row_count * col_count
            self._emit_line(f'_flat = _elems[-{total}:]')
            self._emit_line(f'_elems = _elems[:-{total}]')
            self._emit_line(
                f'{q.result} = [_flat[_i*{col_count}:(_i+1)*{col_count}] '
                f'for _i in range({row_count})]'
            )
            return True

        if op == 'list_assign':
            val = self._translate_value(q.arg1)
            self._emit_line(f'{q.result} = {val}')
            return True

        if op == 'list_access':
            name = q.arg1
            if ',' in q.arg2:
                idx1, idx2 = q.arg2.split(',', 1)
                self._emit_line(f'{q.result} = {name}[{idx1}][{idx2}]')
            else:
                self._emit_line(f'{q.result} = {name}[{q.arg2}]')
            return True

        # ── Member access ──
        if op == 'member_access':
            self._emit_line(f'{q.result} = {q.arg1}.{q.arg2}')
            return True

        # ── Size (len) ──
        if op == 'size':
            name = q.arg1
            if q.arg2 != '_' and q.arg2 == '0':
                self._emit_line(f'{q.result} = len({name}[0])')
            else:
                self._emit_line(f'{q.result} = len({name})')
            return True

        # ── Textlen (len for strings) ──
        if op == 'textlen':
            self._emit_line(f'{q.result} = len({q.arg1})')
            return True

        # ── Charat (string indexing) ──
        if op == 'charat':
            self._emit_line(f'{q.result} = {q.arg1}[{q.arg2}]')
            return True

        # ── Ord (character to ASCII) ──
        if op == 'ord':
            self._emit_line(f'{q.result} = ord({q.arg1})')
            return True

        # Fallback: emit as comment
        self._emit_line(f'# Unknown TAC op: {q}')
        return True

    # ── Call emission ─────────────────────────────────────────

    def _emit_call(self, q: Quadruple) -> bool:
        """Emit a function/built-in call quad."""
        fname = q.arg1
        argc = int(q.arg2) if q.arg2 != '_' else 0

        if fname == 'show':
            if argc > 0:
                self._emit_line(f'print(*_params[-{argc}:], flush=True)')
                self._emit_line(f'_params = _params[:-{argc}]')
            else:
                self._emit_line('print(flush=True)')
            return True

        if fname == 'display':
            if argc > 0:
                self._emit_line(
                    f'print(*_params[-{argc}:], sep="", end="", flush=True)')
                self._emit_line(f'_params = _params[:-{argc}]')
            else:
                self._emit_line('print(sep="", end="", flush=True)')
            return True

        # User-defined function call
        if argc > 0:
            args_str = ', '.join(
                f'_params[{-argc + i}]' for i in range(argc))
            if q.result != '_':
                self._emit_line(f'{q.result} = {fname}({args_str})')
            else:
                self._emit_line(f'{fname}({args_str})')
            self._emit_line(f'_params = _params[:-{argc}]')
        else:
            if q.result != '_':
                self._emit_line(f'{q.result} = {fname}()')
            else:
                self._emit_line(f'{fname}()')
        return True

    # ── Read (input) emission ─────────────────────────────────

    def _emit_read(self, q: Quadruple) -> bool:
        """Emit type-coerced input() for a read quad."""
        var_name = q.arg1
        var_type = q.arg2 if q.arg2 != '_' else 'text'

        if var_type == 'num':
            self._emit_line(f'{var_name} = int(input())')
        elif var_type in ('decimal', 'bigdecimal'):
            self._emit_line(f'{var_name} = float(input())')
        elif var_type == 'letter':
            self._emit_line(f'{var_name} = input()[0]')
        elif var_type == 'bool':
            self._emit_line(
                f"{var_name} = input().strip() in ('Yes', '1', 'true')")
        else:
            self._emit_line(f'{var_name} = input()')
        return True

    # ── Helpers ───────────────────────────────────────────────

    def _emit_line(self, line: str) -> None:
        self.lines.append('    ' * self._indent_level + line)

    def _emit_blank(self) -> None:
        self.lines.append('')

    def _indent(self) -> None:
        self._indent_level += 1

    def _dedent(self) -> None:
        self._indent_level -= 1

    def _translate_value(self, val: str) -> str:
        """Translate TAC value to Python value (Yes→1, No→0)."""
        if val == 'Yes':
            return '1'
        if val == 'No':
            return '0'
        return val

    def _get_worldwide_names(self) -> List[str]:
        """Get all worldwide variable names from the global scope."""
        names = []
        if self.symbol_table.scopes:
            for name, sym in self.symbol_table.scopes[0].items():
                if sym.is_worldwide:
                    names.append(name)
        return names
