
from ast_nodes import (
    Program, GroupDef, GroupMember, WorldwideDecl, FuncDef, Parameter,
    VarDecl, FixedDecl, ListDecl,
    Assignment, CompoundAssign, Increment, Decrement,
    IfChain, ElifBranch, SelectStmt, OptionBlock,
    EachLoop, DuringLoop, FuncCallStmt, ReturnStmt, ShowStmt, DisplayStmt, ReadStmt,
    BinaryOp, UnaryOp, Literal, Identifier, FuncCall,
    ListAccess, MemberAccess, SizeCall, ListLiteral1D, ListLiteral2D,
)

# Sentinel for tail-epsilon results
_TAIL_EMPTY = object()


class TableDrivenParser:
    def __init__(self, tokens):
        """Initialize parser with token stream"""
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

        self._init_grammar()
        self._compute_first_sets()
        self._compute_follow_sets()
        self._build_parsing_table()

        self.stack = ['$', '<program>']
        self.derivations = []
        self.skipped_expected = set()

        # Semantic stack for AST construction
        self.sem_stack = []
        self._build_action_registry()

    def _init_grammar(self):
        """Defining the 289 CFG Productions"""

        self.productions = {

            # PROGRAM STRUCTURE

            '<program>': [
                ['<group_part>']
            ],

            '<group_part>': [
                ['<group_definitions>', '<group_part>'],
                ['<worldwide_part>']
            ],

            '<worldwide_part>': [
                ['<global_variable_declarations>', '<worldwide_part>'],
                ['<define_part>']
            ],

            '<define_part>': [
                ['<function_definitions>', '<define_part>'],
                ['<start_block>']
            ],

            '<start_block>': [
                ['start', '{', '<statements>', '}', 'finish']
            ],

            # GROUP DEFINITIONS

            '<group_definitions>': [
                ['group', 'identifier', '{', '<group_body>', '}']
            ],

            '<group_body>': [
                ['<group_member>', '<group_body_tail>'],
                ['λ']  # 11
            ],

            '<group_body_tail>': [
                ['<group_member>', '<group_body_tail>'],
                ['λ']
            ],

            '<group_member>': [
                ['<datatype>', 'identifier', ';']
            ],

            # DATATYPES

            '<datatype>': [
                ['num'],
                ['decimal'],
                ['bigdecimal'],
                ['bool'],
                ['text'],
                ['letter']
            ],

            # GLOBAL DECLARATIONS

            '<global_variable_declarations>': [
                ['worldwide', '<global_modifier>', '<global_typed_decl>']
            ],

            '<global_modifier>': [
                ['fixed'],
                ['λ']
            ],

            '<global_typed_decl>': [
                ['num', 'identifier', '=', '<stmt_value>', ';'],
                ['decimal', 'identifier', '=', '<stmt_value>', ';'],
                ['bigdecimal', 'identifier', '=', '<stmt_value>', ';'],
                ['bool', 'identifier', '=', '<stmt_value>', ';'],
                ['text', 'identifier', '=', '<stmt_value>', ';'],
                ['letter', 'identifier', '=', '<stmt_value>', ';']
            ],

            # FUNCTION DEFINITIONS

            '<function_definitions>': [
                ['define', '<return_type>', 'identifier', '(', '<parameter_list>', ')',
                 '{', '<local_declarations>', '<statements>', '<optional_return>', '}']
            ],

            '<return_type>': [
                ['num'],
                ['decimal'],
                ['bigdecimal'],
                ['bool'],
                ['text'],
                ['letter'],
                ['empty']
            ],

            '<parameter_list>': [
                ['<parameter>', '<parameter_list_tail>'],
                ['λ']
            ],

            '<parameter_list_tail>': [
                [',', '<parameter>', '<parameter_list_tail>'],
                ['λ']
            ],

            '<parameter>': [
                ['<datatype>', 'identifier']
            ],

            '<optional_return>': [
                ['give', '<return_tail>'],
                ['λ']
            ],

            '<return_tail>': [
                ['<stmt_value>', ';'],
                [';']
            ],


            # LOCAL DECLARATIONS

            '<local_declarations>': [
                ['<declaration>', '<local_declarations>'],
                ['λ']
            ],

            '<declaration>': [
                ['<local_declaration>'],
                ['<fixed_declaration>'],
                ['<list_declaration>']
            ],

            '<local_declaration>': [
                ['identifier', 'identifier', ';'],
                ['num', 'identifier', '=', '<stmt_value>', ';'],
                ['decimal', 'identifier', '=', '<stmt_value>', ';'],
                ['bigdecimal', 'identifier', '=', '<stmt_value>', ';'],
                ['bool', 'identifier', '=', '<stmt_value>', ';'],
                ['text', 'identifier', '=', '<stmt_value>', ';'],
                ['letter', 'identifier', '=', '<stmt_value>', ';']
            ],

            '<fixed_declaration>': [
                ['fixed', '<fixed_typed_decl>']
            ],

            '<fixed_typed_decl>': [
                ['num', 'identifier', '=', '<stmt_value>', ';'],
                ['decimal', 'identifier', '=', '<stmt_value>', ';'],
                ['bigdecimal', 'identifier', '=', '<stmt_value>', ';'],
                ['bool', 'identifier', '=', '<stmt_value>', ';'],
                ['text', 'identifier', '=', '<stmt_value>', ';'],
                ['letter', 'identifier', '=', '<stmt_value>', ';']
            ],

            '<list_declaration>': [
                ['list', '<list_typed_decl>']
            ],

            '<list_typed_decl>': [
                ['num', 'identifier', '=', '<val_list>', ';'],
                ['decimal', 'identifier', '=', '<val_list>', ';'],
                ['bigdecimal', 'identifier', '=', '<val_list>', ';'],
                ['bool', 'identifier', '=', '<val_list>', ';'],
                ['text', 'identifier', '=', '<val_list>', ';'],
                ['letter', 'identifier', '=', '<val_list>', ';']
            ],

            # List literals
            '<val_list>': [
                ['<val_list_1d>'],
                ['<val_list_2d>']
            ],

            '<val_list_1d>': [
                ['[', '<val_list_elems>', ']']
            ],

            '<val_list_elems>': [
                ['<arg_value>', '<val_list_tail>'],
                ['λ']
            ],

            '<val_list_tail>': [
                [',', '<arg_value>', '<val_list_tail>'],
                ['λ']
            ],

            '<val_list_2d>': [
                ['[', '<val_list_rows>', ']']
            ],

            '<val_list_rows>': [
                ['<val_list_1d>', '<val_list_rows_tail>'],
                ['λ']
            ],

            '<val_list_rows_tail>': [
                [',', '<val_list_1d>', '<val_list_rows_tail>'],
                ['λ']
            ],

            # STATEMENTS

            '<statements>': [
                ['<statement>', '<statements>'],
                ['λ']
            ],

            '<statement>': [
                ['<control_statement>'],
                ['<assignment_statement>'],
                ['<function_call_statement>'],
                ['<declaration>'],
                ['<io_statement>']
            ],

            # ASSIGNMENT STATEMENTS

            '<assignment_statement>': [
                ['<assignable>', '<assignment_tail>']
            ],

            '<assignment_tail>': [
                ['=', '<stmt_value>', ';'],
                ['+=', '<stmt_value>', ';'],
                ['-=', '<stmt_value>', ';'],
                ['*=', '<stmt_value>', ';'],
                ['/=', '<stmt_value>', ';'],
                ['//=', '<stmt_value>', ';'],
                ['%=', '<stmt_value>', ';'],
                ['**=', '<stmt_value>', ';'],
                ['++', ';'],
                ['--', ';']
            ],

            '<assignable>': [
                ['identifier', '<assignable_suffix>']
            ],

            '<assignable_suffix>': [
                ['[', '<index_value>', ']', '<assignable_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<assignable_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],

            # FUNCTION CALLS

            '<function_call_statement>': [
                ['<function_call>', ';']
            ],

            '<function_call>': [
                ['identifier', '(', '<arg_list>', ')']
            ],

            '<arg_list>': [
                ['<arg_value>', '<arg_list_tail>'],
                ['λ']
            ],

            '<arg_list_tail>': [
                [',', '<arg_value>', '<arg_list_tail>'],
                ['λ']
            ],

            # I/O STATEMENTS

            '<io_statement>': [
                ['show', '(', '<arg_list>', ')', ';'],
                ['display', '(', '<arg_list>', ')', ';'],
                ['read', '(', 'identifier', ')', ';']
            ],

            # CONTROL STATEMENTS

            '<control_statement>': [
                ['<check_structure>'],
                ['<select_statement>'],
                ['<iterative_statement>']
            ],

            # CHECK - uses <cond_value>
            '<check_structure>': [
                ['check', '(', '<cond_value>', ')',
                 '{', '<statements>', '}', '<otherwise_chain>']
            ],

            '<otherwise_chain>': [
                ['otherwisecheck', '(', '<cond_value>', ')',
                 '{', '<statements>', '}', '<otherwise_chain>'],
                ['otherwise', '{', '<statements>', '}'],
                ['λ']
            ],

            # SELECT - only IDENTIFIER allowed inside
            '<select_statement>': [
                ['select', '(', 'identifier', ')',
                 '{', '<option_blocks>', '<optional_fallback>', '}']
            ],

            '<option_blocks>': [
                ['<option_block>', '<option_blocks>'],
                ['λ']
            ],

            '<option_block>': [
                ['option', '<literal>', ':', '<option_statements>',
                    '<control_flow>', ';']
            ],

            '<option_statements>': [
                ['<statement>', '<option_statements>'],
                ['λ']
            ],

            '<control_flow>': [
                ['stop'],
                ['skip']
            ],

            '<optional_fallback>': [
                ['fallback', ':',  '<statements>'],
                ['λ']
            ],

            # LOOPS
            '<iterative_statement>': [
                ['<each_loop>'],
                ['<during_loop>']
            ],

            # EACH
            '<each_loop>': [
                ['each', 'identifier', 'from', '<from_primary>', 'to',

                    '<to_primary>', '<step_clause>', '{', '<statements>', '}']
            ],

            '<step_clause>': [
                ['step', '<step_primary>'],
                ['λ']
            ],

            # DURING - uses <cond_value>
            '<during_loop>': [
                ['during', '(', '<cond_value>', ')',
                 '{', '<statements>', '}']
            ],

            # LITERALS
            '<literal>': [
                ['num_lit'],
                ['decimal_lit'],
                ['string_lit'],
                ['char_lit'],
                ['Yes'],
                ['No']
            ],



            '<stmt_value>': [['<stmt_or>']],

            '<stmt_or>': [['<stmt_and>', '<stmt_or_tail>']],
            '<stmt_or_tail>': [
                ['||', '<stmt_and>', '<stmt_or_tail>'],
                ['λ']
            ],

            '<stmt_and>': [['<stmt_eq>', '<stmt_and_tail>']],
            '<stmt_and_tail>': [
                ['&&', '<stmt_eq>', '<stmt_and_tail>'],
                ['λ']
            ],

            '<stmt_eq>': [['<stmt_rel>', '<stmt_eq_tail>']],
            '<stmt_eq_tail>': [
                ['==', '<stmt_rel>', '<stmt_eq_tail>'],
                ['!=', '<stmt_rel>', '<stmt_eq_tail>'],
                ['λ']
            ],

            '<stmt_rel>': [['<stmt_add>', '<stmt_rel_tail>']],
            '<stmt_rel_tail>': [
                ['>', '<stmt_add>', '<stmt_rel_tail>'],
                ['<', '<stmt_add>', '<stmt_rel_tail>'],
                ['>=', '<stmt_add>', '<stmt_rel_tail>'],
                ['<=', '<stmt_add>', '<stmt_rel_tail>'],
                ['λ']
            ],

            '<stmt_add>': [['<stmt_mult>', '<stmt_add_tail>']],
            '<stmt_add_tail>': [
                ['+', '<stmt_mult>', '<stmt_add_tail>'],
                ['-', '<stmt_mult>', '<stmt_add_tail>'],
                ['λ']
            ],

            '<stmt_mult>': [['<stmt_exp>', '<stmt_mult_tail>']],
            '<stmt_mult_tail>': [
                ['*', '<stmt_exp>', '<stmt_mult_tail>'],
                ['/', '<stmt_exp>', '<stmt_mult_tail>'],
                ['//', '<stmt_exp>', '<stmt_mult_tail>'],
                ['%', '<stmt_exp>', '<stmt_mult_tail>'],
                ['λ']
            ],

            '<stmt_exp>': [['<stmt_unary>', '<stmt_exp_tail>']],
            '<stmt_exp_tail>': [
                ['**', '<stmt_exp>'],
                ['λ']
            ],

            '<stmt_unary>': [
                ['-', '<stmt_post>'],
                ['!', '<stmt_post>'],
                ['<stmt_post>']
            ],


            '<stmt_post>': [['<stmt_prim>']],

            '<stmt_prim>': [
                ['(', '<stmt_value>', ')'],
                ['<literal>'],
                ['identifier', '<stmt_id_suffix>'],
                ['<size_call>']
            ],

            '<stmt_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<stmt_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<stmt_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



            '<arg_value>': [['<arg_or>']],

            '<arg_or>': [['<arg_and>', '<arg_or_tail>']],
            '<arg_or_tail>': [
                ['||', '<arg_and>', '<arg_or_tail>'],
                ['λ']
            ],

            '<arg_and>': [['<arg_eq>', '<arg_and_tail>']],
            '<arg_and_tail>': [
                ['&&', '<arg_eq>', '<arg_and_tail>'],
                ['λ']
            ],

            '<arg_eq>': [['<arg_rel>', '<arg_eq_tail>']],
            '<arg_eq_tail>': [
                ['==', '<arg_rel>', '<arg_eq_tail>'],
                ['!=', '<arg_rel>', '<arg_eq_tail>'],
                ['λ']
            ],

            '<arg_rel>': [['<arg_add>', '<arg_rel_tail>']],
            '<arg_rel_tail>': [
                ['>', '<arg_add>', '<arg_rel_tail>'],
                ['<', '<arg_add>', '<arg_rel_tail>'],
                ['>=', '<arg_add>', '<arg_rel_tail>'],
                ['<=', '<arg_add>', '<arg_rel_tail>'],
                ['λ']
            ],

            '<arg_add>': [['<arg_mult>', '<arg_add_tail>']],
            '<arg_add_tail>': [
                ['+', '<arg_mult>', '<arg_add_tail>'],
                ['-', '<arg_mult>', '<arg_add_tail>'],
                ['λ']
            ],

            '<arg_mult>': [['<arg_exp>', '<arg_mult_tail>']],
            '<arg_mult_tail>': [
                ['*', '<arg_exp>', '<arg_mult_tail>'],
                ['/', '<arg_exp>', '<arg_mult_tail>'],
                ['//', '<arg_exp>', '<arg_mult_tail>'],
                ['%', '<arg_exp>', '<arg_mult_tail>'],
                ['λ']
            ],

            '<arg_exp>': [['<arg_unary>', '<arg_exp_tail>']],
            '<arg_exp_tail>': [
                ['**', '<arg_exp>'],
                ['λ']
            ],

            '<arg_unary>': [
                ['-', '<arg_post>'],
                ['!', '<arg_post>'],
                ['<arg_post>']
            ],

            '<arg_post>': [['<arg_prim>']],

            '<arg_prim>': [
                ['(', '<arg_value>', ')'],
                ['<literal>'],
                ['identifier', '<arg_id_suffix>'],
                ['<size_call>']
            ],

            '<arg_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<arg_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<arg_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



            '<cond_value>': [['<arg_value>']],



            '<index_value>': [['<index_add>']],

            '<index_add>': [['<index_mult>', '<index_add_tail>']],
            '<index_add_tail>': [
                ['+', '<index_mult>', '<index_add_tail>'],
                ['-', '<index_mult>', '<index_add_tail>'],
                ['λ']
            ],

            '<index_mult>': [['<index_exp>', '<index_mult_tail>']],
            '<index_mult_tail>': [
                ['*', '<index_exp>', '<index_mult_tail>'],
                ['/', '<index_exp>', '<index_mult_tail>'],
                ['//', '<index_exp>', '<index_mult_tail>'],
                ['%', '<index_exp>', '<index_mult_tail>'],
                ['λ']
            ],

            '<index_exp>': [['<index_unary>', '<index_exp_tail>']],
            '<index_exp_tail>': [
                ['**', '<index_exp>'],
                ['λ']
            ],

            '<index_unary>': [
                ['-', '<index_post>'],
                ['<index_post>']
            ],

            '<index_post>': [['<index_prim>']],

            '<index_prim>': [
                ['(', '<index_value>', ')'],
                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<index_id_suffix>'],
                ['<size_call>']
            ],

            '<index_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<index_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<index_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



            '<from_primary>': [
                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<from_id_suffix>'],

                ['<size_call>']
            ],

            '<from_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<from_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<from_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],


            '<to_primary>': [
                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<to_id_suffix>'],
                ['<size_call>']
            ],

            '<to_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<to_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<to_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



            '<step_primary>': [
                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<step_id_suffix>'],
                ['<size_call>']
            ],

            '<step_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<step_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<step_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



            '<size_call>': [
                ['size', '(', 'identifier', '<size_second_arg>', ')']
            ],

            '<size_second_arg>': [
                [',', 'num_lit'],
                ['λ']
            ],
        }

        self.non_terminals = set(self.productions.keys())
        self.terminals = self._extract_terminals()

    def _extract_terminals(self):
        """Extract all terminals from productions"""
        terminals = set()
        for nt, prods in self.productions.items():
            for prod in prods:
                for symbol in prod:
                    if symbol not in self.non_terminals and symbol != 'λ':
                        terminals.add(symbol)
        terminals.add('$')
        return terminals

    def _compute_first_sets(self):
        """Compute FIRST sets for all non-terminals"""
        self.first = {nt: set() for nt in self.non_terminals}

        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.productions[nt]:
                    old_size = len(self.first[nt])
                    first_of_prod = self._first_of_sequence(production)
                    self.first[nt].update(first_of_prod)
                    if len(self.first[nt]) > old_size:
                        changed = True

    def _first_of_sequence(self, sequence):
        """Compute FIRST of a sequence of symbols"""
        result = set()
        for symbol in sequence:
            if symbol == 'λ':
                result.add('λ')
                break
            elif symbol in self.terminals:
                result.add(symbol)
                break
            else:
                result.update(self.first[symbol] - {'λ'})
                if 'λ' not in self.first[symbol]:
                    break
        else:
            result.add('λ')
        return result

    def _compute_follow_sets(self):
        """Compute FOLLOW sets for all non-terminals"""
        self.follow = {nt: set() for nt in self.non_terminals}
        self.follow['<program>'].add('$')

        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.productions[nt]:
                    for i, symbol in enumerate(production):
                        if symbol in self.non_terminals:
                            old_size = len(self.follow[symbol])
                            rest = production[i+1:]
                            if rest:
                                first_of_rest = self._first_of_sequence(rest)
                                self.follow[symbol].update(
                                    first_of_rest - {'λ'})
                                if 'λ' in first_of_rest:
                                    self.follow[symbol].update(self.follow[nt])
                            else:
                                self.follow[symbol].update(self.follow[nt])
                            if len(self.follow[symbol]) > old_size:
                                changed = True

    def _build_parsing_table(self):
        """Build LL(1) parsing table"""
        self.table = {}
        self.conflicts = []

        for nt in self.non_terminals:
            for production in self.productions[nt]:
                first_of_prod = self._first_of_sequence(production)

                # Add entries for terminals in FIRST
                for terminal in first_of_prod - {'λ'}:
                    key = (nt, terminal)
                    if key in self.table:
                        self.conflicts.append({
                            'key': key,
                            'existing': self.table[key],
                            'new': production
                        })
                    self.table[key] = production

                # If λ in FIRST, add entries for FOLLOW
                if 'λ' in first_of_prod:
                    for terminal in self.follow[nt]:
                        key = (nt, terminal)
                        if key in self.table:
                            self.conflicts.append({
                                'key': key,
                                'existing': self.table[key],
                                'new': production
                            })
                        self.table[key] = production

    # ══════════════════════════════════════════════════════════════
    # ACTION REGISTRY — maps (NT, production_tuple) to action name
    # ══════════════════════════════════════════════════════════════

    def _build_action_registry(self):
        """Classify all productions into action categories."""
        self.production_actions = {}

        # Sets of terminals that carry semantic value (pushed onto sem_stack)
        self._semantic_terminals = {
            'identifier', 'num_lit', 'decimal_lit', 'string_lit', 'char_lit',
            'Yes', 'No',
            # Operators
            '+', '-', '*', '/', '//', '%', '**',
            '||', '&&', '==', '!=', '>', '<', '>=', '<=',
            '=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '++', '--',
            '!',
            # Type keywords (semantic value = the type itself)
            'num', 'decimal', 'bigdecimal', 'bool', 'text', 'letter', 'empty',
            # Keywords that carry semantic meaning
            'fixed', 'stop', 'skip',
        }

        # NTs that are simple pass-through (single NT child)
        pass_through_nts = {
            '<program>', '<stmt_value>', '<arg_value>', '<cond_value>',
            '<index_value>',
            '<stmt_post>', '<arg_post>', '<index_post>',
            '<control_statement>', '<iterative_statement>',
            '<declaration>',
            '<statement>',
        }

        # NTs for binary expression levels: <X> → <operand> <X_tail>
        # These need FOLD_TAIL action
        fold_tail_nts = {
            '<stmt_or>', '<stmt_and>', '<stmt_eq>', '<stmt_rel>',
            '<stmt_add>', '<stmt_mult>',
            '<arg_or>', '<arg_and>', '<arg_eq>', '<arg_rel>',
            '<arg_add>', '<arg_mult>',
            '<index_add>', '<index_mult>',
        }

        # NTs for binary tails: <X_tail> → op <operand> <X_tail> | λ
        build_tail_nts = {
            '<stmt_or_tail>', '<stmt_and_tail>', '<stmt_eq_tail>',
            '<stmt_rel_tail>', '<stmt_add_tail>', '<stmt_mult_tail>',
            '<arg_or_tail>', '<arg_and_tail>', '<arg_eq_tail>',
            '<arg_rel_tail>', '<arg_add_tail>', '<arg_mult_tail>',
            '<index_add_tail>', '<index_mult_tail>',
        }

        # NTs for exponent: <X_exp> → <X_unary> <X_exp_tail>
        fold_exp_nts = {
            '<stmt_exp>', '<arg_exp>', '<index_exp>',
        }

        # NTs for exponent tails: <X_exp_tail> → ** <X_exp> | λ
        build_exp_tail_nts = {
            '<stmt_exp_tail>', '<arg_exp_tail>', '<index_exp_tail>',
        }

        # List-accumulator NTs (recursive: item rest → prepend item to rest)
        list_accum_nts = {
            '<statements>', '<option_statements>',
            '<local_declarations>',
            '<group_body>', '<group_body_tail>',
            '<option_blocks>',
            '<val_list_rows>', '<val_list_rows_tail>',
        }

        # List-tail NTs (comma-separated: , item rest → prepend item to rest)
        list_tail_nts = {
            '<parameter_list_tail>', '<arg_list_tail>',
            '<val_list_tail>',
        }

        for nt, prods in self.productions.items():
            for prod in prods:
                key = (nt, tuple(prod))
                is_epsilon = prod == ['λ']

                # ── Epsilon productions ─────────────────────────
                if is_epsilon:
                    if nt in list_accum_nts or nt in list_tail_nts:
                        self.production_actions[key] = 'EPSILON_LIST'
                    elif nt in build_tail_nts or nt in build_exp_tail_nts:
                        self.production_actions[key] = 'EPSILON_TAIL'
                    else:
                        self.production_actions[key] = 'EPSILON'
                    continue

                # ── Pass-through: single NT child ───────────────
                if nt in pass_through_nts:
                    self.production_actions[key] = 'PASS_THROUGH'
                    continue

                # ── Binary fold: <level> → <operand> <tail> ────
                if nt in fold_tail_nts:
                    self.production_actions[key] = 'FOLD_TAIL'
                    continue

                # ── Binary tail: op <operand> <tail> ────────────
                if nt in build_tail_nts:
                    self.production_actions[key] = 'BUILD_TAIL'
                    continue

                # ── Exponent fold: <exp> → <unary> <exp_tail> ──
                if nt in fold_exp_nts:
                    self.production_actions[key] = 'FOLD_EXP'
                    continue

                # ── Exponent tail: ** <exp> | λ ─────────────────
                if nt in build_exp_tail_nts:
                    self.production_actions[key] = 'BUILD_EXP_TAIL'
                    continue

                # ── List accumulators ───────────────────────────
                if nt in list_accum_nts:
                    self.production_actions[key] = 'COLLECT_LIST'
                    continue

                # ── List tails (comma-separated) ────────────────
                if nt in list_tail_nts:
                    self.production_actions[key] = 'COLLECT_LIST_TAIL'
                    continue

                # ── Everything else: CUSTOM per NT ──────────────
                self.production_actions[key] = f'CUSTOM_{nt}'

    # ══════════════════════════════════════════════════════════════
    # TOKEN LOCATION HELPER
    # ══════════════════════════════════════════════════════════════

    def _token_loc(self, token):
        """Extract (line, col) from a token."""
        if token and hasattr(token, 'pos_start') and token.pos_start:
            return token.pos_start.ln + 1, token.pos_start.col + 1
        return 0, 0

    # ══════════════════════════════════════════════════════════════
    # MODIFIED PARSE LOOP
    # ══════════════════════════════════════════════════════════════

    def parse(self, verbose=False):
        """Table-driven LL(1) parsing algorithm with AST construction."""
        if verbose:
            print("\n" + "="*80)
            print("TABLE-DRIVEN LL(1) PARSER")
            print("="*80)

        step = 1
        while self.stack:
            top = self.stack[-1]

            if self.current_token is None:
                current = '$'
            elif hasattr(self.current_token, 'type'):
                current = self.current_token.type
            else:
                current = str(self.current_token)

            if verbose:
                print(f"Step {step}: Stack top={top}, Input={current}")

            # ── Action marker processing ─────────────────────
            if isinstance(top, tuple) and len(top) >= 4 and top[0] == '@POST':
                self.stack.pop()
                _, nt, action, saved_depth = top
                self._execute_action(nt, action, saved_depth)
                continue

            # Case 1: Top is $
            if top == '$':
                if verbose:
                    print("="*80)
                    print("PARSING SUCCESSFUL!")
                    print("="*80)
                # Return the AST (should be one Program node on sem_stack)
                if self.sem_stack:
                    return self.sem_stack[-1]
                return True

            # Case 2: Top is terminal
            elif top in self.terminals:
                if top == current:
                    if verbose:
                        print(f"  MATCH '{top}'")
                    self.stack.pop()

                    # Push semantic terminal onto sem_stack
                    if top in self._semantic_terminals:
                        self.sem_stack.append(self.current_token)

                    self.advance()
                    self.skipped_expected = set()
                else:
                    self._error(f"Unexpected: '{current}'\nExpected: '{top}'")

            # Case 3: Top is λ
            elif top == 'λ':
                if verbose:
                    print(f"  POP λ")
                self.stack.pop()

            # Case 4: Top is non-terminal
            elif top in self.non_terminals:
                production = None

                # Special case: Statement-level ambiguity requires 2-token lookahead
                if top == '<statement>' and current == 'identifier':
                    next_token = None
                    if self.pos + 1 < len(self.tokens):
                        next_tok_obj = self.tokens[self.pos + 1]
                        if hasattr(next_tok_obj, 'type'):
                            next_token = next_tok_obj.type
                        else:
                            next_token = str(next_tok_obj)
                    else:
                        next_token = '$'

                    if next_token in ['=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '++', '--', '[', '.']:
                        production = ['<assignment_statement>']
                    elif next_token == '(':
                        production = ['<function_call_statement>']
                    elif next_token == 'identifier':
                        production = ['<declaration>']
                    else:
                        all_valid_tokens = set()
                        all_valid_tokens.update(
                            ['=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '++', '--', '[', '.'])
                        all_valid_tokens.add('(')
                        all_valid_tokens.add('identifier')
                        exp_str = ', '.join(
                            f"'{e}'" for e in sorted(all_valid_tokens))
                        self._error(
                            f"Unexpected: '{next_token}'\nExpected: {exp_str}")

                    if verbose:
                        prod_str = ' '.join(production)
                        print(
                            f"  EXPAND {top} → {prod_str} (2-token lookahead, next={next_token})")

                # Special case: List 1D vs 2D disambiguation
                elif top == '<val_list>' and current == '[':
                    next_token = None
                    if self.pos + 1 < len(self.tokens):
                        next_tok_obj = self.tokens[self.pos + 1]
                        if hasattr(next_tok_obj, 'type'):
                            next_token = next_tok_obj.type
                        else:
                            next_token = str(next_tok_obj)
                    else:
                        next_token = '$'

                    if next_token == '[':
                        production = ['<val_list_2d>']
                    else:
                        production = ['<val_list_1d>']

                    if verbose:
                        prod_str = ' '.join(production)
                        print(
                            f"  EXPAND {top} → {prod_str} (2-token lookahead for list, next={next_token})")

                else:
                    # Normal LL(1) table lookup
                    key = (top, current)
                    if key in self.table:
                        production = self.table[key]
                        if verbose:
                            prod_str = ' '.join(production)
                            print(f"  EXPAND {top} → {prod_str}")

                        # Track skipped alternatives when taking λ path
                        if production == ['λ']:
                            other_tokens = set(
                                term for (nt_k, term) in self.table.keys() if nt_k == top and term != current)
                            self.skipped_expected.update(other_tokens)

                    else:
                        expected = set(
                            term for (nt_k, term) in self.table.keys() if nt_k == top)
                        expected.update(self.skipped_expected)
                        expected = sorted(expected)
                        if expected:
                            exp_str = ', '.join(f"'{e}'" for e in expected)
                            self._error(
                                f"Unexpected: '{current}'\nExpected: {exp_str}")
                        else:
                            self._error(
                                f"Unexpected: '{current}'\nNo valid continuation for {top}")

                # ── Expand the production onto the parse stack ──
                if production is not None:
                    action_key = (top, tuple(production))
                    action = self.production_actions.get(action_key, 'PASS_THROUGH')

                    self.stack.pop()

                    if production == ['λ']:
                        # Epsilon: handle immediately
                        self._execute_action(top, action, len(self.sem_stack))
                    else:
                        # Push post-action marker BEFORE reversed production
                        # (so it fires AFTER all children are processed)
                        saved_depth = len(self.sem_stack)
                        self.stack.append(('@POST', top, action, saved_depth))
                        for symbol in reversed(production):
                            self.stack.append(symbol)

                    self.derivations.append((top, production))

            else:
                self._error(
                    f"Internal parser error: Unknown symbol '{top}' on stack")

            step += 1
            if verbose:
                print()

            if step > 10000:
                self._error(
                    "Parser exceeded maximum steps (possible infinite loop)")

        # Stack empty - success
        if self.sem_stack:
            return self.sem_stack[-1]
        return True

    # ══════════════════════════════════════════════════════════════
    # ACTION EXECUTION
    # ══════════════════════════════════════════════════════════════

    def _execute_action(self, nt, action, saved_depth):
        """Execute a semantic action after a production's children are processed."""

        if action == 'PASS_THROUGH':
            # Child's result is already on sem_stack — nothing to do
            return

        if action == 'EPSILON':
            self.sem_stack.append(None)
            return

        if action == 'EPSILON_LIST':
            self.sem_stack.append([])
            return

        if action == 'EPSILON_TAIL':
            self.sem_stack.append(_TAIL_EMPTY)
            return

        if action == 'FOLD_TAIL':
            # sem_stack has: ... left_operand tail_result
            tail = self.sem_stack.pop()
            left = self.sem_stack.pop()
            if tail is _TAIL_EMPTY or tail is None:
                self.sem_stack.append(left)
            else:
                # tail is a list of (op_token, right_expr) pairs
                result = left
                for op_tok, right in tail:
                    op_str = op_tok.type if hasattr(op_tok, 'type') else str(op_tok)
                    ln, col = self._token_loc(op_tok)
                    result = BinaryOp(op=op_str, left=result, right=right, line=ln, col=col)
                self.sem_stack.append(result)
            return

        if action == 'BUILD_TAIL':
            # sem_stack has: ... op_token operand tail_result
            tail = self.sem_stack.pop()
            operand = self.sem_stack.pop()
            op_tok = self.sem_stack.pop()
            pair = (op_tok, operand)
            if tail is _TAIL_EMPTY or tail is None:
                self.sem_stack.append([pair])
            else:
                self.sem_stack.append([pair] + tail)
            return

        if action == 'FOLD_EXP':
            # sem_stack has: ... base exp_tail_result
            tail = self.sem_stack.pop()
            base = self.sem_stack.pop()
            if tail is _TAIL_EMPTY or tail is None:
                self.sem_stack.append(base)
            else:
                op_tok, right = tail
                op_str = op_tok.type if hasattr(op_tok, 'type') else str(op_tok)
                ln, col = self._token_loc(op_tok)
                self.sem_stack.append(BinaryOp(op=op_str, left=base, right=right, line=ln, col=col))
            return

        if action == 'BUILD_EXP_TAIL':
            # sem_stack has: ... ** <exp_result>
            right = self.sem_stack.pop()
            op_tok = self.sem_stack.pop()
            self.sem_stack.append((op_tok, right))
            return

        if action == 'COLLECT_LIST':
            # sem_stack has: ... item rest_list
            rest = self.sem_stack.pop()
            item = self.sem_stack.pop()
            if not isinstance(rest, list):
                rest = []
            self.sem_stack.append([item] + rest)
            return

        if action == 'COLLECT_LIST_TAIL':
            # sem_stack has: ... item rest_list  (comma was a structural terminal, not pushed)
            rest = self.sem_stack.pop()
            item = self.sem_stack.pop()
            if not isinstance(rest, list):
                rest = []
            self.sem_stack.append([item] + rest)
            return

        # ── CUSTOM actions ──────────────────────────────────
        handler = self._custom_actions.get(action)
        if handler:
            handler(self, saved_depth)
        # else: no action needed (e.g., for simple forwarding NTs)

    # ══════════════════════════════════════════════════════════════
    # CUSTOM ACTION HANDLERS
    # ══════════════════════════════════════════════════════════════

    # Use a class-level dict to map action names to handler methods.
    # Each handler takes (self, saved_depth) and manipulates self.sem_stack.

    def _action_datatype(self, saved_depth):
        # sem_stack has: ... type_keyword_token
        tok = self.sem_stack.pop()
        type_str = tok.type if hasattr(tok, 'type') else str(tok)
        self.sem_stack.append(type_str)

    def _action_return_type(self, saved_depth):
        # Same as datatype
        tok = self.sem_stack.pop()
        type_str = tok.type if hasattr(tok, 'type') else str(tok)
        self.sem_stack.append(type_str)

    def _action_literal(self, saved_depth):
        # sem_stack has: ... literal_token
        tok = self.sem_stack.pop()
        ln, col = self._token_loc(tok)
        val = tok.value if hasattr(tok, 'value') and tok.value is not None else ''
        self.sem_stack.append(Literal(token_type=tok.type, value=str(val), line=ln, col=col))

    def _action_control_flow(self, saved_depth):
        # sem_stack has: ... stop/skip_token
        tok = self.sem_stack.pop()
        self.sem_stack.append(tok.type if hasattr(tok, 'type') else str(tok))

    def _action_group_member(self, saved_depth):
        # sem_stack has: ... datatype_str identifier_token
        id_tok = self.sem_stack.pop()
        dtype = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        self.sem_stack.append(GroupMember(datatype=dtype, name=name, line=ln, col=col))

    def _action_group_definitions(self, saved_depth):
        # sem_stack has: ... identifier_token group_body_list
        body_list = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        if not isinstance(body_list, list):
            body_list = []
        self.sem_stack.append(GroupDef(name=name, members=body_list, line=ln, col=col))

    def _action_global_modifier(self, saved_depth):
        # sem_stack has: ... fixed_token
        tok = self.sem_stack.pop()
        self.sem_stack.append(True)

    def _action_global_modifier_epsilon(self, saved_depth):
        self.sem_stack.append(False)

    def _action_global_typed_decl(self, saved_depth):
        # sem_stack has: ... type_token identifier_token value_expr
        value = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        type_tok = self.sem_stack.pop()
        dtype = type_tok.type if hasattr(type_tok, 'type') else str(type_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        ln, col = self._token_loc(id_tok)
        # Push (dtype, name, value, line, col) — to be assembled by parent
        self.sem_stack.append((dtype, name, value, ln, col))

    def _action_global_variable_declarations(self, saved_depth):
        # sem_stack has: ... is_fixed typed_decl_tuple
        typed_decl = self.sem_stack.pop()
        is_fixed = self.sem_stack.pop()
        dtype, name, value, ln, col = typed_decl
        self.sem_stack.append(
            WorldwideDecl(is_fixed=is_fixed, datatype=dtype, name=name, value=value, line=ln, col=col)
        )

    def _action_parameter(self, saved_depth):
        # sem_stack has: ... datatype_str identifier_token
        id_tok = self.sem_stack.pop()
        dtype = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        self.sem_stack.append(Parameter(datatype=dtype, name=name, line=ln, col=col))

    def _action_parameter_list(self, saved_depth):
        # sem_stack has: ... first_param tail_list
        tail = self.sem_stack.pop()
        first = self.sem_stack.pop()
        if not isinstance(tail, list):
            tail = []
        self.sem_stack.append([first] + tail)

    def _action_parameter_list_epsilon(self, saved_depth):
        self.sem_stack.append([])

    def _action_return_tail_value(self, saved_depth):
        # sem_stack has: ... expr
        # Value return — expr is already on stack
        expr = self.sem_stack.pop()
        self.sem_stack.append(ReturnStmt(value=expr))

    def _action_return_tail_empty(self, saved_depth):
        # give ;  — no value
        self.sem_stack.append(ReturnStmt(value=None))

    def _action_optional_return(self, saved_depth):
        # sem_stack has: ... return_stmt_node
        # The return_tail already built a ReturnStmt — pass through
        pass

    def _action_optional_return_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_function_definitions(self, saved_depth):
        # sem_stack has: ... return_type_str identifier_token param_list local_decls_list stmts_list optional_return
        opt_return = self.sem_stack.pop()
        stmts = self.sem_stack.pop()
        local_decls = self.sem_stack.pop()
        params = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        rtype = self.sem_stack.pop()

        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        ln, col = self._token_loc(id_tok)

        if not isinstance(stmts, list):
            stmts = []
        if not isinstance(local_decls, list):
            local_decls = []
        if not isinstance(params, list):
            params = []

        self.sem_stack.append(
            FuncDef(return_type=rtype, name=name, params=params,
                    local_decls=local_decls, body=stmts,
                    return_stmt=opt_return, line=ln, col=col)
        )

    def _action_start_block(self, saved_depth):
        # sem_stack has: ... stmts_list
        stmts = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []
        self.sem_stack.append(stmts)

    def _action_group_part_recursive(self, saved_depth):
        # sem_stack has: ... group_def program_node
        program = self.sem_stack.pop()
        group = self.sem_stack.pop()
        if isinstance(program, Program):
            program.groups.insert(0, group)
            self.sem_stack.append(program)
        else:
            self.sem_stack.append(Program(groups=[group]))

    def _action_group_part_base(self, saved_depth):
        # sem_stack has: ... worldwide_result (which is already a Program)
        pass

    def _action_worldwide_part_recursive(self, saved_depth):
        # sem_stack has: ... worldwide_decl program_node
        program = self.sem_stack.pop()
        ww_decl = self.sem_stack.pop()
        if isinstance(program, Program):
            program.worldwide_decls.insert(0, ww_decl)
            self.sem_stack.append(program)
        else:
            self.sem_stack.append(Program(worldwide_decls=[ww_decl]))

    def _action_worldwide_part_base(self, saved_depth):
        # sem_stack has: ... define_result (which is already a Program)
        pass

    def _action_define_part_recursive(self, saved_depth):
        # sem_stack has: ... func_def program_node
        program = self.sem_stack.pop()
        func_def = self.sem_stack.pop()
        if isinstance(program, Program):
            program.functions.insert(0, func_def)
            self.sem_stack.append(program)
        else:
            self.sem_stack.append(Program(functions=[func_def]))

    def _action_define_part_base(self, saved_depth):
        # sem_stack has: ... start_body_list
        start_body = self.sem_stack.pop()
        if not isinstance(start_body, list):
            start_body = []
        self.sem_stack.append(Program(start_body=start_body))

    def _action_local_declaration_group_typed(self, saved_depth):
        # GroupType varName ;
        # sem_stack has: ... group_type_identifier_token var_name_identifier_token
        name_tok = self.sem_stack.pop()
        type_tok = self.sem_stack.pop()
        ln, col = self._token_loc(name_tok)
        group_type = type_tok.value if hasattr(type_tok, 'value') else str(type_tok)
        vname = name_tok.value if hasattr(name_tok, 'value') else str(name_tok)
        self.sem_stack.append(
            VarDecl(datatype=group_type, name=vname, is_group_typed=True, line=ln, col=col)
        )

    def _action_local_declaration_typed(self, saved_depth):
        # type identifier = expr ;
        # sem_stack has: ... type_token identifier_token expr
        expr = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        type_tok = self.sem_stack.pop()
        dtype = type_tok.type if hasattr(type_tok, 'type') else str(type_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        ln, col = self._token_loc(id_tok)
        self.sem_stack.append(
            VarDecl(datatype=dtype, name=name, value=expr, line=ln, col=col)
        )

    def _action_fixed_typed_decl(self, saved_depth):
        # type identifier = expr ;
        # sem_stack has: ... type_token identifier_token expr
        expr = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        type_tok = self.sem_stack.pop()
        dtype = type_tok.type if hasattr(type_tok, 'type') else str(type_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        ln, col = self._token_loc(id_tok)
        self.sem_stack.append(
            FixedDecl(datatype=dtype, name=name, value=expr, line=ln, col=col)
        )

    def _action_fixed_declaration(self, saved_depth):
        # sem_stack has: ... fixed_token fixed_decl_node
        decl = self.sem_stack.pop()
        _fixed_tok = self.sem_stack.pop()  # discard 'fixed' token
        self.sem_stack.append(decl)

    def _action_list_typed_decl(self, saved_depth):
        # type identifier = val_list ;
        # sem_stack has: ... type_token identifier_token val_list_node
        val_list = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        type_tok = self.sem_stack.pop()
        dtype = type_tok.type if hasattr(type_tok, 'type') else str(type_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        ln, col = self._token_loc(id_tok)
        self.sem_stack.append(
            ListDecl(datatype=dtype, name=name, value=val_list, line=ln, col=col)
        )

    def _action_list_declaration(self, saved_depth):
        # sem_stack has: ... list_decl_node (list keyword was structural)
        pass

    def _action_val_list_1d(self, saved_depth):
        # sem_stack has: ... elems_list_or_node
        elems = self.sem_stack.pop()
        if not isinstance(elems, list):
            elems = [] if elems is None else [elems]
        self.sem_stack.append(ListLiteral1D(elements=elems))

    def _action_val_list_elems(self, saved_depth):
        # sem_stack has: ... first_elem tail_list
        tail = self.sem_stack.pop()
        first = self.sem_stack.pop()
        if not isinstance(tail, list):
            tail = []
        self.sem_stack.append([first] + tail)

    def _action_val_list_2d(self, saved_depth):
        # sem_stack has: ... rows_list
        rows = self.sem_stack.pop()
        if not isinstance(rows, list):
            rows = []
        self.sem_stack.append(ListLiteral2D(rows=rows))

    def _action_assignable(self, saved_depth):
        # sem_stack has: ... identifier_token suffix_result
        suffix = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)

        if suffix is None:
            # Plain variable
            self.sem_stack.append(Identifier(name=name, line=ln, col=col))
        elif isinstance(suffix, ListAccess):
            suffix.name = name
            suffix.line = ln
            suffix.col = col
            self.sem_stack.append(suffix)
        elif isinstance(suffix, MemberAccess):
            suffix.object_name = name
            suffix.line = ln
            suffix.col = col
            self.sem_stack.append(suffix)
        else:
            self.sem_stack.append(suffix)

    def _action_assignable_suffix_index(self, saved_depth):
        # sem_stack has: ... (id_tok is below us) index_expr assignable_2d_result
        # Do NOT pop id_tok — _action_assignable will handle it.
        a2d = self.sem_stack.pop()
        idx1 = self.sem_stack.pop()
        idx2 = a2d if a2d is not None else None
        self.sem_stack.append(ListAccess(index1=idx1, index2=idx2))

    def _action_assignable_suffix_member(self, saved_depth):
        # sem_stack has: ... (id_tok is below us) member_identifier_token
        # Do NOT pop id_tok — _action_assignable will handle it.
        member_tok = self.sem_stack.pop()
        member = member_tok.value if hasattr(member_tok, 'value') else str(member_tok)
        self.sem_stack.append(MemberAccess(member=member))

    def _action_assignable_suffix_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_assignable_2d_index(self, saved_depth):
        # sem_stack has: ... index_expr
        # Just leave the index on the stack — parent will use it
        pass

    def _action_assignable_2d_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_assignment_statement(self, saved_depth):
        # sem_stack has: ... target_expr assignment_tail_result
        tail = self.sem_stack.pop()
        target = self.sem_stack.pop()
        # tail is already a Statement node
        if isinstance(tail, (Assignment, CompoundAssign, Increment, Decrement)):
            tail.target = target
            if hasattr(target, 'line'):
                tail.line = target.line
                tail.col = target.col
        self.sem_stack.append(tail)

    def _action_assignment_tail_eq(self, saved_depth):
        # = expr ;  ('=' is not a semantic terminal, not on sem_stack)
        # sem_stack has: ... expr
        expr = self.sem_stack.pop()
        self.sem_stack.append(Assignment(value=expr))

    def _action_assignment_tail_compound(self, saved_depth):
        # op= expr ;
        # sem_stack has: ... op_token expr
        expr = self.sem_stack.pop()
        op_tok = self.sem_stack.pop()
        op = op_tok.type if hasattr(op_tok, 'type') else str(op_tok)
        self.sem_stack.append(CompoundAssign(op=op, value=expr))

    def _action_assignment_tail_increment(self, saved_depth):
        # ++ ;
        # sem_stack has: ... ++_token
        _tok = self.sem_stack.pop()
        self.sem_stack.append(Increment())

    def _action_assignment_tail_decrement(self, saved_depth):
        # -- ;
        # sem_stack has: ... --_token
        _tok = self.sem_stack.pop()
        self.sem_stack.append(Decrement())

    def _action_function_call(self, saved_depth):
        # identifier ( arg_list )
        # sem_stack has: ... identifier_token arg_list
        args = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        if not isinstance(args, list):
            args = []
        self.sem_stack.append(FuncCall(name=name, args=args, line=ln, col=col))

    def _action_function_call_statement(self, saved_depth):
        # <function_call> ;
        # sem_stack has: ... func_call_expr
        call = self.sem_stack.pop()
        ln = call.line if hasattr(call, 'line') else 0
        col = call.col if hasattr(call, 'col') else 0
        self.sem_stack.append(FuncCallStmt(call=call, line=ln, col=col))

    def _action_arg_list(self, saved_depth):
        # sem_stack has: ... first_arg tail_list
        tail = self.sem_stack.pop()
        first = self.sem_stack.pop()
        if not isinstance(tail, list):
            tail = []
        self.sem_stack.append([first] + tail)

    def _action_arg_list_epsilon(self, saved_depth):
        self.sem_stack.append([])

    def _action_io_show(self, saved_depth):
        # show ( arg_list ) ;
        # sem_stack has: ... arg_list
        args = self.sem_stack.pop()
        if not isinstance(args, list):
            args = []
        self.sem_stack.append(ShowStmt(args=args))

    def _action_io_display(self, saved_depth):
        # display ( arg_list ) ;
        # sem_stack has: ... arg_list
        args = self.sem_stack.pop()
        if not isinstance(args, list):
            args = []
        self.sem_stack.append(DisplayStmt(args=args))

    def _action_io_read(self, saved_depth):
        # read ( identifier ) ;
        # sem_stack has: ... identifier_token
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        self.sem_stack.append(ReadStmt(variable=name, line=ln, col=col))

    def _action_check_structure(self, saved_depth):
        # check ( cond ) { stmts } otherwise_chain
        # sem_stack has: ... cond stmts otherwise_chain_result
        chain = self.sem_stack.pop()
        stmts = self.sem_stack.pop()
        cond = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []

        elif_branches = []
        else_body = None
        if isinstance(chain, list):
            for item in chain:
                if isinstance(item, ElifBranch):
                    elif_branches.append(item)
                elif isinstance(item, list):
                    else_body = item

        ln = cond.line if hasattr(cond, 'line') else 0
        col = cond.col if hasattr(cond, 'col') else 0
        self.sem_stack.append(
            IfChain(condition=cond, body=stmts, elif_branches=elif_branches,
                    else_body=else_body, line=ln, col=col)
        )

    def _action_otherwise_chain_elif(self, saved_depth):
        # otherwisecheck ( cond ) { stmts } otherwise_chain
        # sem_stack has: ... cond stmts rest_chain
        rest = self.sem_stack.pop()
        stmts = self.sem_stack.pop()
        cond = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []
        ln = cond.line if hasattr(cond, 'line') else 0
        col = cond.col if hasattr(cond, 'col') else 0
        branch = ElifBranch(condition=cond, body=stmts, line=ln, col=col)
        if isinstance(rest, list):
            self.sem_stack.append([branch] + rest)
        else:
            self.sem_stack.append([branch])

    def _action_otherwise_chain_else(self, saved_depth):
        # otherwise { stmts }
        # sem_stack has: ... stmts
        stmts = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []
        self.sem_stack.append([stmts])  # Wrap in list so parent can distinguish

    def _action_otherwise_chain_epsilon(self, saved_depth):
        self.sem_stack.append([])

    def _action_select_statement(self, saved_depth):
        # select ( identifier ) { option_blocks optional_fallback }
        # sem_stack has: ... identifier_token option_blocks_list fallback_or_none
        fallback = self.sem_stack.pop()
        options = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        if not isinstance(options, list):
            options = []
        fb = fallback if isinstance(fallback, list) else None
        self.sem_stack.append(
            SelectStmt(variable=name, options=options, fallback=fb, line=ln, col=col)
        )

    def _action_option_block(self, saved_depth):
        # option <literal> : <option_statements> <control_flow> ;
        # sem_stack has: ... literal stmts control_flow_str
        cf = self.sem_stack.pop()
        stmts = self.sem_stack.pop()
        lit = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []
        cf_str = cf if isinstance(cf, str) else 'stop'
        ln = lit.line if hasattr(lit, 'line') else 0
        col = lit.col if hasattr(lit, 'col') else 0
        self.sem_stack.append(
            OptionBlock(value=lit, body=stmts, control_flow=cf_str, line=ln, col=col)
        )

    def _action_optional_fallback(self, saved_depth):
        # fallback : stmts
        # sem_stack has: ... stmts
        stmts = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []
        self.sem_stack.append(stmts)

    def _action_optional_fallback_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_each_loop(self, saved_depth):
        # each identifier from <from_primary> to <to_primary> <step_clause> { <statements> }
        # sem_stack has: ... identifier_token from_expr to_expr step_or_none stmts
        stmts = self.sem_stack.pop()
        step = self.sem_stack.pop()
        to_expr = self.sem_stack.pop()
        from_expr = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        if not isinstance(stmts, list):
            stmts = []
        self.sem_stack.append(
            EachLoop(variable=name, from_expr=from_expr, to_expr=to_expr,
                     step_expr=step, body=stmts, line=ln, col=col)
        )

    def _action_step_clause(self, saved_depth):
        # step <step_primary>
        # sem_stack has: ... step_expr
        # Just leave it — the step expression is already there
        pass

    def _action_step_clause_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_during_loop(self, saved_depth):
        # during ( cond ) { stmts }
        # sem_stack has: ... cond stmts
        stmts = self.sem_stack.pop()
        cond = self.sem_stack.pop()
        if not isinstance(stmts, list):
            stmts = []
        ln = cond.line if hasattr(cond, 'line') else 0
        col = cond.col if hasattr(cond, 'col') else 0
        self.sem_stack.append(
            DuringLoop(condition=cond, body=stmts, line=ln, col=col)
        )

    def _action_unary_neg(self, saved_depth):
        # - <post>
        # sem_stack has: ... minus_token operand
        operand = self.sem_stack.pop()
        op_tok = self.sem_stack.pop()
        ln, col = self._token_loc(op_tok)
        self.sem_stack.append(UnaryOp(op='-', operand=operand, line=ln, col=col))

    def _action_unary_not(self, saved_depth):
        # ! <post>
        # sem_stack has: ... bang_token operand
        operand = self.sem_stack.pop()
        op_tok = self.sem_stack.pop()
        ln, col = self._token_loc(op_tok)
        self.sem_stack.append(UnaryOp(op='!', operand=operand, line=ln, col=col))

    def _action_unary_passthrough(self, saved_depth):
        # <post> — just pass through
        pass

    def _action_prim_paren(self, saved_depth):
        # ( expr ) — expr is already on the stack, nothing to do
        pass

    def _action_prim_identifier(self, saved_depth):
        # identifier <id_suffix>
        # sem_stack has: ... id_token suffix_result
        suffix = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)

        if suffix is None:
            # Plain identifier
            self.sem_stack.append(Identifier(name=name, line=ln, col=col))
        elif isinstance(suffix, FuncCall):
            suffix.name = name
            suffix.line = ln
            suffix.col = col
            self.sem_stack.append(suffix)
        elif isinstance(suffix, ListAccess):
            suffix.name = name
            suffix.line = ln
            suffix.col = col
            self.sem_stack.append(suffix)
        elif isinstance(suffix, MemberAccess):
            suffix.object_name = name
            suffix.line = ln
            suffix.col = col
            self.sem_stack.append(suffix)
        else:
            self.sem_stack.append(Identifier(name=name, line=ln, col=col))

    def _action_id_suffix_call(self, saved_depth):
        # ( arg_list )
        # sem_stack has: ... arg_list
        args = self.sem_stack.pop()
        if not isinstance(args, list):
            args = []
        self.sem_stack.append(FuncCall(args=args))

    def _action_id_suffix_index(self, saved_depth):
        # [ index ] <var_2d>
        # sem_stack has: ... index_expr var_2d_result
        var_2d = self.sem_stack.pop()
        idx1 = self.sem_stack.pop()
        idx2 = var_2d if var_2d is not None else None
        self.sem_stack.append(ListAccess(index1=idx1, index2=idx2))

    def _action_id_suffix_member(self, saved_depth):
        # . identifier
        # sem_stack has: ... member_id_token
        member_tok = self.sem_stack.pop()
        member = member_tok.value if hasattr(member_tok, 'value') else str(member_tok)
        self.sem_stack.append(MemberAccess(member=member))

    def _action_id_suffix_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_var_2d_index(self, saved_depth):
        # [ index ]
        # sem_stack has: ... index_expr
        # Just leave it — it's the index2
        pass

    def _action_var_2d_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_size_call(self, saved_depth):
        # size ( identifier <size_second_arg> )
        # sem_stack has: ... identifier_token second_arg_or_none
        second = self.sem_stack.pop()
        id_tok = self.sem_stack.pop()
        ln, col = self._token_loc(id_tok)
        name = id_tok.value if hasattr(id_tok, 'value') else str(id_tok)
        dim = None
        if second is not None and hasattr(second, 'value'):
            dim = str(second.value)
        elif second is not None and isinstance(second, str):
            dim = second
        self.sem_stack.append(SizeCall(list_name=name, dimension=dim, line=ln, col=col))

    def _action_size_second_arg(self, saved_depth):
        # , num_lit
        # sem_stack has: ... num_lit_token
        # Leave the token (it will be consumed by _action_size_call)
        pass

    def _action_size_second_arg_epsilon(self, saved_depth):
        self.sem_stack.append(None)

    def _action_index_prim_num(self, saved_depth):
        # num_lit in index context
        tok = self.sem_stack.pop()
        ln, col = self._token_loc(tok)
        val = tok.value if hasattr(tok, 'value') and tok.value is not None else ''
        self.sem_stack.append(Literal(token_type='num_lit', value=str(val), line=ln, col=col))

    def _action_index_prim_decimal(self, saved_depth):
        # decimal_lit in index context
        tok = self.sem_stack.pop()
        ln, col = self._token_loc(tok)
        val = tok.value if hasattr(tok, 'value') and tok.value is not None else ''
        self.sem_stack.append(Literal(token_type='decimal_lit', value=str(val), line=ln, col=col))

    def _action_index_unary_neg(self, saved_depth):
        # - <index_post>
        operand = self.sem_stack.pop()
        op_tok = self.sem_stack.pop()
        ln, col = self._token_loc(op_tok)
        self.sem_stack.append(UnaryOp(op='-', operand=operand, line=ln, col=col))

    def _action_index_unary_passthrough(self, saved_depth):
        pass

    def _action_from_primary_num(self, saved_depth):
        tok = self.sem_stack.pop()
        ln, col = self._token_loc(tok)
        val = tok.value if hasattr(tok, 'value') and tok.value is not None else ''
        self.sem_stack.append(Literal(token_type='num_lit', value=str(val), line=ln, col=col))

    def _action_from_primary_decimal(self, saved_depth):
        tok = self.sem_stack.pop()
        ln, col = self._token_loc(tok)
        val = tok.value if hasattr(tok, 'value') and tok.value is not None else ''
        self.sem_stack.append(Literal(token_type='decimal_lit', value=str(val), line=ln, col=col))

    def _action_range_primary_id(self, saved_depth):
        # identifier <id_suffix>
        # Same as _action_prim_identifier
        self._action_prim_identifier(saved_depth)

    # ══════════════════════════════════════════════════════════════
    # CUSTOM ACTION DISPATCH TABLE
    # ══════════════════════════════════════════════════════════════

    _custom_actions = {}

    def _register_custom_actions(self):
        """Build the custom action dispatch table based on specific productions."""
        # This is called once. We map action string → handler.
        # Since _build_action_registry assigns 'CUSTOM_<nt>' for complex NTs,
        # we need to register each one.
        pass

    # Override _build_action_registry to assign specific custom action names
    # to specific productions (not just 'CUSTOM_<nt>' for all productions of an NT)
    def _build_action_registry(self):
        """Classify all productions into action categories with specific custom actions."""
        self.production_actions = {}

        self._semantic_terminals = {
            'identifier', 'num_lit', 'decimal_lit', 'string_lit', 'char_lit',
            'Yes', 'No',
            # Binary operators (needed for BUILD_TAIL / expression actions)
            '+', '-', '*', '/', '//', '%', '**',
            '||', '&&', '==', '!=', '>', '<', '>=', '<=',
            # Compound assignment ops & increment/decrement
            '+=', '-=', '*=', '/=', '//=', '%=', '**=', '++', '--',
            # Unary
            '!',
            # Type keywords
            'num', 'decimal', 'bigdecimal', 'bool', 'text', 'letter', 'empty',
            # Keywords with semantic value
            'fixed', 'stop', 'skip',
            # NOTE: '=' is NOT semantic — it appears in declarations and
            # assignment_tail but the specific production already determines
            # the action to take.
        }

        pass_through_nts = {
            '<program>', '<stmt_value>', '<arg_value>', '<cond_value>',
            '<index_value>',
            '<stmt_post>', '<arg_post>', '<index_post>',
            '<control_statement>', '<iterative_statement>',
            '<declaration>', '<statement>',
        }

        fold_tail_nts = {
            '<stmt_or>', '<stmt_and>', '<stmt_eq>', '<stmt_rel>',
            '<stmt_add>', '<stmt_mult>',
            '<arg_or>', '<arg_and>', '<arg_eq>', '<arg_rel>',
            '<arg_add>', '<arg_mult>',
            '<index_add>', '<index_mult>',
        }

        build_tail_nts = {
            '<stmt_or_tail>', '<stmt_and_tail>', '<stmt_eq_tail>',
            '<stmt_rel_tail>', '<stmt_add_tail>', '<stmt_mult_tail>',
            '<arg_or_tail>', '<arg_and_tail>', '<arg_eq_tail>',
            '<arg_rel_tail>', '<arg_add_tail>', '<arg_mult_tail>',
            '<index_add_tail>', '<index_mult_tail>',
        }

        fold_exp_nts = {
            '<stmt_exp>', '<arg_exp>', '<index_exp>',
        }

        build_exp_tail_nts = {
            '<stmt_exp_tail>', '<arg_exp_tail>', '<index_exp_tail>',
        }

        list_accum_nts = {
            '<statements>', '<option_statements>',
            '<local_declarations>',
            '<group_body>', '<group_body_tail>',
            '<option_blocks>',
            '<val_list_rows>', '<val_list_rows_tail>',
        }

        list_tail_nts = {
            '<parameter_list_tail>', '<arg_list_tail>',
            '<val_list_tail>',
        }

        for nt, prods in self.productions.items():
            for prod in prods:
                key = (nt, tuple(prod))
                is_epsilon = prod == ['λ']

                # ── Handle specific custom productions first ────

                # Datatype
                if nt == '<datatype>':
                    self.production_actions[key] = 'CUSTOM_datatype'
                    continue

                # Return type
                if nt == '<return_type>':
                    self.production_actions[key] = 'CUSTOM_return_type'
                    continue

                # Literal
                if nt == '<literal>':
                    self.production_actions[key] = 'CUSTOM_literal'
                    continue

                # Control flow
                if nt == '<control_flow>':
                    self.production_actions[key] = 'CUSTOM_control_flow'
                    continue

                # Group member
                if nt == '<group_member>':
                    self.production_actions[key] = 'CUSTOM_group_member'
                    continue

                # Group definitions
                if nt == '<group_definitions>':
                    self.production_actions[key] = 'CUSTOM_group_definitions'
                    continue

                # Global modifier
                if nt == '<global_modifier>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_global_modifier_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_global_modifier'
                    continue

                # Global typed decl
                if nt == '<global_typed_decl>':
                    self.production_actions[key] = 'CUSTOM_global_typed_decl'
                    continue

                # Global variable declarations
                if nt == '<global_variable_declarations>':
                    self.production_actions[key] = 'CUSTOM_global_variable_declarations'
                    continue

                # Parameter
                if nt == '<parameter>':
                    self.production_actions[key] = 'CUSTOM_parameter'
                    continue

                # Parameter list
                if nt == '<parameter_list>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_parameter_list_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_parameter_list'
                    continue

                # Return tail
                if nt == '<return_tail>':
                    if prod == [';']:
                        self.production_actions[key] = 'CUSTOM_return_tail_empty'
                    else:
                        self.production_actions[key] = 'CUSTOM_return_tail_value'
                    continue

                # Optional return
                if nt == '<optional_return>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_optional_return_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_optional_return'
                    continue

                # Function definitions
                if nt == '<function_definitions>':
                    self.production_actions[key] = 'CUSTOM_function_definitions'
                    continue

                # Start block
                if nt == '<start_block>':
                    self.production_actions[key] = 'CUSTOM_start_block'
                    continue

                # Group part
                if nt == '<group_part>':
                    if prod == ['<group_definitions>', '<group_part>']:
                        self.production_actions[key] = 'CUSTOM_group_part_recursive'
                    else:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                # Worldwide part
                if nt == '<worldwide_part>':
                    if prod == ['<global_variable_declarations>', '<worldwide_part>']:
                        self.production_actions[key] = 'CUSTOM_worldwide_part_recursive'
                    else:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                # Define part
                if nt == '<define_part>':
                    if prod == ['<function_definitions>', '<define_part>']:
                        self.production_actions[key] = 'CUSTOM_define_part_recursive'
                    else:
                        self.production_actions[key] = 'CUSTOM_define_part_base'
                    continue

                # Local declaration
                if nt == '<local_declaration>':
                    if prod == ['identifier', 'identifier', ';']:
                        self.production_actions[key] = 'CUSTOM_local_declaration_group_typed'
                    else:
                        self.production_actions[key] = 'CUSTOM_local_declaration_typed'
                    continue

                # Fixed typed decl
                if nt == '<fixed_typed_decl>':
                    self.production_actions[key] = 'CUSTOM_fixed_typed_decl'
                    continue

                # Fixed declaration
                if nt == '<fixed_declaration>':
                    self.production_actions[key] = 'CUSTOM_fixed_declaration'
                    continue

                # List typed decl
                if nt == '<list_typed_decl>':
                    self.production_actions[key] = 'CUSTOM_list_typed_decl'
                    continue

                # List declaration
                if nt == '<list_declaration>':
                    self.production_actions[key] = 'CUSTOM_list_declaration'
                    continue

                # Val list (1d/2d)
                if nt == '<val_list>':
                    self.production_actions[key] = 'PASS_THROUGH'
                    continue

                if nt == '<val_list_1d>':
                    self.production_actions[key] = 'CUSTOM_val_list_1d'
                    continue

                if nt == '<val_list_elems>':
                    if is_epsilon:
                        self.production_actions[key] = 'EPSILON_LIST'
                    else:
                        self.production_actions[key] = 'CUSTOM_val_list_elems'
                    continue

                if nt == '<val_list_2d>':
                    self.production_actions[key] = 'CUSTOM_val_list_2d'
                    continue

                # Assignable
                if nt == '<assignable>':
                    self.production_actions[key] = 'CUSTOM_assignable'
                    continue

                if nt == '<assignable_suffix>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_assignable_suffix_epsilon'
                    elif prod[0] == '[':
                        self.production_actions[key] = 'CUSTOM_assignable_suffix_index'
                    elif prod[0] == '.':
                        self.production_actions[key] = 'CUSTOM_assignable_suffix_member'
                    continue

                if nt == '<assignable_2d>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_assignable_2d_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_assignable_2d_index'
                    continue

                # Assignment statement
                if nt == '<assignment_statement>':
                    self.production_actions[key] = 'CUSTOM_assignment_statement'
                    continue

                if nt == '<assignment_tail>':
                    if prod[0] == '=':
                        self.production_actions[key] = 'CUSTOM_assignment_tail_eq'
                    elif prod[0] in ('+=', '-=', '*=', '/=', '//=', '%=', '**='):
                        self.production_actions[key] = 'CUSTOM_assignment_tail_compound'
                    elif prod[0] == '++':
                        self.production_actions[key] = 'CUSTOM_assignment_tail_increment'
                    elif prod[0] == '--':
                        self.production_actions[key] = 'CUSTOM_assignment_tail_decrement'
                    continue

                # Function call
                if nt == '<function_call>':
                    self.production_actions[key] = 'CUSTOM_function_call'
                    continue

                if nt == '<function_call_statement>':
                    self.production_actions[key] = 'CUSTOM_function_call_statement'
                    continue

                # Arg list
                if nt == '<arg_list>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_arg_list_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_arg_list'
                    continue

                # I/O
                if nt == '<io_statement>':
                    if prod[0] == 'show':
                        self.production_actions[key] = 'CUSTOM_io_show'
                    elif prod[0] == 'display':
                        self.production_actions[key] = 'CUSTOM_io_display'
                    else:
                        self.production_actions[key] = 'CUSTOM_io_read'
                    continue

                # Check structure
                if nt == '<check_structure>':
                    self.production_actions[key] = 'CUSTOM_check_structure'
                    continue

                # Otherwise chain
                if nt == '<otherwise_chain>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_otherwise_chain_epsilon'
                    elif prod[0] == 'otherwisecheck':
                        self.production_actions[key] = 'CUSTOM_otherwise_chain_elif'
                    else:
                        self.production_actions[key] = 'CUSTOM_otherwise_chain_else'
                    continue

                # Select
                if nt == '<select_statement>':
                    self.production_actions[key] = 'CUSTOM_select_statement'
                    continue

                if nt == '<option_block>':
                    self.production_actions[key] = 'CUSTOM_option_block'
                    continue

                if nt == '<optional_fallback>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_optional_fallback_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_optional_fallback'
                    continue

                # Each loop
                if nt == '<each_loop>':
                    self.production_actions[key] = 'CUSTOM_each_loop'
                    continue

                if nt == '<step_clause>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_step_clause_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_step_clause'
                    continue

                # During loop
                if nt == '<during_loop>':
                    self.production_actions[key] = 'CUSTOM_during_loop'
                    continue

                # Unary productions
                if nt in ('<stmt_unary>', '<arg_unary>'):
                    if prod[0] == '-':
                        self.production_actions[key] = 'CUSTOM_unary_neg'
                    elif prod[0] == '!':
                        self.production_actions[key] = 'CUSTOM_unary_not'
                    else:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                if nt == '<index_unary>':
                    if prod[0] == '-':
                        self.production_actions[key] = 'CUSTOM_index_unary_neg'
                    else:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                # Primary with parens
                if nt in ('<stmt_prim>', '<arg_prim>'):
                    if prod[0] == '(':
                        self.production_actions[key] = 'CUSTOM_prim_paren'
                    elif prod[0] == 'identifier':
                        self.production_actions[key] = 'CUSTOM_prim_identifier'
                    elif prod == ['<literal>']:
                        self.production_actions[key] = 'PASS_THROUGH'
                    elif prod == ['<size_call>']:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                if nt == '<index_prim>':
                    if prod[0] == '(':
                        self.production_actions[key] = 'CUSTOM_prim_paren'
                    elif prod == ['num_lit']:
                        self.production_actions[key] = 'CUSTOM_index_prim_num'
                    elif prod == ['decimal_lit']:
                        self.production_actions[key] = 'CUSTOM_index_prim_decimal'
                    elif prod[0] == 'identifier':
                        self.production_actions[key] = 'CUSTOM_prim_identifier'
                    elif prod == ['<size_call>']:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                # Id suffix (for all expression contexts)
                if nt in ('<stmt_id_suffix>', '<arg_id_suffix>', '<index_id_suffix>',
                          '<from_id_suffix>', '<to_id_suffix>', '<step_id_suffix>'):
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_id_suffix_epsilon'
                    elif prod[0] == '(':
                        self.production_actions[key] = 'CUSTOM_id_suffix_call'
                    elif prod[0] == '[':
                        self.production_actions[key] = 'CUSTOM_id_suffix_index'
                    elif prod[0] == '.':
                        self.production_actions[key] = 'CUSTOM_id_suffix_member'
                    continue

                # Var 2d suffixes
                if nt in ('<stmt_var_2d>', '<arg_var_2d>', '<index_var_2d>',
                          '<from_var_2d>', '<to_var_2d>', '<step_var_2d>',
                          '<assignable_2d>'):
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_var_2d_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_var_2d_index'
                    continue

                # Size call
                if nt == '<size_call>':
                    self.production_actions[key] = 'CUSTOM_size_call'
                    continue

                if nt == '<size_second_arg>':
                    if is_epsilon:
                        self.production_actions[key] = 'CUSTOM_size_second_arg_epsilon'
                    else:
                        self.production_actions[key] = 'CUSTOM_size_second_arg'
                    continue

                # Range primaries (from/to/step)
                if nt in ('<from_primary>', '<to_primary>', '<step_primary>'):
                    if prod == ['num_lit']:
                        self.production_actions[key] = 'CUSTOM_from_primary_num'
                    elif prod == ['decimal_lit']:
                        self.production_actions[key] = 'CUSTOM_from_primary_decimal'
                    elif prod[0] == 'identifier':
                        self.production_actions[key] = 'CUSTOM_prim_identifier'
                    elif prod == ['<size_call>']:
                        self.production_actions[key] = 'PASS_THROUGH'
                    continue

                # ── Standard categories ─────────────────────────
                if is_epsilon:
                    if nt in list_accum_nts or nt in list_tail_nts:
                        self.production_actions[key] = 'EPSILON_LIST'
                    elif nt in build_tail_nts or nt in build_exp_tail_nts:
                        self.production_actions[key] = 'EPSILON_TAIL'
                    else:
                        self.production_actions[key] = 'EPSILON'
                    continue

                if nt in pass_through_nts:
                    self.production_actions[key] = 'PASS_THROUGH'
                    continue

                if nt in fold_tail_nts:
                    self.production_actions[key] = 'FOLD_TAIL'
                    continue

                if nt in build_tail_nts:
                    self.production_actions[key] = 'BUILD_TAIL'
                    continue

                if nt in fold_exp_nts:
                    self.production_actions[key] = 'FOLD_EXP'
                    continue

                if nt in build_exp_tail_nts:
                    self.production_actions[key] = 'BUILD_EXP_TAIL'
                    continue

                if nt in list_accum_nts:
                    self.production_actions[key] = 'COLLECT_LIST'
                    continue

                if nt in list_tail_nts:
                    self.production_actions[key] = 'COLLECT_LIST_TAIL'
                    continue

                # Fallback
                self.production_actions[key] = 'PASS_THROUGH'

        # Build the custom actions dispatch table
        self._custom_actions = {
            'CUSTOM_datatype': TableDrivenParser._action_datatype,
            'CUSTOM_return_type': TableDrivenParser._action_return_type,
            'CUSTOM_literal': TableDrivenParser._action_literal,
            'CUSTOM_control_flow': TableDrivenParser._action_control_flow,
            'CUSTOM_group_member': TableDrivenParser._action_group_member,
            'CUSTOM_group_definitions': TableDrivenParser._action_group_definitions,
            'CUSTOM_global_modifier': TableDrivenParser._action_global_modifier,
            'CUSTOM_global_modifier_epsilon': TableDrivenParser._action_global_modifier_epsilon,
            'CUSTOM_global_typed_decl': TableDrivenParser._action_global_typed_decl,
            'CUSTOM_global_variable_declarations': TableDrivenParser._action_global_variable_declarations,
            'CUSTOM_parameter': TableDrivenParser._action_parameter,
            'CUSTOM_parameter_list': TableDrivenParser._action_parameter_list,
            'CUSTOM_parameter_list_epsilon': TableDrivenParser._action_parameter_list_epsilon,
            'CUSTOM_return_tail_value': TableDrivenParser._action_return_tail_value,
            'CUSTOM_return_tail_empty': TableDrivenParser._action_return_tail_empty,
            'CUSTOM_optional_return': TableDrivenParser._action_optional_return,
            'CUSTOM_optional_return_epsilon': TableDrivenParser._action_optional_return_epsilon,
            'CUSTOM_function_definitions': TableDrivenParser._action_function_definitions,
            'CUSTOM_start_block': TableDrivenParser._action_start_block,
            'CUSTOM_group_part_recursive': TableDrivenParser._action_group_part_recursive,
            'CUSTOM_worldwide_part_recursive': TableDrivenParser._action_worldwide_part_recursive,
            'CUSTOM_define_part_recursive': TableDrivenParser._action_define_part_recursive,
            'CUSTOM_define_part_base': TableDrivenParser._action_define_part_base,
            'CUSTOM_local_declaration_group_typed': TableDrivenParser._action_local_declaration_group_typed,
            'CUSTOM_local_declaration_typed': TableDrivenParser._action_local_declaration_typed,
            'CUSTOM_fixed_typed_decl': TableDrivenParser._action_fixed_typed_decl,
            'CUSTOM_fixed_declaration': TableDrivenParser._action_fixed_declaration,
            'CUSTOM_list_typed_decl': TableDrivenParser._action_list_typed_decl,
            'CUSTOM_list_declaration': TableDrivenParser._action_list_declaration,
            'CUSTOM_val_list_1d': TableDrivenParser._action_val_list_1d,
            'CUSTOM_val_list_elems': TableDrivenParser._action_val_list_elems,
            'CUSTOM_val_list_2d': TableDrivenParser._action_val_list_2d,
            'CUSTOM_assignable': TableDrivenParser._action_assignable,
            'CUSTOM_assignable_suffix_index': TableDrivenParser._action_assignable_suffix_index,
            'CUSTOM_assignable_suffix_member': TableDrivenParser._action_assignable_suffix_member,
            'CUSTOM_assignable_suffix_epsilon': TableDrivenParser._action_assignable_suffix_epsilon,
            'CUSTOM_assignable_2d_index': TableDrivenParser._action_assignable_2d_index,
            'CUSTOM_assignable_2d_epsilon': TableDrivenParser._action_assignable_2d_epsilon,
            'CUSTOM_assignment_statement': TableDrivenParser._action_assignment_statement,
            'CUSTOM_assignment_tail_eq': TableDrivenParser._action_assignment_tail_eq,
            'CUSTOM_assignment_tail_compound': TableDrivenParser._action_assignment_tail_compound,
            'CUSTOM_assignment_tail_increment': TableDrivenParser._action_assignment_tail_increment,
            'CUSTOM_assignment_tail_decrement': TableDrivenParser._action_assignment_tail_decrement,
            'CUSTOM_function_call': TableDrivenParser._action_function_call,
            'CUSTOM_function_call_statement': TableDrivenParser._action_function_call_statement,
            'CUSTOM_arg_list': TableDrivenParser._action_arg_list,
            'CUSTOM_arg_list_epsilon': TableDrivenParser._action_arg_list_epsilon,
            'CUSTOM_io_show': TableDrivenParser._action_io_show,
            'CUSTOM_io_display': TableDrivenParser._action_io_display,
            'CUSTOM_io_read': TableDrivenParser._action_io_read,
            'CUSTOM_check_structure': TableDrivenParser._action_check_structure,
            'CUSTOM_otherwise_chain_elif': TableDrivenParser._action_otherwise_chain_elif,
            'CUSTOM_otherwise_chain_else': TableDrivenParser._action_otherwise_chain_else,
            'CUSTOM_otherwise_chain_epsilon': TableDrivenParser._action_otherwise_chain_epsilon,
            'CUSTOM_select_statement': TableDrivenParser._action_select_statement,
            'CUSTOM_option_block': TableDrivenParser._action_option_block,
            'CUSTOM_optional_fallback': TableDrivenParser._action_optional_fallback,
            'CUSTOM_optional_fallback_epsilon': TableDrivenParser._action_optional_fallback_epsilon,
            'CUSTOM_each_loop': TableDrivenParser._action_each_loop,
            'CUSTOM_step_clause': TableDrivenParser._action_step_clause,
            'CUSTOM_step_clause_epsilon': TableDrivenParser._action_step_clause_epsilon,
            'CUSTOM_during_loop': TableDrivenParser._action_during_loop,
            'CUSTOM_unary_neg': TableDrivenParser._action_unary_neg,
            'CUSTOM_unary_not': TableDrivenParser._action_unary_not,
            'CUSTOM_prim_paren': TableDrivenParser._action_prim_paren,
            'CUSTOM_prim_identifier': TableDrivenParser._action_prim_identifier,
            'CUSTOM_id_suffix_call': TableDrivenParser._action_id_suffix_call,
            'CUSTOM_id_suffix_index': TableDrivenParser._action_id_suffix_index,
            'CUSTOM_id_suffix_member': TableDrivenParser._action_id_suffix_member,
            'CUSTOM_id_suffix_epsilon': TableDrivenParser._action_id_suffix_epsilon,
            'CUSTOM_var_2d_index': TableDrivenParser._action_var_2d_index,
            'CUSTOM_var_2d_epsilon': TableDrivenParser._action_var_2d_epsilon,
            'CUSTOM_size_call': TableDrivenParser._action_size_call,
            'CUSTOM_size_second_arg': TableDrivenParser._action_size_second_arg,
            'CUSTOM_size_second_arg_epsilon': TableDrivenParser._action_size_second_arg_epsilon,
            'CUSTOM_index_prim_num': TableDrivenParser._action_index_prim_num,
            'CUSTOM_index_prim_decimal': TableDrivenParser._action_index_prim_decimal,
            'CUSTOM_index_unary_neg': TableDrivenParser._action_index_unary_neg,
            'CUSTOM_from_primary_num': TableDrivenParser._action_from_primary_num,
            'CUSTOM_from_primary_decimal': TableDrivenParser._action_from_primary_decimal,
        }

    def advance(self):
        """Move to next token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def _error(self, message):
        """Report parsing error with location"""
        token = self.current_token

        if token and hasattr(token, 'pos_start') and token.pos_start:
            line = token.pos_start.ln + 1
            col = token.pos_start.col + 1
            raise SyntaxError(
                f"Parse Error at Line {line}, Column {col}\n{message}")
        else:
            raise SyntaxError(f"Parse Error\n{message}")

    def print_statistics(self):
        """Print grammar statistics"""
        print("\n" + "="*80)
        print("GRAMMAR STATISTICS")
        print("="*80)
        total_prods = sum(len(prods) for prods in self.productions.values())
        print(f"Non-terminals: {len(self.non_terminals)}")
        print(f"Terminals: {len(self.terminals)}")
        print(f"Productions: {total_prods}")
        print(f"Parsing table entries: {len(self.table)}")
        print(f"Conflicts: {len(self.conflicts)}")

        if len(self.conflicts) == 0:
            print("\n✓ Grammar is LL(1)!")
        else:
            print(
                f"\n⚠ Grammar has {len(self.conflicts)} conflicts (requires lookahead)")


class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'Token({self.type}, {self.value})'
        return f'Token({self.type})'


if __name__ == "__main__":
    print("OPTIMIZED CONTEXT-SPECIFIC TABLE-DRIVEN LL(1) PARSER")
    print("="*80)

    # Test
    test_tokens = [
        Token('start'),
        Token('{'),
        Token('num'), Token('identifier', 'x'), Token(
            '='), Token('num_lit', '5'), Token(';'),
        Token('}'),
        Token('finish')
    ]

    parser = TableDrivenParser(test_tokens)
    parser.print_statistics()

    try:
        result = parser.parse()
        print(f"\n✓ Test passed! Result: {type(result).__name__}")
        if hasattr(result, 'start_body'):
            print(f"  Start body: {result.start_body}")
    except SyntaxError as e:
        print(f"\n✗ Test failed: {e}")
