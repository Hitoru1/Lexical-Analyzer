

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

    def _init_grammar(self):
        """Defining the 413 CFG Productions"""

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
                ['option', '<literal>', ':', '<statements>',
                    '<control_flow>', ';']
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
                ['>', '<stmt_add>'],
                ['<', '<stmt_add>'],
                ['>=', '<stmt_add>'],
                ['<=', '<stmt_add>'],
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
                ['>', '<arg_add>'],
                ['<', '<arg_add>'],
                ['>=', '<arg_add>'],
                ['<=', '<arg_add>'],
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



            '<cond_value>': [['<cond_or>']],

            '<cond_or>': [['<cond_and>', '<cond_or_tail>']],
            '<cond_or_tail>': [
                ['||', '<cond_and>', '<cond_or_tail>'],
                ['λ']
            ],

            '<cond_and>': [['<cond_eq>', '<cond_and_tail>']],
            '<cond_and_tail>': [
                ['&&', '<cond_eq>', '<cond_and_tail>'],
                ['λ']
            ],

            '<cond_eq>': [['<cond_comp>', '<cond_eq_tail>']],
            '<cond_eq_tail>': [
                ['==', '<cond_comp>', '<cond_eq_tail>'],
                ['!=', '<cond_comp>', '<cond_eq_tail>'],
                ['λ']
            ],

            '<cond_comp>': [['<cond_unary>']],

            '<cond_unary>': [
                ['!', '<cond_base>'],
                ['<cond_base>']
            ],

            '<cond_base>': [
                ['Yes'],
                ['No'],
                ['(', '<cond_inner_paren>'],

                ['<cond_arith_noparen>', '<cond_rel_tail>'],

                ['string_lit', '<cond_str_tail>'],
                ['char_lit', '<cond_str_tail>']
            ],


            '<cond_str_tail>': [
                ['==', '<cond_eq_rhs>'],
                ['!=', '<cond_eq_rhs>']
            ],


            '<cond_paren_tail>': [

                [')', '<cond_rel_tail>'],

                ['<cond_rel_tail_in_paren>', '<cond_and_tail_ip>',
                    '<cond_or_tail_ip>', ')']
            ],



            '<cond_rel_tail_in_paren>': [
                ['>', '<cond_arith_no_rel>'],
                ['<', '<cond_arith_no_rel>'],
                ['>=', '<cond_arith_no_rel>'],
                ['<=', '<cond_arith_no_rel>'],
                ['==', '<cond_eq_rhs>'],
                ['!=', '<cond_eq_rhs>']
            ],


            '<cond_inner_paren>': [

                ['<cond_arith>', '<cond_paren_tail>'],
                ['!', '<cond_comparison_ip>', '<cond_and_tail_ip>',
                    '<cond_or_tail_ip>', ')'],
                ['Yes', '<cond_and_tail_ip>', '<cond_or_tail_ip>', ')'],
                ['No', '<cond_and_tail_ip>', '<cond_or_tail_ip>', ')'],
                ['string_lit', '<cond_str_tail>', '<cond_and_tail_ip>',
                    '<cond_or_tail_ip>', ')'],
                ['char_lit', '<cond_str_tail>', '<cond_and_tail_ip>',
                    '<cond_or_tail_ip>', ')']
            ],


            '<cond_and_tail_ip>': [
                ['&&', '<cond_comparison_ip>', '<cond_and_tail_ip>'],
                ['λ']
            ],


            '<cond_or_tail_ip>': [
                ['||', '<cond_and_ip>', '<cond_or_tail_ip>'],
                ['λ']
            ],


            '<cond_and_ip>': [
                ['<cond_comparison_ip>', '<cond_and_tail_ip>']
            ],


            '<cond_comparison_ip>': [

                ['<cond_arith_noparen>', '<cond_rel_tail_in_paren>'],

                ['(', '<cond_arith>', '<cond_paren_tail_ip>'],

                ['!', '<cond_comparison_ip>'],

                ['Yes'],

                ['No'],

                ['string_lit', '<cond_str_tail>'],

                ['char_lit', '<cond_str_tail>']
            ],


            '<cond_paren_tail_ip>': [

                [')', '<cond_rel_tail_in_paren>'],
                ['<cond_rel_tail_in_paren>', '<cond_and_tail_ip>',

                    '<cond_or_tail_ip>', ')']
            ],


            '<cond_rel_tail>': [
                ['>', '<cond_arith_no_rel>'],
                ['<', '<cond_arith_no_rel>'],
                ['>=', '<cond_arith_no_rel>'],
                ['<=', '<cond_arith_no_rel>'],
                ['==', '<cond_eq_rhs>'],
                ['!=', '<cond_eq_rhs>']
            ],


            '<cond_eq_rhs>': [
                ['Yes'],
                ['No'],
                ['<cond_arith_no_rel>'],
                ['string_lit'],
                ['char_lit']
            ],


            '<cond_arith_no_rel>': [['<cond_add_no_rel>']],


            '<cond_add_no_rel>': [['<cond_mult_no_rel>', '<cond_add_tail_no_rel>']],
            '<cond_add_tail_no_rel>': [
                ['+', '<cond_mult_no_rel>', '<cond_add_tail_no_rel>'],
                ['-', '<cond_mult_no_rel>', '<cond_add_tail_no_rel>'],
                ['λ']
            ],


            '<cond_mult_no_rel>': [['<cond_exp_no_rel>', '<cond_mult_tail_no_rel>']],
            '<cond_mult_tail_no_rel>': [
                ['*', '<cond_exp_no_rel>', '<cond_mult_tail_no_rel>'],
                ['/', '<cond_exp_no_rel>', '<cond_mult_tail_no_rel>'],
                ['%', '<cond_exp_no_rel>', '<cond_mult_tail_no_rel>'],
                ['λ']
            ],


            '<cond_exp_no_rel>': [['<cond_arith_unary_no_rel>', '<cond_exp_tail_no_rel>']],
            '<cond_exp_tail_no_rel>': [
                ['**', '<cond_exp_no_rel>'],
                ['λ']
            ],

            '<cond_arith_unary_no_rel>': [
                ['-', '<cond_post_no_rel>'],
                ['<cond_post_no_rel>']
            ],


            '<cond_post_no_rel>': [['<cond_prim_no_rel>']],


            '<cond_prim_no_rel>': [
                ['(', '<cond_arith_no_rel>', ')'],
                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<cond_id_suffix_no_rel>'],
                ['<size_call>']
            ],

            '<cond_id_suffix_no_rel>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<cond_var_2d_no_rel>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<cond_var_2d_no_rel>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



            '<cond_arith_noparen>': [['<cond_add_noparen>']],


            '<cond_add_noparen>': [['<cond_mult_noparen>', '<cond_add_tail>']],

            '<cond_mult_noparen>': [['<cond_exp_noparen>', '<cond_mult_tail>']],

            '<cond_exp_noparen>': [['<cond_unary_noparen>', '<cond_exp_tail>']],

            '<cond_unary_noparen>': [
                ['-', '<cond_post>'],
                ['<cond_prim_noparen>']
            ],


            '<cond_prim_noparen>': [

                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<cond_id_suffix>'],
                ['<size_call>']
            ],



            '<cond_arith>': [['<cond_add>']],

            '<cond_add>': [['<cond_mult>', '<cond_add_tail>']],
            '<cond_add_tail>': [
                ['+', '<cond_mult>', '<cond_add_tail>'],
                ['-', '<cond_mult>', '<cond_add_tail>'],
                ['λ']
            ],

            '<cond_mult>': [['<cond_exp>', '<cond_mult_tail>']],
            '<cond_mult_tail>': [
                ['*', '<cond_exp>', '<cond_mult_tail>'],
                ['/', '<cond_exp>', '<cond_mult_tail>'],
                ['%', '<cond_exp>', '<cond_mult_tail>'],
                ['λ']
            ],

            '<cond_exp>': [['<cond_arith_unary>', '<cond_exp_tail>']],
            '<cond_exp_tail>': [
                ['**', '<cond_exp>'],
                ['λ']
            ],

            '<cond_arith_unary>': [
                ['-', '<cond_post>'],
                ['<cond_post>']
            ],


            '<cond_post>': [['<cond_prim>']],


            '<cond_prim>': [
                ['(', '<cond_arith>', ')'],
                ['num_lit'],
                ['decimal_lit'],
                ['identifier', '<cond_id_suffix>'],
                ['<size_call>']
            ],

            '<cond_id_suffix>': [
                ['(', '<arg_list>', ')'],
                ['[', '<index_value>', ']', '<cond_var_2d>'],
                ['.', 'identifier'],
                ['λ']
            ],

            '<cond_var_2d>': [
                ['[', '<index_value>', ']'],
                ['λ']
            ],



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

    def parse(self, verbose=False):
        """Table-driven LL(1) parsing algorithm"""
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

            # Case 1: Top is $
            if top == '$':
                if verbose:
                    print("="*80)
                    print("PARSING SUCCESSFUL!")
                    print("="*80)
                return True

            # Case 2: Top is terminal
            elif top in self.terminals:
                if top == current:
                    if verbose:
                        print(f"  MATCH '{top}'")
                    self.stack.pop()
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
                # Special case: Statement-level ambiguity requires 2-token lookahead
                if top == '<statement>' and current == 'identifier':
                    # Look at the NEXT token to decide
                    next_token = None
                    if self.pos + 1 < len(self.tokens):
                        next_tok_obj = self.tokens[self.pos + 1]
                        if hasattr(next_tok_obj, 'type'):
                            next_token = next_tok_obj.type
                        else:
                            next_token = str(next_tok_obj)
                    else:
                        next_token = '$'  # End of input

                    # Decide based on second token
                    if next_token in ['=', '+=', '-=', '*=', '/=', '%=', '**=', '++', '--', '[', '.']:
                        # Assignment: x = 5; or x += 5; or x[0] = 5; or x.field = 5;
                        production = ['<assignment_statement>']
                    elif next_token == '(':
                        # Function call: foo();
                        production = ['<function_call_statement>']
                    elif next_token == 'identifier':
                        # Declaration: Person p;
                        production = ['<declaration>']
                    else:
                        # Unrecognized token after IDENTIFIER in statement (including ';', '}', '$', operators, etc.)
                        # We can't determine which production the user intended
                        # Show all valid tokens from assignment, function call, and declaration
                        # This is an error situation, so we trigger error with combined FIRST sets

                        # Collect valid tokens from all three possibilities:
                        # 1. Assignment: =, +=, -=, *=, /=, %=, **=, ++, --, [, .
                        # 2. Function call: (
                        # 3. Declaration: IDENTIFIER
                        all_valid_tokens = set()
                        all_valid_tokens.update(
                            # Assignment
                            ['=', '+=', '-=', '*=', '/=', '%=', '**=', '++', '--', '[', '.'])
                        all_valid_tokens.add('(')  # Function call
                        all_valid_tokens.add('identifier')  # Declaration

                        exp_str = ', '.join(
                            f"'{e}'" for e in sorted(all_valid_tokens))
                        self._error(
                            f"Unexpected: '{next_token}'\nExpected: {exp_str}")

                    if verbose:
                        prod_str = ' '.join(production)
                        print(
                            f"  EXPAND {top} → {prod_str} (2-token lookahead, next={next_token})")

                    self.stack.pop()
                    if production != ['λ']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                    self.derivations.append((top, production))

                # Special case: List 1D vs 2D disambiguation
                elif top == '<val_list>' and current == '[':
                    # Look at the NEXT token after '['
                    next_token = None
                    if self.pos + 1 < len(self.tokens):
                        next_tok_obj = self.tokens[self.pos + 1]
                        if hasattr(next_tok_obj, 'type'):
                            next_token = next_tok_obj.type
                        else:
                            next_token = str(next_tok_obj)
                    else:
                        next_token = '$'

                    # Decide: if next is '[', it's 2D; otherwise 1D
                    if next_token == '[':
                        production = ['<val_list_2d>']
                    else:
                        production = ['<val_list_1d>']

                    if verbose:
                        prod_str = ' '.join(production)
                        print(
                            f"  EXPAND {top} → {prod_str} (2-token lookahead for list, next={next_token})")

                    self.stack.pop()
                    if production != ['λ']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                    self.derivations.append((top, production))

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
                                term for (nt, term) in self.table.keys() if nt == top and term != current)
                            self.skipped_expected.update(other_tokens)

                        self.stack.pop()
                        if production != ['λ']:
                            for symbol in reversed(production):
                                self.stack.append(symbol)

                        self.derivations.append((top, production))
                    else:
                        # Context-specific error message
                        # Combine current expected with skipped alternatives
                        expected = set(
                            term for (nt, term) in self.table.keys() if nt == top)
                        expected.update(self.skipped_expected)
                        expected = sorted(expected)
                        if expected:
                            exp_str = ', '.join(f"'{e}'" for e in expected)
                            self._error(
                                f"Unexpected: '{current}'\nExpected: {exp_str}")
                        else:
                            self._error(
                                f"Unexpected: '{current}'\nNo valid continuation for {top}")
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
        return True

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
        print("\n✓ Test passed!")
    except SyntaxError as e:
        print(f"\n✗ Test failed: {e}")
