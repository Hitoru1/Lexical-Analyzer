"""
OPTIMIZED CONTEXT-SPECIFIC TABLE-DRIVEN LL(1) PARSER FOR KUCODE

374 Productions - 5 Expression Hierarchies + Boolean Enforcement
- <stmt_value>: declarations, assignments, returns (FOLLOW = {';'})
- <arg_value>: function args, list elements (FOLLOW = {',', ')', ']'})
- <cond_value>: conditions (FOLLOW = {')'})
- <index_value>: array indices (FOLLOW = {']'})
- <from_primary>, <to_primary>, <step_primary>: loop bounds (PRIMARY ONLY)

BOOLEAN ENFORCEMENT:
- Removed λ from <cond_rel_tail> (production 276)
- Arithmetic in conditions MUST have comparison operator
- check(x + 5) → SYNTAX ERROR (must be check(x + 5 > 0))
- check(flag) → SYNTAX ERROR (must be check(flag == Yes))
"""


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

    def _init_grammar(self):
        """Define the complete 374-production CFG with boolean enforcement"""

        self.productions = {
            # ============================================================
            # PROGRAM STRUCTURE (1-8)
            # ============================================================

            '<program>': [
                ['<group_part>']  # 1
            ],

            '<group_part>': [
                ['<group_definitions>', '<group_part>'],  # 2
                ['<worldwide_part>']  # 3
            ],

            '<worldwide_part>': [
                ['<global_variable_declarations>', '<worldwide_part>'],  # 4
                ['<define_part>']  # 5
            ],

            '<define_part>': [
                ['<function_definitions>', '<define_part>'],  # 6
                ['<start_block>']  # 7
            ],

            '<start_block>': [
                ['start', '{', '<statements>', '}', 'finish']  # 8
            ],

            # ============================================================
            # GROUP DEFINITIONS (9-14)
            # ============================================================

            '<group_definitions>': [
                ['group', 'identifier', '{', '<group_body>', '}']  # 9
            ],

            '<group_body>': [
                ['<group_member>', '<group_body_tail>'],  # 10
                ['λ']  # 11
            ],

            '<group_body_tail>': [
                ['<group_member>', '<group_body_tail>'],  # 12
                ['λ']  # 13
            ],

            '<group_member>': [
                ['<datatype>', 'identifier', ';']  # 14
            ],

            # ============================================================
            # DATATYPES (15-20)
            # ============================================================

            '<datatype>': [
                ['num'],  # 15
                ['decimal'],  # 16
                ['bigdecimal'],  # 17
                ['bool'],  # 18
                ['text'],  # 19
                ['letter']  # 20
            ],

            # ============================================================
            # GLOBAL DECLARATIONS (21-27) - uses <stmt_value>
            # ============================================================

            '<global_variable_declarations>': [
                ['worldwide', '<global_typed_decl>']  # 21
            ],

            '<global_typed_decl>': [
                ['num', 'identifier', '=', '<stmt_value>', ';'],  # 22
                ['decimal', 'identifier', '=', '<stmt_value>', ';'],  # 23
                ['bigdecimal', 'identifier', '=', '<stmt_value>', ';'],  # 24
                ['bool', 'identifier', '=', '<stmt_value>', ';'],  # 25
                ['text', 'identifier', '=', '<stmt_value>', ';'],  # 26
                ['letter', 'identifier', '=', '<stmt_value>', ';']  # 27
            ],

            # ============================================================
            # FUNCTION DEFINITIONS (28-44) - uses <stmt_value>
            # ============================================================

            '<function_definitions>': [
                ['define', '<return_type>', 'identifier', '(', '<parameter_list>', ')',
                 '{', '<local_declarations>', '<statements>', '<optional_return>', '}']  # 28
            ],

            '<return_type>': [
                ['num'],  # 29
                ['decimal'],  # 30
                ['bigdecimal'],  # 31
                ['bool'],  # 32
                ['text'],  # 33
                ['letter'],  # 34
                ['empty']  # 35
            ],

            '<parameter_list>': [
                ['<parameter>', '<parameter_list_tail>'],  # 36
                ['λ']  # 37
            ],

            '<parameter_list_tail>': [
                [',', '<parameter>', '<parameter_list_tail>'],  # 38
                ['λ']  # 39
            ],

            '<parameter>': [
                ['<datatype>', 'identifier']  # 40
            ],

            '<optional_return>': [
                ['give', '<return_tail>'],  # 41
                ['λ']  # 42
            ],

            '<return_tail>': [
                ['<stmt_value>', ';'],  # 43
                [';']  # 44
            ],

            # ============================================================
            # LOCAL DECLARATIONS (45-106) - uses <stmt_value> and <arg_value>
            # ============================================================

            '<local_declarations>': [
                ['<declaration>', '<local_declarations>'],  # 45
                ['λ']  # 46
            ],

            '<declaration>': [
                ['<local_declaration>'],  # 47
                ['<fixed_declaration>'],  # 48
                ['<list_declaration>']  # 49
            ],

            '<local_declaration>': [
                ['identifier', 'identifier', ';'],  # 50 - custom type
                ['num', 'identifier', '=', '<stmt_value>', ';'],  # 51
                ['decimal', 'identifier', '=', '<stmt_value>', ';'],  # 52
                ['bigdecimal', 'identifier', '=', '<stmt_value>', ';'],  # 53
                ['bool', 'identifier', '=', '<stmt_value>', ';'],  # 54
                ['text', 'identifier', '=', '<stmt_value>', ';'],  # 55
                ['letter', 'identifier', '=', '<stmt_value>', ';']  # 56
            ],

            '<fixed_declaration>': [
                ['fixed', '<fixed_typed_decl>']  # 57
            ],

            '<fixed_typed_decl>': [
                ['num', 'identifier', '=', '<stmt_value>', ';'],  # 58
                ['decimal', 'identifier', '=', '<stmt_value>', ';'],  # 59
                ['bigdecimal', 'identifier', '=', '<stmt_value>', ';'],  # 60
                ['bool', 'identifier', '=', '<stmt_value>', ';'],  # 61
                ['text', 'identifier', '=', '<stmt_value>', ';'],  # 62
                ['letter', 'identifier', '=', '<stmt_value>', ';']  # 63
            ],

            '<list_declaration>': [
                ['list', '<list_typed_decl>']  # 64
            ],

            '<list_typed_decl>': [
                ['num', 'identifier', '=', '<num_list>', ';'],  # 65
                ['decimal', 'identifier', '=', '<num_list>', ';'],  # 66
                ['bigdecimal', 'identifier', '=', '<num_list>', ';'],  # 67
                ['bool', 'identifier', '=', '<bool_list>', ';'],  # 68
                ['text', 'identifier', '=', '<expr_list>', ';'],  # 69
                ['letter', 'identifier', '=', '<expr_list>', ';']  # 70
            ],

            # List literals - use <arg_value>
            '<num_list>': [
                ['<num_list_1d>'],  # 71
                ['<num_list_2d>']  # 72
            ],

            '<num_list_1d>': [
                ['[', '<num_list_elems>', ']']  # 73
            ],

            '<num_list_elems>': [
                ['<arg_value>', '<num_list_tail>'],  # 74
                ['λ']  # 75
            ],

            '<num_list_tail>': [
                [',', '<arg_value>', '<num_list_tail>'],  # 76
                ['λ']  # 77
            ],

            '<num_list_2d>': [
                ['[', '<num_list_rows>', ']']  # 78
            ],

            '<num_list_rows>': [
                ['<num_list_1d>', '<num_list_rows_tail>'],  # 79
                ['λ']  # 80
            ],

            '<num_list_rows_tail>': [
                [',', '<num_list_1d>', '<num_list_rows_tail>'],  # 81
                ['λ']  # 82
            ],

            '<bool_list>': [
                ['<bool_list_1d>'],  # 83
                ['<bool_list_2d>']  # 84
            ],

            '<bool_list_1d>': [
                ['[', '<bool_list_elems>', ']']  # 85
            ],

            '<bool_list_elems>': [
                ['<arg_value>', '<bool_list_tail>'],  # 86
                ['λ']  # 87
            ],

            '<bool_list_tail>': [
                [',', '<arg_value>', '<bool_list_tail>'],  # 88
                ['λ']  # 89
            ],

            '<bool_list_2d>': [
                ['[', '<bool_list_rows>', ']']  # 90
            ],

            '<bool_list_rows>': [
                ['<bool_list_1d>', '<bool_list_rows_tail>'],  # 91
                ['λ']  # 92
            ],

            '<bool_list_rows_tail>': [
                [',', '<bool_list_1d>', '<bool_list_rows_tail>'],  # 93
                ['λ']  # 94
            ],

            '<expr_list>': [
                ['<expr_list_1d>'],  # 95
                ['<expr_list_2d>']  # 96
            ],

            '<expr_list_1d>': [
                ['[', '<expr_list_elems>', ']']  # 97
            ],

            '<expr_list_elems>': [
                ['<arg_value>', '<expr_list_tail>'],  # 98
                ['λ']  # 99
            ],

            '<expr_list_tail>': [
                [',', '<arg_value>', '<expr_list_tail>'],  # 100
                ['λ']  # 101
            ],

            '<expr_list_2d>': [
                ['[', '<expr_list_rows>', ']']  # 102
            ],

            '<expr_list_rows>': [
                ['<expr_list_1d>', '<expr_list_rows_tail>'],  # 103
                ['λ']  # 104
            ],

            '<expr_list_rows_tail>': [
                [',', '<expr_list_1d>', '<expr_list_rows_tail>'],  # 105
                ['λ']  # 106
            ],

            # ============================================================
            # STATEMENTS (107-113)
            # ============================================================

            '<statements>': [
                ['<statement>', '<statements>'],  # 107
                ['λ']  # 108
            ],

            '<statement>': [
                ['<control_statement>'],  # 109
                ['<assignment_statement>'],  # 110
                ['<function_call_statement>'],  # 111
                ['<declaration>'],  # 112
                ['<io_statement>']  # 113
            ],

            # ============================================================
            # ASSIGNMENT STATEMENTS (114-129) - uses <stmt_value> and <index_value>
            # ============================================================

            '<assignment_statement>': [
                ['<assignable>', '<assignment_tail>']  # 114
            ],

            '<assignment_tail>': [
                ['=', '<stmt_value>', ';'],  # 115
                ['+=', '<stmt_value>', ';'],  # 116
                ['-=', '<stmt_value>', ';'],  # 117
                ['*=', '<stmt_value>', ';'],  # 118
                ['/=', '<stmt_value>', ';'],  # 119
                ['%=', '<stmt_value>', ';'],  # 120
                ['**=', '<stmt_value>', ';'],  # 121
                ['++', ';'],  # 122
                ['--', ';']  # 123
            ],

            '<assignable>': [
                ['identifier', '<assignable_suffix>']  # 124
            ],

            '<assignable_suffix>': [
                ['[', '<index_value>', ']', '<assignable_2d>'],  # 125
                ['.', 'identifier'],  # 126
                ['λ']  # 127
            ],

            '<assignable_2d>': [
                ['[', '<index_value>', ']'],  # 128
                ['λ']  # 129
            ],

            # ============================================================
            # FUNCTION CALLS (130-135) - uses <arg_value>
            # ============================================================

            '<function_call_statement>': [
                ['<function_call>', ';']  # 130
            ],

            '<function_call>': [
                ['identifier', '(', '<arg_list>', ')']  # 131
            ],

            '<arg_list>': [
                ['<arg_value>', '<arg_list_tail>'],  # 132
                ['λ']  # 133
            ],

            '<arg_list_tail>': [
                [',', '<arg_value>', '<arg_list_tail>'],  # 134
                ['λ']  # 135
            ],

            # ============================================================
            # I/O STATEMENTS (136-137)
            # ============================================================

            '<io_statement>': [
                ['show', '(', '<arg_list>', ')', ';'],  # 136
                ['read', '(', 'identifier', ')', ';']  # 137
            ],

            # ============================================================
            # CONTROL STATEMENTS (138-164)
            # ============================================================

            '<control_statement>': [
                ['<check_structure>'],  # 138
                ['<select_statement>'],  # 139
                ['<iterative_statement>']  # 140
            ],

            # CHECK - uses <cond_value>
            '<check_structure>': [
                ['check', '(', '<cond_value>', ')',
                 '{', '<statements>', '}', '<otherwise_chain>']  # 141
            ],

            '<otherwise_chain>': [
                ['otherwisecheck', '(', '<cond_value>', ')',
                 '{', '<statements>', '}', '<otherwise_chain>'],  # 142
                ['otherwise', '{', '<statements>', '}'],  # 143
                ['λ']  # 144
            ],

            # SELECT - uses <cond_value>
            '<select_statement>': [
                ['select', '(', '<cond_value>', ')',
                 '{', '<option_blocks>', '<optional_fallback>', '}']  # 145
            ],

            '<option_blocks>': [
                ['<option_block>', '<option_blocks>'],  # 146
                ['λ']  # 147
            ],

            '<option_block>': [
                ['option', '<literal>', ':', '<statements>',
                    '<control_flow>', ';']  # 148
            ],

            '<control_flow>': [
                ['stop'],  # 149
                ['skip']  # 150
            ],

            '<optional_fallback>': [
                ['fallback', ':', '{', '<statements>', '}'],  # 151
                ['λ']  # 152
            ],

            # LOOPS
            '<iterative_statement>': [
                ['<each_loop>'],  # 153
                ['<during_loop>']  # 154
            ],

            # EACH - uses <from_primary>, <to_primary>, <step_primary>
            '<each_loop>': [
                ['each', 'identifier', 'from', '<from_primary>', 'to',
                    # 155
                    '<to_primary>', '<step_clause>', '{', '<statements>', '}']
            ],

            '<step_clause>': [
                ['step', '<step_primary>'],  # 156
                ['λ']  # 157
            ],

            # DURING - uses <cond_value>
            '<during_loop>': [
                ['during', '(', '<cond_value>', ')',
                 '{', '<statements>', '}']  # 158
            ],

            # LITERALS
            '<literal>': [
                ['num_lit'],  # 159
                ['decimal_lit'],  # 160
                ['string_lit'],  # 161
                ['char_lit'],  # 162
                ['Yes'],  # 163
                ['No']  # 164
            ],

            # ============================================================
            # STMT_VALUE HIERARCHY (165-209)
            # Context: declarations, assignments, returns
            # FOLLOW: {';'}
            # ============================================================

            '<stmt_value>': [['<stmt_or>']],  # 165

            '<stmt_or>': [['<stmt_and>', '<stmt_or_tail>']],  # 166
            '<stmt_or_tail>': [
                ['||', '<stmt_and>', '<stmt_or_tail>'],  # 167
                ['λ']  # 168
            ],

            '<stmt_and>': [['<stmt_eq>', '<stmt_and_tail>']],  # 169
            '<stmt_and_tail>': [
                ['&&', '<stmt_eq>', '<stmt_and_tail>'],  # 170
                ['λ']  # 171
            ],

            '<stmt_eq>': [['<stmt_rel>', '<stmt_eq_tail>']],  # 172
            '<stmt_eq_tail>': [
                ['==', '<stmt_rel>', '<stmt_eq_tail>'],  # 173
                ['!=', '<stmt_rel>', '<stmt_eq_tail>'],  # 174
                ['λ']  # 175
            ],

            '<stmt_rel>': [['<stmt_add>', '<stmt_rel_tail>']],  # 176
            '<stmt_rel_tail>': [
                ['>', '<stmt_add>'],  # 177
                ['<', '<stmt_add>'],  # 178
                ['>=', '<stmt_add>'],  # 179
                ['<=', '<stmt_add>'],  # 180
                ['λ']  # 181
            ],

            '<stmt_add>': [['<stmt_mult>', '<stmt_add_tail>']],  # 182
            '<stmt_add_tail>': [
                ['+', '<stmt_mult>', '<stmt_add_tail>'],  # 183
                ['-', '<stmt_mult>', '<stmt_add_tail>'],  # 184
                ['λ']  # 185
            ],

            '<stmt_mult>': [['<stmt_exp>', '<stmt_mult_tail>']],  # 186
            '<stmt_mult_tail>': [
                ['*', '<stmt_exp>', '<stmt_mult_tail>'],  # 187
                ['/', '<stmt_exp>', '<stmt_mult_tail>'],  # 188
                ['%', '<stmt_exp>', '<stmt_mult_tail>'],  # 189
                ['λ']  # 190
            ],

            '<stmt_exp>': [['<stmt_unary>', '<stmt_exp_tail>']],  # 191
            '<stmt_exp_tail>': [
                ['**', '<stmt_exp>'],  # 192
                ['λ']  # 193
            ],

            '<stmt_unary>': [
                ['-', '<stmt_post>'],  # 194
                ['!', '<stmt_post>'],  # 195
                ['<stmt_post>']  # 196
            ],

            # 197 - No postfix operators (++ and -- are statements, not expressions)
            '<stmt_post>': [['<stmt_prim>']],

            '<stmt_prim>': [
                ['(', '<stmt_value>', ')'],  # 201
                ['<literal>'],  # 202
                ['identifier', '<stmt_id_suffix>'],  # 203
                ['<size_call>']  # 204 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<stmt_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 204
                ['[', '<index_value>', ']', '<stmt_var_2d>'],  # 205
                ['.', 'identifier'],  # 206
                ['λ']  # 207
            ],

            '<stmt_var_2d>': [
                ['[', '<index_value>', ']'],  # 208
                ['λ']  # 209
            ],

            # ============================================================
            # ARG_VALUE HIERARCHY (210-254)
            # Context: function arguments, list elements
            # FOLLOW: {',', ')', ']'}
            # ============================================================

            '<arg_value>': [['<arg_or>']],  # 210

            '<arg_or>': [['<arg_and>', '<arg_or_tail>']],  # 211
            '<arg_or_tail>': [
                ['||', '<arg_and>', '<arg_or_tail>'],  # 212
                ['λ']  # 213
            ],

            '<arg_and>': [['<arg_eq>', '<arg_and_tail>']],  # 214
            '<arg_and_tail>': [
                ['&&', '<arg_eq>', '<arg_and_tail>'],  # 215
                ['λ']  # 216
            ],

            '<arg_eq>': [['<arg_rel>', '<arg_eq_tail>']],  # 217
            '<arg_eq_tail>': [
                ['==', '<arg_rel>', '<arg_eq_tail>'],  # 218
                ['!=', '<arg_rel>', '<arg_eq_tail>'],  # 219
                ['λ']  # 220
            ],

            '<arg_rel>': [['<arg_add>', '<arg_rel_tail>']],  # 221
            '<arg_rel_tail>': [
                ['>', '<arg_add>'],  # 222
                ['<', '<arg_add>'],  # 223
                ['>=', '<arg_add>'],  # 224
                ['<=', '<arg_add>'],  # 225
                ['λ']  # 226
            ],

            '<arg_add>': [['<arg_mult>', '<arg_add_tail>']],  # 227
            '<arg_add_tail>': [
                ['+', '<arg_mult>', '<arg_add_tail>'],  # 228
                ['-', '<arg_mult>', '<arg_add_tail>'],  # 229
                ['λ']  # 230
            ],

            '<arg_mult>': [['<arg_exp>', '<arg_mult_tail>']],  # 231
            '<arg_mult_tail>': [
                ['*', '<arg_exp>', '<arg_mult_tail>'],  # 232
                ['/', '<arg_exp>', '<arg_mult_tail>'],  # 233
                ['%', '<arg_exp>', '<arg_mult_tail>'],  # 234
                ['λ']  # 235
            ],

            '<arg_exp>': [['<arg_unary>', '<arg_exp_tail>']],  # 236
            '<arg_exp_tail>': [
                ['**', '<arg_exp>'],  # 237
                ['λ']  # 238
            ],

            '<arg_unary>': [
                ['-', '<arg_post>'],  # 239
                ['!', '<arg_post>'],  # 240
                ['<arg_post>']  # 241
            ],

            '<arg_post>': [['<arg_prim>']],  # 242 - No postfix operators

            '<arg_prim>': [
                ['(', '<arg_value>', ')'],  # 246
                ['<literal>'],  # 247
                ['identifier', '<arg_id_suffix>'],  # 248
                ['<size_call>']  # 249 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<arg_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 249
                ['[', '<index_value>', ']', '<arg_var_2d>'],  # 250
                ['.', 'identifier'],  # 251
                ['λ']  # 252
            ],

            '<arg_var_2d>': [
                ['[', '<index_value>', ']'],  # 253
                ['λ']  # 254
            ],

            # ============================================================
            # COND_VALUE HIERARCHY (255-305)
            # Context: check, during, select conditions
            # FOLLOW: {')'}
            # ============================================================

            '<cond_value>': [['<cond_or>']],  # 255

            '<cond_or>': [['<cond_and>', '<cond_or_tail>']],  # 256
            '<cond_or_tail>': [
                ['||', '<cond_and>', '<cond_or_tail>'],  # 257
                ['λ']  # 258
            ],

            '<cond_and>': [['<cond_eq>', '<cond_and_tail>']],  # 259
            '<cond_and_tail>': [
                ['&&', '<cond_eq>', '<cond_and_tail>'],  # 260
                ['λ']  # 261
            ],

            '<cond_eq>': [['<cond_comp>', '<cond_eq_tail>']],  # 262
            '<cond_eq_tail>': [
                ['==', '<cond_comp>', '<cond_eq_tail>'],  # 263
                ['!=', '<cond_comp>', '<cond_eq_tail>'],  # 264
                ['λ']  # 265
            ],

            '<cond_comp>': [['<cond_unary>']],  # 266

            '<cond_unary>': [
                ['!', '<cond_base>'],  # 267
                ['<cond_base>']  # 268
            ],

            '<cond_base>': [
                ['Yes'],  # 269
                ['No'],  # 270
                ['<cond_arith>', '<cond_rel_tail>']  # 271
            ],

            '<cond_rel_tail>': [
                # Second operand uses <cond_arith_no_rel> to prevent chaining (a < b == c)
                # NO λ - comparison is REQUIRED (enforces boolean expressions)
                ['>', '<cond_arith_no_rel>'],   # 272
                ['<', '<cond_arith_no_rel>'],   # 273
                ['>=', '<cond_arith_no_rel>'],  # 274
                ['<=', '<cond_arith_no_rel>'],  # 275
                ['==', '<cond_arith_no_rel>'],  # 276 - equality
                ['!=', '<cond_arith_no_rel>']   # 277 - inequality
                # λ REMOVED - check(x + 5) now INVALID
            ],

            # Arithmetic without relational tail (used as second operand in comparisons)
            '<cond_arith_no_rel>': [['<cond_add_no_rel>']],  # 277

            # 278
            '<cond_add_no_rel>': [['<cond_mult_no_rel>', '<cond_add_tail_no_rel>']],
            '<cond_add_tail_no_rel>': [
                ['+', '<cond_mult_no_rel>', '<cond_add_tail_no_rel>'],  # 279
                ['-', '<cond_mult_no_rel>', '<cond_add_tail_no_rel>'],  # 280
                ['λ']  # 281
            ],

            # 282
            '<cond_mult_no_rel>': [['<cond_exp_no_rel>', '<cond_mult_tail_no_rel>']],
            '<cond_mult_tail_no_rel>': [
                ['*', '<cond_exp_no_rel>', '<cond_mult_tail_no_rel>'],  # 283
                ['/', '<cond_exp_no_rel>', '<cond_mult_tail_no_rel>'],  # 284
                ['%', '<cond_exp_no_rel>', '<cond_mult_tail_no_rel>'],  # 285
                ['λ']  # 286
            ],

            # 287
            '<cond_exp_no_rel>': [['<cond_arith_unary_no_rel>', '<cond_exp_tail_no_rel>']],
            '<cond_exp_tail_no_rel>': [
                ['**', '<cond_exp_no_rel>'],  # 288
                ['λ']  # 289
            ],

            '<cond_arith_unary_no_rel>': [
                ['-', '<cond_post_no_rel>'],  # 290
                ['<cond_post_no_rel>']  # 291
            ],

            # 292 - No postfix operators
            '<cond_post_no_rel>': [['<cond_prim_no_rel>']],

            '<cond_prim_no_rel>': [
                ['(', '<cond_value>', ')'],  # 296
                ['num_lit'],  # 297
                ['decimal_lit'],  # 298
                ['identifier', '<cond_id_suffix_no_rel>'],  # 299
                ['<size_call>']  # 300 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<cond_id_suffix_no_rel>': [
                ['(', '<arg_list>', ')'],  # 300
                ['[', '<index_value>', ']', '<cond_var_2d_no_rel>'],  # 301
                ['.', 'identifier'],  # 302
                ['λ']  # 303
            ],

            '<cond_var_2d_no_rel>': [
                ['[', '<index_value>', ']'],  # 304
                ['λ']  # 305
            ],

            # Regular arithmetic (can have relational tail)
            '<cond_arith>': [['<cond_add>']],  # 306

            '<cond_add>': [['<cond_mult>', '<cond_add_tail>']],  # 278
            '<cond_add_tail>': [
                ['+', '<cond_mult>', '<cond_add_tail>'],  # 279
                ['-', '<cond_mult>', '<cond_add_tail>'],  # 280
                ['λ']  # 281
            ],

            '<cond_mult>': [['<cond_exp>', '<cond_mult_tail>']],  # 282
            '<cond_mult_tail>': [
                ['*', '<cond_exp>', '<cond_mult_tail>'],  # 283
                ['/', '<cond_exp>', '<cond_mult_tail>'],  # 284
                ['%', '<cond_exp>', '<cond_mult_tail>'],  # 285
                ['λ']  # 286
            ],

            '<cond_exp>': [['<cond_arith_unary>', '<cond_exp_tail>']],  # 287
            '<cond_exp_tail>': [
                ['**', '<cond_exp>'],  # 288
                ['λ']  # 289
            ],

            '<cond_arith_unary>': [
                ['-', '<cond_post>'],  # 290
                ['<cond_post>']  # 291
            ],

            # 292 - No postfix operators in conditions
            '<cond_post>': [['<cond_prim>']],

            '<cond_prim>': [
                ['(', '<cond_value>', ')'],  # 296
                ['num_lit'],  # 297
                ['decimal_lit'],  # 298
                ['identifier', '<cond_id_suffix>'],  # 299
                ['<size_call>']  # 300 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<cond_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 300
                ['[', '<index_value>', ']', '<cond_var_2d>'],  # 301
                ['.', 'identifier'],  # 302
                ['λ']  # 303
            ],

            '<cond_var_2d>': [
                ['[', '<index_value>', ']'],  # 304
                ['λ']  # 305
            ],

            # ============================================================
            # INDEX_VALUE HIERARCHY (306-334)
            # Context: array indices
            # FOLLOW: {']'}
            # ============================================================

            '<index_value>': [['<index_add>']],  # 306

            '<index_add>': [['<index_mult>', '<index_add_tail>']],  # 307
            '<index_add_tail>': [
                ['+', '<index_mult>', '<index_add_tail>'],  # 308
                ['-', '<index_mult>', '<index_add_tail>'],  # 309
                ['λ']  # 310
            ],

            '<index_mult>': [['<index_exp>', '<index_mult_tail>']],  # 311
            '<index_mult_tail>': [
                ['*', '<index_exp>', '<index_mult_tail>'],  # 312
                ['/', '<index_exp>', '<index_mult_tail>'],  # 313
                ['%', '<index_exp>', '<index_mult_tail>'],  # 314
                ['λ']  # 315
            ],

            '<index_exp>': [['<index_unary>', '<index_exp_tail>']],  # 316
            '<index_exp_tail>': [
                ['**', '<index_exp>'],  # 317
                ['λ']  # 318
            ],

            '<index_unary>': [
                ['-', '<index_post>'],  # 319
                ['<index_post>']  # 320
            ],

            '<index_post>': [['<index_prim>']],  # 321 - No postfix operators

            '<index_prim>': [
                ['(', '<index_value>', ')'],  # 325
                ['num_lit'],  # 326
                ['decimal_lit'],  # 327
                ['identifier', '<index_id_suffix>'],  # 328
                ['<size_call>']  # 329 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<index_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 329
                ['[', '<index_value>', ']', '<index_var_2d>'],  # 330
                ['.', 'identifier'],  # 331
                ['λ']  # 332
            ],

            '<index_var_2d>': [
                ['[', '<index_value>', ']'],  # 333
                ['λ']  # 334
            ],

            # ============================================================
            # FROM_PRIMARY (365-373)
            # Context: loop FROM value
            # FOLLOW: {'to'}
            # PRIMARY ONLY - NO OPERATORS!
            # ============================================================

            '<from_primary>': [
                ['num_lit'],  # 365
                ['decimal_lit'],  # 366
                ['identifier', '<from_id_suffix>'],  # 367
                ['<size_call>']  # 368 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<from_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 368
                ['[', '<index_value>', ']', '<from_var_2d>'],  # 369
                ['.', 'identifier'],  # 370
                ['λ']  # 371
            ],

            '<from_var_2d>': [
                ['[', '<index_value>', ']'],  # 372
                ['λ']  # 373
            ],

            # ============================================================
            # TO_PRIMARY (374-382)
            # Context: loop TO value
            # FOLLOW: {'step', '{'}
            # PRIMARY ONLY - NO OPERATORS!
            # ============================================================

            '<to_primary>': [
                ['num_lit'],  # 374
                ['decimal_lit'],  # 375
                ['identifier', '<to_id_suffix>'],  # 376
                ['<size_call>']  # 377 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<to_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 377
                ['[', '<index_value>', ']', '<to_var_2d>'],  # 378
                ['.', 'identifier'],  # 379
                ['λ']  # 380
            ],

            '<to_var_2d>': [
                ['[', '<index_value>', ']'],  # 381
                ['λ']  # 382
            ],

            # ============================================================
            # STEP_PRIMARY (383-391)
            # Context: loop STEP value
            # FOLLOW: {'{'}
            # PRIMARY ONLY - NO OPERATORS!
            # ============================================================

            '<step_primary>': [
                ['num_lit'],  # 383
                ['decimal_lit'],  # 384
                ['identifier', '<step_id_suffix>'],  # 385
                ['<size_call>']  # 386 - size(IDENTIFIER) or size(IDENTIFIER, 0)
            ],

            '<step_id_suffix>': [
                ['(', '<arg_list>', ')'],  # 386
                ['[', '<index_value>', ']', '<step_var_2d>'],  # 387
                ['.', 'identifier'],  # 388
                ['λ']  # 389
            ],

            '<step_var_2d>': [
                ['[', '<index_value>', ']'],  # 390
                ['λ']  # 391
            ],

            # ============================================================
            # SIZE BUILT-IN FUNCTION (375-377)
            # Returns size of array. 1D: total elements. 2D: rows (default) or columns (with ,0)
            # ============================================================

            '<size_call>': [
                ['size', '(', 'identifier', '<size_second_arg>', ')']  # 375
            ],

            '<size_second_arg>': [
                [',', 'num_lit'],  # 376
                ['λ']  # 377
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
                elif top in ['<num_list>', '<bool_list>', '<expr_list>'] and current == '[':
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
                        # 2D: [ [ ... ] ]
                        if top == '<num_list>':
                            production = ['<num_list_2d>']
                        elif top == '<bool_list>':
                            production = ['<bool_list_2d>']
                        else:  # <expr_list>
                            production = ['<expr_list_2d>']
                    else:
                        # 1D: [ values ]
                        if top == '<num_list>':
                            production = ['<num_list_1d>']
                        elif top == '<bool_list>':
                            production = ['<bool_list_1d>']
                        else:  # <expr_list>
                            production = ['<expr_list_1d>']

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

                        self.stack.pop()
                        if production != ['λ']:
                            for symbol in reversed(production):
                                self.stack.append(symbol)

                        self.derivations.append((top, production))
                    else:
                        # Context-specific error message
                        expected = sorted(
                            set(term for (nt, term) in self.table.keys() if nt == top))
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
