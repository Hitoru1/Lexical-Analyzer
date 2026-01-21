class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def error(self, expected_tokens):
        token = self.current_token

        # Get previous token for context
        prev_token = self.tokens[self.pos - 1] if self.pos > 0 else None

        if prev_token:
            if prev_token.value:
                prev_str = f"'{prev_token.value}'"
            else:
                prev_str = f"'{prev_token.type}'"
        else:
            prev_str = "start of file"

        # Format current token
        if token:
            if token.value:
                current_str = f"'{token.value}'"
            else:
                current_str = f"'{token.type}'"
        else:
            current_str = "EOF"

        # Format expected tokens
        if isinstance(expected_tokens, str):
            expected_str = expected_tokens
        elif isinstance(expected_tokens, (list, tuple)):
            expected_str = ", ".join(f"'{t}'" for t in expected_tokens)
        else:
            expected_str = str(expected_tokens)

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

    def expect(self, token_type):
        """Consume a token of expected type or error"""
        if not self.match(token_type):
            self.error(f"'{token_type}'")
        self.advance()

    # ===== START PARSING FROM HERE =====

    def parse(self):
        """Entry point - parse entire program"""
        self.parse_program()
        # After 'finish', ignore all remaining tokens (follow set is null/empty)
        # No error for tokens after program terminator
        return "SUCCESS"

    def parse_program(self):
        # 1. <program> ⇒ <program_definitions> <main_program>
        self.parse_program_definitions()
        self.parse_main_program()

    def parse_program_definitions(self):
        # 2. <program_definitions> ⇒ <group_definition> <global_declaration> <function_definition> <program_definitions>
        # 3. <program_definitions> ⇒ λ

        # Keep parsing definitions until we hit 'start' (main program)
        while self.match('group', 'worldwide', 'define'):
            if self.match('group'):
                self.parse_group_definition()
            elif self.match('worldwide'):
                self.parse_global_declaration()
            elif self.match('define'):
                self.parse_function_definition()

    def parse_group_definition(self):
        # 4. group identifier { <group_member_list> }
        if not self.match('group'):
            return  # λ production

        self.expect('group')
        self.expect('IDENTIFIER')
        self.expect('{')
        self.parse_group_member_list()
        self.expect('}')

    def parse_group_member_list(self):
        # 6. <group_member> <group_member_tail>
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_group_member()
            self.parse_group_member_tail()

    def parse_group_member_tail(self):
        # 7. <group_member> <group_member_tail> | 8. λ
        while self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_group_member()

    def parse_group_member(self):
        # 9. <datatype> identifier;
        self.parse_datatype()
        self.expect('IDENTIFIER')
        self.expect(';')

    def parse_global_declaration(self):
        # 10. worldwide <datatype> identifier = <expression>;
        if not self.match('worldwide'):
            return  # λ production

        self.expect('worldwide')
        self.parse_datatype()
        self.expect('IDENTIFIER')
        self.expect('=')
        self.parse_expression()
        self.expect(';')

    def parse_datatype(self):
        # 14-19: num | decimal | bigdecimal | letter | text | bool
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.advance()
        else:
            self.error(
                "'num', 'decimal', 'bigdecimal', 'letter', 'text', or 'bool'")

    def parse_function_definition(self):
        # 20. define <return_type> identifier ( <parameter_list> ) { <local_declarations> <statements> <optional_return> }
        if not self.match('define'):
            return  # λ production

        self.expect('define')
        self.parse_return_type()
        self.expect('IDENTIFIER')
        self.expect('(')
        self.parse_parameter_list()
        self.expect(')')
        self.expect('{')
        self.parse_local_declarations()
        self.parse_statements()
        self.parse_optional_return()
        self.expect('}')

    def parse_return_type(self):
        # 24-25: <datatype> | empty
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_datatype()
        elif self.match('empty'):
            self.advance()
        else:
            self.error(
                "'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', or 'empty'")

    def parse_parameter_list(self):
        # 26-27: <parameter> <parameter_list_tail> | λ
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_parameter()
            self.parse_parameter_list_tail()

    def parse_parameter_list_tail(self):
        # 28-29: , <parameter> <parameter_list_tail> | λ
        while self.match(','):
            self.advance()
            self.parse_parameter()

    def parse_parameter(self):
        # 30. <datatype> identifier
        self.parse_datatype()
        self.expect('IDENTIFIER')

    def parse_local_declarations(self):
        # 22-23: <local_declaration> <local_declarations> | λ
        while self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'IDENTIFIER'):
            self.parse_local_declaration()

    def parse_local_declaration(self):
        # 40. <datatype> identifier = <expression>;
        # 41. identifier identifier;
        if self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool'):
            self.parse_datatype()
            self.expect('IDENTIFIER')
            self.expect('=')
            self.parse_expression()
            self.expect(';')
        elif self.match('IDENTIFIER'):
            self.advance()  # first identifier (type)
            self.expect('IDENTIFIER')  # second identifier (variable name)
            self.expect(';')

    def parse_optional_return(self):
        # 31-32: <return_statement> | λ
        if self.match('give'):
            self.parse_return_statement()

    def parse_return_statement(self):
        # 33. give <return_tail>
        self.expect('give')
        self.parse_return_tail()

    def parse_return_tail(self):
        # 34. <expression>; | 35. ;
        if self.match(';'):
            self.advance()
        else:
            self.parse_expression()
            self.expect(';')

    def parse_main_program(self):
        # 36. start { <statements> } finish
        self.expect('start')
        self.expect('{')
        self.parse_statements()
        self.expect('}')
        self.expect('finish')

    def parse_statements(self):
        # 55-56: <statement> <statements> | λ
        # stop when we hit closing brace or case keywords
        while not self.match('}', 'option', 'fallback', 'stop', 'skip', 'give'):
            if self.current_token is None:
                break
            self.parse_statement()

    def parse_statement(self):
        # 56-60: control | assignment | function_call | declaration | io
        if self.match('check', 'select', 'each', 'during'):
            self.parse_control_statement()
        elif self.match('show', 'read'):
            self.parse_io_statement()
        elif self.match('num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool', 'fixed', 'list'):
            self.parse_declaration()
        elif self.match('IDENTIFIER'):
            # Look ahead to distinguish: "Student s1;" vs "s1.name = ..."
            saved_pos = self.pos
            self.advance()  # Move past first identifier

            # If next token is IDENTIFIER, it's a declaration: "Student s1;"
            if self.match('IDENTIFIER'):
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_declaration()
            else:
                # Otherwise it's assignment or function call: "s1.name = ...", "func()"
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_assignment_or_call()
        else:
            self.error(
                "statement ('check', 'select', 'each', 'during', 'show', 'read', datatype, 'fixed', 'list', or identifier)")

    def parse_assignment_or_call(self):
        # Check if it's assignment or function call
        # ADD THIS
        print(
            f"DEBUG parse_assignment_or_call: current = {self.current_token}")
        saved_pos = self.pos
        self.advance()  # consume identifier
        # ADD THIS
        print(f"DEBUG after advance: current = {self.current_token}")

        if self.match('('):
            # It's a function call
            self.pos = saved_pos
            self.current_token = self.tokens[self.pos]
            self.parse_function_call_statement()
        elif self.match('.', '[', '=', '+=', '-=', '*=', '/=', '%=', '**=', '++', '--'):
            # ADD THIS
            print(f"DEBUG: Detected assignment with {self.current_token}")
            # It's an assignment (includes group member access, list access, or direct assignment)
            self.pos = saved_pos
            self.current_token = self.tokens[self.pos]
            self.parse_assignment_statement()
        else:
            print(f"DEBUG: Default to assignment")  # ADD THIS
            # Default to assignment for standalone identifier
            self.pos = saved_pos
            self.current_token = self.tokens[self.pos]
            self.parse_assignment_statement()

    def parse_declaration(self):
        # 37-39: local | fixed | list
        if self.match('fixed'):
            self.parse_fixed_declaration()
        elif self.match('list'):
            self.parse_list_declaration()
        else:
            self.parse_local_declaration()

    def parse_fixed_declaration(self):
        # 42. fixed <datatype> identifier = <expression>;
        self.expect('fixed')
        self.parse_datatype()
        self.expect('IDENTIFIER')
        self.expect('=')
        self.parse_expression()
        self.expect(';')

    def parse_list_declaration(self):
        # 43-44: list <datatype> identifier = <list_literal_1d/2d>;
        self.expect('list')
        self.parse_datatype()
        self.expect('IDENTIFIER')
        self.expect('=')
        self.expect('[')

        # Check if 2D (next token is '[') or 1D
        if self.match('['):
            # 2D list: [ [elements], [elements] ]
            self.parse_list_rows()
        else:
            # 1D list: [ elements ]
            self.parse_list_elements()

        self.expect(']')
        self.expect(';')

    def parse_list_rows(self):
        # Parse 2D list rows: [row1], [row2], ...
        if not self.match(']'):  # Not empty
            self.expect('[')
            self.parse_list_elements()
            self.expect(']')

            while self.match(','):
                self.advance()
                self.expect('[')
                self.parse_list_elements()
                self.expect(']')

    def parse_list_elements(self):
        # 46-47: <expression> <list_elements_tail> | λ
        if not self.match(']'):
            self.parse_expression()
            while self.match(','):
                self.advance()
                self.parse_expression()

    def parse_assignment_statement(self):
        # 63-64: <assignable> <assignment_op> <expression>; OR <assignable> <increment_op>;
        self.parse_assignable()

        if self.match('=', '+=', '-=', '*=', '/=', '%=', '**='):
            self.advance()  # assignment operator
            self.parse_expression()
            self.expect(';')
        elif self.match('++', '--'):
            self.advance()  # increment operator
            self.expect(';')
        else:
            self.error(
                "'=', '+=', '-=', '*=', '/=', '%=', '**=', '++', or '--'")

    def parse_assignable(self):
        # 66-68: identifier | list_access | group_member_access
        self.expect('IDENTIFIER')

        if self.match('['):
            # List access
            self.advance()
            self.parse_expression()
            self.expect(']')
        elif self.match('.'):
            # Group member access
            self.advance()
            self.expect('IDENTIFIER')

    def parse_function_call_statement(self):
        # 62-63: identifier ( <argument_list> )
        self.parse_function_call()
        self.expect(';')

    def parse_function_call(self):
        self.expect('IDENTIFIER')
        self.expect('(')
        self.parse_argument_list()
        self.expect(')')

    def parse_argument_list(self):
        # 135-136: <expression> <argument_list_tail> | λ
        if not self.match(')'):
            self.parse_expression()
            while self.match(','):
                self.advance()
                self.parse_expression()

    def parse_io_statement(self):
        # 69-70: show | read
        if self.match('show'):
            self.expect('show')
            self.expect('(')
            self.parse_argument_list()
            self.expect(')')
            self.expect(';')
        elif self.match('read'):
            # read(identifier);
            self.expect('read')
            self.expect('(')
            self.expect('IDENTIFIER')
            self.expect(')')
            self.expect(';')

    def parse_control_statement(self):
        # 71-73: check | select | iterative
        if self.match('check'):
            self.parse_check_structure()
        elif self.match('select'):
            self.parse_select_statement()
        elif self.match('each', 'during'):
            self.parse_iterative_statement()

    def parse_check_structure(self):
        # 74. <check_block> <otherwise_chain>
        self.parse_check_block()
        self.parse_otherwise_chain()

    def parse_check_block(self):
        # 75. check ( <expression> ) { <statements> }
        self.expect('check')
        self.expect('(')
        self.parse_expression()
        self.expect(')')
        self.expect('{')
        self.parse_statements()
        self.expect('}')

    def parse_otherwise_chain(self):
        # 76-77: <otherwise_check> <otherwise_chain> | <optional_otherwise>
        while self.match('otherwise', 'otherwisecheck'):  # <-- Add 'otherwisecheck'
            # Check if it's "otherwisecheck" or just "otherwise"
            if self.match('otherwisecheck'):
                self.parse_otherwise_check()
            elif self.match('otherwise'):
                # Look ahead - is there a 'check' after? (shouldn't be, since we have otherwisecheck)
                self.parse_otherwise_block()
                break

    def parse_otherwise_check(self):
        # 80. otherwisecheck ( <expression> ) { <statements> }
        # <-- Changed from 'otherwise' and 'check'
        self.expect('otherwisecheck')
        self.expect('(')
        self.parse_expression()
        self.expect(')')
        self.expect('{')
        self.parse_statements()
        self.expect('}')

    def parse_otherwise_block(self):
        # 81. otherwise { <statements> }
        self.expect('otherwise')
        self.expect('{')
        self.parse_statements()
        self.expect('}')

    def parse_select_statement(self):
        # 82. select ( <expression> ) { <option_blocks> <optional_fallback> }
        self.expect('select')
        self.expect('(')
        self.parse_expression()
        self.expect(')')
        self.expect('{')
        self.parse_option_blocks()
        self.parse_optional_fallback()
        self.expect('}')

    def parse_option_blocks(self):
        # 83-84: <option_block> <option_blocks> | λ
        while self.match('option'):
            self.parse_option_block()

    def parse_option_block(self):
        # 85. option <literal> : <statements> <control_flow> ;
        self.expect('option')
        self.parse_literal()
        self.expect(':')
        # No braces - statements directly after colon
        self.parse_statements()
        self.parse_control_flow()
        self.expect(';')

    def parse_control_flow(self):
        # 85-86: stop | skip
        if self.match('stop', 'skip'):
            self.advance()
        else:
            self.error("'stop' or 'skip'")

    def parse_optional_fallback(self):
        # 88-89: <fallback_block> | λ
        if self.match('fallback'):
            self.parse_fallback_block()

    def parse_fallback_block(self):
        # 90. fallback : { <statements> }
        self.expect('fallback')
        self.expect(':')
        self.expect('{')
        self.parse_statements()
        self.expect('}')

    def parse_iterative_statement(self):
        # 91-92: each | during
        if self.match('each'):
            self.parse_each_loop()
        elif self.match('during'):
            self.parse_during_loop()

    def parse_each_loop(self):
        # 93. each identifier from <expression> to <expression> <step_clause> { <statements> }
        self.expect('each')
        self.expect('IDENTIFIER')
        self.expect('from')
        self.parse_expression()
        self.expect('to')
        self.parse_expression()
        self.parse_step_clause()
        self.expect('{')
        self.parse_statements()
        self.expect('}')

    def parse_step_clause(self):
        # 94-95: step <expression> | λ
        if self.match('step'):
            self.advance()
            self.parse_expression()

    def parse_during_loop(self):
        # 96. during ( <expression> ) { <statements> }
        self.expect('during')
        self.expect('(')
        self.parse_expression()
        self.expect(')')
        self.expect('{')
        self.parse_statements()
        self.expect('}')

    # ===== EXPRESSIONS (The tricky part) =====

    def parse_expression(self):
        # 97. <expression> ⇒ <logical_or_expression>
        return self.parse_logical_or()

    def parse_logical_or(self):
        # 98-99: Handle || operator (left-associative)
        left = self.parse_logical_and()

        while self.match('||'):
            self.advance()
            right = self.parse_logical_and()
            # left = BinaryOp(left, '||', right)  # if building AST

        return left

    def parse_logical_and(self):
        # 100-101: Handle && operator
        left = self.parse_equality()

        while self.match('&&'):
            self.advance()
            right = self.parse_equality()

        return left

    def parse_equality(self):
        # 102-103: Handle == and !=
        left = self.parse_relational()

        while self.match('==', '!='):
            self.advance()
            right = self.parse_relational()

        return left

    def parse_relational(self):
        # 106-107: Handle >, <, >=, <=
        left = self.parse_additive()

        while self.match('>', '<', '>=', '<='):
            self.advance()
            right = self.parse_additive()

        return left

    def parse_additive(self):
        # 112-113: Handle + and -
        left = self.parse_multiplicative()

        while self.match('+', '-'):
            self.advance()
            right = self.parse_multiplicative()

        return left

    def parse_multiplicative(self):
        # 116-117: Handle *, /, %
        left = self.parse_exponentiation()

        while self.match('*', '/', '%'):
            self.advance()
            right = self.parse_exponentiation()

        return left

    def parse_exponentiation(self):
        # 121-122: Handle ** (right-associative)
        left = self.parse_unary()

        if self.match('**'):
            self.advance()
            right = self.parse_exponentiation()  # Right-associative recursion

        return left

    def parse_unary(self):
        # 123-124: Handle unary - and !
        if self.match('-', '!'):
            self.advance()
            return self.parse_postfix()
        else:
            return self.parse_postfix()

    def parse_postfix(self):
        # 127-128: Handle ++ and --
        expr = self.parse_primary()

        if self.match('++', '--'):
            self.advance()

        return expr

    def parse_primary(self):
        # 130-131: ( <expression> ) | <factor>
        if self.match('('):
            self.advance()
            expr = self.parse_expression()
            self.expect(')')
            return expr
        else:
            return self.parse_factor()

    def parse_factor(self):
        # 131-133: <literal> | <variable_reference> | <function_call>
        if self.match('NUM_LIT', 'DECIMAL_LIT', 'STRING_LIT', 'CHAR_LIT', 'Yes', 'No', 'bool_literal'):
            self.parse_literal()
        elif self.match('IDENTIFIER'):
            # Could be variable or function call
            saved_pos = self.pos
            self.advance()

            if self.match('('):
                # Function call
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_function_call()
            elif self.match('['):
                # List access
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_variable_reference()
            elif self.match('.'):
                # Group member access
                self.pos = saved_pos
                self.current_token = self.tokens[self.pos]
                self.parse_variable_reference()
            else:
                # Just identifier
                pass  # Already consumed
        else:
            self.error("literal, identifier, or function call")

    def parse_variable_reference(self):
        # 139-141: identifier | list_access | group_member_access
        self.expect('IDENTIFIER')

        if self.match('['):
            self.advance()
            self.parse_expression()
            self.expect(']')
        elif self.match('.'):
            self.advance()
            self.expect('IDENTIFIER')

    def parse_literal(self):
        # 152-156: num_lit | decimal_lit | string_lit | char_lit | bool
        if self.match('NUM_LIT', 'DECIMAL_LIT', 'STRING_LIT', 'CHAR_LIT', 'Yes', 'No', 'bool_literal'):
            self.advance()
        else:
            self.error(
                "'NUM_LIT', 'DECIMAL_LIT', 'STRING_LIT', 'CHAR_LIT', 'Yes', or 'No'")


# ===== USAGE =====
def test_parser():
    # Assume you have tokens from your lexer
    tokens = [
        Token('start', 'start'),
        Token('{', '{'),
        Token('num', 'num'),
        Token('IDENTIFIER', 'x'),
        Token('=', '='),
        Token('NUM_LIT', '5'),
        Token(';', ';'),
        Token('}', '}'),
        Token('finish', 'finish'),
    ]

    parser = Parser(tokens)
    try:
        result = parser.parse()
        print(result)  # "SUCCESS"
    except SyntaxError as e:
        print(f"Syntax Error: {e}")


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
