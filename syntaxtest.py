class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
        self.context_stack = []  # Track parsing context for better errors

    def error(self, expected_tokens=None, context=None):
        """Enhanced error with context-aware FOLLOW sets"""
        token = self.current_token
        prev_token = self.tokens[self.pos - 1] if self.pos > 0 else None

        # Format previous token
        if prev_token:
            prev_str = f"'{prev_token.value}'" if prev_token.value else f"'{prev_token.type}'"
        else:
            prev_str = "start of file"

        # Format current token
        if token:
            current_str = f"'{token.value}'" if token.value else f"'{token.type}'"
        else:
            current_str = "EOF"

        # Use context to determine proper FOLLOW set
        if context:
            expected_str = self._get_follow_set_string(context)
        elif expected_tokens:
            if isinstance(expected_tokens, str):
                expected_str = expected_tokens
            elif isinstance(expected_tokens, (list, tuple)):
                expected_str = ", ".join(f"'{t}'" for t in expected_tokens)
            else:
                expected_str = str(expected_tokens)
        else:
            expected_str = "valid token"

        # Build error message
        error_msg = f"Unexpected token after {prev_str}\n"
        error_msg += f"Expected: {expected_str}\n"
        error_msg += f"Got: {current_str}"

        if token and hasattr(token, 'pos_start'):
            line = token.pos_start.ln + 1
            col = token.pos_start.col + 1
            raise SyntaxError(
                f"Syntax Error at Line {line}, Column {col}\n{error_msg}")
        else:
            raise SyntaxError(f"Syntax Error\n{error_msg}")

    def _get_follow_set_string(self, context):
        """Return FOLLOW set as formatted string based on parsing context"""
        follow_sets = {
            # Expression contexts
            'expression_in_statement': "';', '+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', or '||'",
            'expression_in_paren': "'+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', '||', or ')'",
            'expression_in_list_literal': "'+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', '||', ',', or ']'",
            'expression_in_list_access': "'+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', '||', or ']'",
            'expression_in_argument': "'+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', '||', ',', or ')'",
            'expression_in_assignment': "';', '+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', or '||'",
            'expression_in_return': "';', '+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', or '||'",
            'expression_in_condition': "'+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', '||', or ')'",
            'expression_in_each': "'+', '-', '*', '/', '%', '**', '>', '<', '>=', '<=', '==', '!=', '&&', '||', 'to', or 'step'",

            # Statement contexts
            'statement': "'check', 'select', 'each', 'during', 'show', 'read', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'fixed', 'list', 'identifier', or '}'",
            'statements_in_function': "'check', 'select', 'each', 'during', 'show', 'read', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'fixed', 'list', 'identifier', 'give', or '}'",
            'statements_in_block': "'check', 'select', 'each', 'during', 'show', 'read', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'fixed', 'list', 'identifier', or '}'",
            'statements_in_option': "'check', 'select', 'each', 'during', 'show', 'read', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'fixed', 'list', 'identifier', 'stop', or 'skip'",

            # Declaration contexts
            'after_datatype': "identifier",
            'after_identifier_in_declaration': "';', '=', or identifier",
            # Production 18: function definition requires '('
            'after_identifier_in_function': "'('",
            # Production 4: group definition requires '{'
            'after_identifier_in_group': "'{'",
            'after_equals': "expression (identifier, literal, '(', '-', or '!')",
            'after_equals_in_list': "'['",

            'after_expression_in_list_access': "']'",
            'after_list_content': "']'",

            # Function contexts - SPLIT INTO TWO
            'parameter_list_start': "'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', or ')'",
            'parameter_list_tail': "',', or ')'",
            'argument_list': "expression, ',', or ')'",

            # Control flow contexts
            'after_check': "'('",
            'after_condition': "')'",
            'after_control_keyword': "'{'",
            'option_block': "'option', 'fallback', or '}'",

            # List contexts
            'list_literal': "expression, ',', ']', or '['",

            # General
            'after_semicolon': "next statement or '}'",
            'after_open_brace': "statement or '}'",
            'after_close_brace': "next statement, 'otherwise', 'otherwisecheck', 'finish', or '}'",
            'after_identifier_in_group_member': "';'",
            'after_identifier_in_function_call': "'('",
            'after_assignable': "';', '=', '+=', '-=', '*=', '/=', '%=', '**=', '++', or '--'",
            'control_flow': "'stop' or 'skip'",
            'datatype': "'num', 'decimal', 'bigdecimal', 'letter', 'text', or 'bool'",
            'return_type': "'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', or 'empty'",
            'literal': "'NUM_LIT', 'DECIMAL_LIT', 'STRING_LIT', 'CHAR_LIT', 'Yes', or 'No'",
            'factor': "literal, identifier, or function call",
            'after_identifier_in_local_declaration': "'='",
            'after_identifier_in_custom_type_declaration': "';'",
            'after_function_call_for_statement': "';'",
            'after_option_literal': "':'",
        }

        return follow_sets.get(context, "valid token")

    def advance(self):
        """Move to next token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, *expected):
        """Check if current token type matches any of the expected"""
        if self.current_token is None:
            return False
        return self.current_token.type in expected

    def expect(self, token_type, context=None):
        """Consume a token of expected type or error with context"""
        if not self.match(token_type):
            if context:
                self.error(context=context)
            else:
                self.error(f"'{token_type}'")
        self.advance()

    # ===== PARSING METHODS =====

    def parse(self):
        """Entry point - parse entire program"""
        self.parse_program()
        return "SUCCESS"

    def parse_program(self):
        # Production 1
        self.parse_program_definitions()
        self.parse_main_program()

    def parse_program_definitions(self):
        # Productions 2-3
        while self.match('group', 'worldwide', 'define'):
            if self.match('group'):
                self.parse_group_definition()
            elif self.match('worldwide'):
                self.parse_global_declaration()
            elif self.match('define'):
                self.parse_function_definition()

    def parse_group_definition(self):
        # Production 4-5
        if not self.match('group'):
            return
        self.expect('group')
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect('{', 'after_identifier_in_group')
        self.parse_group_member_list()
        self.expect('}', 'after_close_brace')

    def parse_group_member_list(self):
        # Production 6
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_group_member()
            self.parse_group_member_tail()

    def parse_group_member_tail(self):
        # Productions 7-8
        while self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_group_member()

    def parse_group_member(self):
        # Production 9
        self.parse_datatype()
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect(';', 'after_identifier_in_group_member')

    def parse_global_declaration(self):
        # Production 10-11
        if not self.match('worldwide'):
            return
        self.expect('worldwide')
        self.parse_datatype()
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect('=', 'after_identifier_in_declaration')
        self.parse_expression('expression_in_assignment')
        self.expect(';', 'expression_in_statement')

    def parse_datatype(self):
        # Productions 12-17
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.advance()
        else:
            self.error(context='datatype')

    def parse_function_definition(self):
        # Production 20-21
        if not self.match('define'):
            return
        self.expect('define')
        self.parse_return_type()
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect('(', 'after_identifier_in_function')
        self.parse_parameter_list()
        self.expect(')', 'parameter_list_tail')
        self.expect('{', 'after_control_keyword')
        self.parse_local_declarations()
        self.parse_statements('statements_in_function')
        self.parse_optional_return()
        self.expect('}', 'after_close_brace')

    def parse_return_type(self):
        # Productions 22-23
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_datatype()
        elif self.match('empty'):
            self.advance()
        else:
            self.error(context='return_type')

    def parse_parameter_list(self):
        # Productions 26-27
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_parameter()
            self.parse_parameter_list_tail()
        elif not self.match(')'):
            # Error: expected parameter or closing paren
            self.error(context='parameter_list_start')

    def parse_parameter_list_tail(self):
        # Productions 28-29
        while self.match(','):
            self.advance()
            self.parse_parameter()

        # After all parameters, we must see ')'
        if not self.match(')'):
            self.error(context='parameter_list_tail')

    def parse_parameter(self):
        # Production 30
        self.parse_datatype()
        self.expect('IDENTIFIER', 'after_datatype')

    def parse_local_declarations(self):
        # Productions 20-21
        while self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_local_declaration()

        # Check for custom type declarations (identifier identifier;)
        if self.match('IDENTIFIER'):
            saved_pos = self.pos
            self.advance()

            if self.match('IDENTIFIER'):
                # Custom type declaration
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_local_declaration()
                # Recursively check for more declarations
                self.parse_local_declarations()
            else:
                # Not a declaration, rewind
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]

    def parse_local_declaration(self):
        # Productions 40-41
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_datatype()
            self.expect('IDENTIFIER', 'after_datatype')
            self.expect('=', 'after_identifier_in_local_declaration')
            self.parse_expression('expression_in_assignment')
            self.expect(';', 'expression_in_statement')
        elif self.match('IDENTIFIER'):
            self.advance()
            self.expect('IDENTIFIER', 'after_datatype')
            self.expect(';', 'after_identifier_in_custom_type_declaration')

    def parse_optional_return(self):
        # Productions 31-32
        if self.match('give'):
            self.parse_return_statement()

    def parse_return_statement(self):
        # Production 33
        self.expect('give')
        self.parse_return_tail()

    def parse_return_tail(self):
        # Productions 34-35
        if self.match(';'):
            self.advance()
        else:
            self.parse_expression('expression_in_return')
            self.expect(';', 'expression_in_statement')

    def parse_main_program(self):
        # Production 36
        self.expect('start')
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')
        self.expect('finish')

    def parse_statements(self, context='statements_in_block'):
        # Productions 54-55
        while not self.match('}', 'option', 'fallback', 'stop', 'skip', 'give'):
            if self.current_token is None:
                break
            self.parse_statement(context)

    def parse_statement(self, context='statement'):
        # Productions 56-60
        if self.match('check', 'select', 'each', 'during'):
            self.parse_control_statement()
        elif self.match('show', 'read'):
            self.parse_io_statement()
        elif self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'fixed', 'list'):
            self.parse_declaration()
        elif self.match('IDENTIFIER'):
            saved_pos = self.pos
            self.advance()

            if self.match('IDENTIFIER'):
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_declaration()
            else:
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_assignment_or_call()
        else:
            self.error(context=context)

    def parse_assignment_or_call(self):
        saved_pos = self.pos
        self.advance()

        if self.match('('):
            self.pos = saved_pos
            self.current_token = self.tokens[self.pos]
            self.parse_function_call_statement()
        elif self.match('.', '[', '=', '+=', '-=', '*=', '/=', '%=', '**=', '++', '--'):
            self.pos = saved_pos
            self.current_token = self.tokens[self.pos]
            self.parse_assignment_statement()
        else:
            self.pos = saved_pos
            self.current_token = self.tokens[self.pos]
            self.parse_assignment_statement()

    def parse_declaration(self):
        # Productions 37-39
        if self.match('fixed'):
            self.parse_fixed_declaration()
        elif self.match('list'):
            self.parse_list_declaration()
        else:
            self.parse_local_declaration()

    def parse_fixed_declaration(self):
        # Production 42
        self.expect('fixed')
        self.parse_datatype()
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect('=', 'after_identifier_in_declaration')
        self.parse_expression('expression_in_assignment')
        self.expect(';', 'expression_in_statement')

    def parse_list_declaration(self):
        # Productions 41-44
        self.expect('list')
        self.parse_datatype()
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect('=', 'after_identifier_in_declaration')
        self.expect('[', 'after_equals_in_list')

        if self.match('['):
            self.parse_list_rows()
        else:
            self.parse_list_elements('expression_in_list_literal')

        self.expect(']', 'after_list_content')
        self.expect(';', 'after_semicolon')

    def parse_list_rows(self):
        if not self.match(']'):
            self.expect('[')
            self.parse_list_elements('expression_in_list')
            self.expect(']', 'list_literal')

            while self.match(','):
                self.advance()
                self.expect('[')
                self.parse_list_elements('expression_in_list')
                self.expect(']', 'list_literal')

    def parse_list_elements(self, context='expression_in_list_literal'):
        if not self.match(']'):
            self.parse_expression(context)
            while self.match(','):
                self.advance()
                self.parse_expression(context)

    def parse_assignment_statement(self):
        # Productions 61-63
        self.parse_assignable()

        if self.match('=', '+=', '-=', '*=', '/=', '%=', '**='):
            self.advance()
            self.parse_expression('expression_in_assignment')
            self.expect(';', 'expression_in_statement')
        elif self.match('++', '--'):
            self.advance()
            self.expect(';', 'after_semicolon')
        elif self.match(';'):
            # Production 63: <assignment_statement> ⇒ <assignable>;
            self.advance()
        else:
            self.error(context='after_assignable')

    def parse_assignable(self):
        # Productions 64-66: identifier | <list_access> | <group_member_access>
        # Productions 140-143: <list_access> handles 1D and 2D
        self.expect('IDENTIFIER')

        # Production 142: <list_access_1d> ⇒ identifier [ <expression> ]
        if self.match('['):
            self.advance()
            self.parse_expression('expression_in_list_access')  # ← CORRECT
            self.expect(']', 'after_expression_in_list_access')  # ← CORRECT

            # Production 143: <list_access_2d> ⇒ <list_access_1d> [ <expression> ]
            if self.match('['):
                self.advance()
                self.parse_expression('expression_in_list_access')  # ← CORRECT
                # ← CORRECT
                self.expect(']', 'after_expression_in_list_access')

        # Production 144: <group_member_access> ⇒ identifier . identifier
        elif self.match('.'):
            self.advance()
            self.expect('IDENTIFIER', 'after_datatype')

    def parse_function_call_statement(self):
        # Production 59: <function_call_statement> ⇒ <function_call> ;
        self.parse_function_call()
        # Semicolon is part of the STATEMENT, not the call
        self.expect(';', 'after_function_call_for_statement')

    def parse_function_call(self):
        # Production 60: <function_call> ⇒ identifier ( <argument_list> )
        self.expect('IDENTIFIER')
        self.expect('(', 'after_identifier_in_function_call')  # New context
        self.parse_argument_list()
        self.expect(')', 'argument_list')

    def parse_argument_list(self):
        # Productions 134-135
        if not self.match(')'):
            self.parse_expression('expression_in_argument')
            while self.match(','):
                self.advance()
                self.parse_expression('expression_in_argument')

    def parse_io_statement(self):
        # Productions 68-69
        if self.match('show'):
            self.expect('show')
            self.expect('(', 'after_check')
            self.parse_argument_list()
            self.expect(')', 'argument_list')
            self.expect(';', 'after_semicolon')
        elif self.match('read'):
            self.expect('read')
            self.expect('(', 'after_check')
            self.expect('IDENTIFIER', 'after_datatype')
            self.expect(')', 'after_condition')
            self.expect(';', 'after_semicolon')

    def parse_control_statement(self):
        # Productions 70-72
        if self.match('check'):
            self.parse_check_structure()
        elif self.match('select'):
            self.parse_select_statement()
        elif self.match('each', 'during'):
            self.parse_iterative_statement()

    def parse_check_structure(self):
        # Production 73
        self.parse_check_block()
        self.parse_otherwise_chain()

    def parse_check_block(self):
        # Production 74
        self.expect('check')
        self.expect('(', 'after_check')
        self.parse_expression('expression_in_condition')
        self.expect(')', 'after_condition')
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')

    def parse_otherwise_chain(self):
        # Productions 75-76
        while self.match('otherwisecheck'):
            self.parse_otherwise_check()

        if self.match('otherwise'):
            self.parse_otherwise_block()

    def parse_otherwise_check(self):
        # Production 79
        self.expect('otherwisecheck')
        self.expect('(', 'after_check')
        self.parse_expression('expression_in_condition')
        self.expect(')', 'after_condition')
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')

    def parse_otherwise_block(self):
        # Production 80
        self.expect('otherwise')
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')

    def parse_select_statement(self):
        # Production 81
        self.expect('select')
        self.expect('(', 'after_check')
        self.parse_expression('expression_in_condition')
        self.expect(')', 'after_condition')
        self.expect('{', 'after_control_keyword')
        self.parse_option_blocks()
        self.parse_optional_fallback()
        self.expect('}', 'option_block')

    def parse_option_blocks(self):
        # Productions 82-83
        while self.match('option'):
            self.parse_option_block()

    def parse_option_block(self):
        # Production 84
        self.expect('option')
        self.parse_literal()
        self.expect(':', 'after_option_literal')
        self.parse_statements('statements_in_option')
        self.parse_control_flow()
        self.expect(';', 'after_semicolon')

    def parse_control_flow(self):
        # Productions 84-85
        if self.match('stop', 'skip'):
            self.advance()
        else:
            self.error(context='control_flow')

    def parse_optional_fallback(self):
        # Productions 87-88
        if self.match('fallback'):
            self.parse_fallback_block()

    def parse_fallback_block(self):
        # Production 89
        self.expect('fallback')
        self.expect(':', 'after_identifier_in_declaration')
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')

    def parse_iterative_statement(self):
        # Productions 90-91
        if self.match('each'):
            self.parse_each_loop()
        elif self.match('during'):
            self.parse_during_loop()

    def parse_each_loop(self):
        # Production 92
        self.expect('each')
        self.expect('IDENTIFIER', 'after_datatype')
        self.expect('from')
        self.parse_expression('expression_in_each')
        self.expect('to', 'expression_in_each')
        self.parse_expression('expression_in_each')
        self.parse_step_clause()
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')

    def parse_step_clause(self):
        # Productions 92-93
        if self.match('step'):
            self.advance()
            self.parse_expression('expression_in_each')  # ← CORRECT

    def parse_during_loop(self):
        # Production 95
        self.expect('during')
        self.expect('(', 'after_check')
        self.parse_expression('expression_in_condition')
        self.expect(')', 'after_condition')
        self.expect('{', 'after_control_keyword')
        self.parse_statements('statements_in_block')
        self.expect('}', 'after_close_brace')

    # ===== EXPRESSION PARSING =====

    def parse_expression(self, context='expression_in_statement'):
        # Production 96
        return self.parse_logical_or(context)

    def parse_logical_or(self, context):
        # Productions 97-98
        left = self.parse_logical_and(context)

        while self.match('||'):
            self.advance()
            right = self.parse_logical_and(context)

        return left

    def parse_logical_and(self, context):
        # Productions 99-100
        left = self.parse_equality(context)

        while self.match('&&'):
            self.advance()
            right = self.parse_equality(context)

        return left

    def parse_equality(self, context):
        # Productions 101-104
        left = self.parse_relational(context)

        while self.match('==', '!='):
            self.advance()
            right = self.parse_relational(context)

        return left

    def parse_relational(self, context):
        # Productions 105-110
        left = self.parse_additive(context)

        while self.match('>', '<', '>=', '<='):
            self.advance()
            right = self.parse_additive(context)

        return left

    def parse_additive(self, context):
        # Productions 111-114
        left = self.parse_multiplicative(context)

        while self.match('+', '-'):
            self.advance()
            right = self.parse_multiplicative(context)

        return left

    def parse_multiplicative(self, context):
        # Productions 115-119
        left = self.parse_exponentiation(context)

        while self.match('*', '/', '%'):
            self.advance()
            right = self.parse_exponentiation(context)

        return left

    def parse_exponentiation(self, context):
        # Productions 120-121
        left = self.parse_unary(context)

        if self.match('**'):
            self.advance()
            right = self.parse_exponentiation(context)

        return left

    def parse_unary(self, context):
        # Productions 122-125
        if self.match('-', '!'):
            self.advance()
            return self.parse_postfix(context)
        else:
            return self.parse_postfix(context)

    def parse_postfix(self, context):
        # Productions 126-128
        expr = self.parse_primary(context)

        if self.match('++', '--'):
            self.advance()

        return expr

    def parse_primary(self, context):
        # Productions 129-130
        if self.match('('):
            self.advance()
            expr = self.parse_expression('expression_in_paren')
            self.expect(')', 'expression_in_paren')
            return expr
        else:
            return self.parse_factor(context)

    def parse_factor(self, context):
        # Productions 130-132
        if self.match('NUM_LIT', 'DECIMAL_LIT', 'STRING_LIT', 'CHAR_LIT', 'Yes', 'No'):
            self.parse_literal()
        elif self.match('IDENTIFIER'):
            saved_pos = self.pos
            self.advance()

            if self.match('('):
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_function_call()
            elif self.match('['):
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_variable_reference()
            elif self.match('.'):
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_variable_reference()
            else:
                pass  # Just identifier
        else:
            self.error(context='factor')

    def parse_variable_reference(self):
        # Productions 137-144: identifier | <list_access> | <group_member_access>
        self.expect('IDENTIFIER')

        # Production 142: <list_access_1d> ⇒ identifier [ <expression> ]
        if self.match('['):
            self.advance()
            self.parse_expression('expression_in_list_access')  # ← CORRECT
            self.expect(']', 'after_expression_in_list_access')  # ← CORRECT

            # Production 143: <list_access_2d> ⇒ <list_access_1d> [ <expression> ]
            if self.match('['):
                self.advance()
                self.parse_expression('expression_in_list_access')  # ← CORRECT
                # ← CORRECT
                self.expect(']', 'after_expression_in_list_access')

        # Production 144: <group_member_access> ⇒ identifier . identifier
        elif self.match('.'):
            self.advance()
            self.expect('IDENTIFIER', 'after_datatype')

    def parse_literal(self):
        # Productions 154-160
        if self.match('NUM_LIT', 'DECIMAL_LIT', 'STRING_LIT', 'CHAR_LIT', 'Yes', 'No'):
            self.advance()
        else:
            self.error(context='literal')


# For compatibility with existing code
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
