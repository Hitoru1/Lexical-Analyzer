import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import string


NUM = '0123456789'
LETTERS = string.ascii_letters
LETTERNUM = NUM + LETTERS
WHITESPACE = '\n\t '

#RESERVED WORDS - FROM PAPER 
keywords = {
    'start', 'finish', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool',
    'Yes', 'No', 'none', 'empty', 'read', 'show', 'check', 'otherwise', 'otherwise check',
    'fallback', 'select', 'option', 'each', 'during', 'from', 'to', 'step',
    'stop', 'skip', 'give', 'define', 'worldwide', 'fixed', 'list', 'group'
}


# Reserved Words - Program Structure
RW_START = 'RW_start'
RW_FINISH = 'RW_finish'

# Reserved Words - Data Types
RW_NUM = 'RW_num'
RW_DECIMAL = 'RW_decimal'
RW_BIGDECIMAL = 'RW_bigdecimal'
RW_LETTER = 'RW_letter'
RW_TEXT = 'RW_text'
RW_BOOL = 'RW_bool'

# Reserved Words - Boolean Literals
RW_YES = 'RW_Yes'
RW_NO = 'RW_No'

# Reserved Words - Null/Empty
RW_NONE = 'RW_none'
RW_EMPTY = 'RW_empty'

# Reserved Words - Constant
RW_FIXED = 'RW_fixed'

# Reserved Words - Input/Output
RW_READ = 'RW_read'
RW_SHOW = 'RW_show'

# Reserved Words - Conditionals
RW_CHECK = 'RW_check'
RW_OTHERWISE = 'RW_otherwise'
RW_OTHERWISECHECK = 'RW_otherwise_check'

# Reserved Words - Switch
RW_FALLBACK = 'RW_fallback'
RW_SELECT = 'RW_select'
RW_OPTION = 'RW_option'

# Reserved Words - Loops
RW_EACH = 'RW_each'
RW_DURING = 'RW_during'
RW_FROM = 'RW_from'
RW_TO = 'RW_to'
RW_STEP = 'RW_step'

# Reserved Words - Control Flow
RW_STOP = 'RW_stop'
RW_SKIP = 'RW_skip'
RW_GIVE = 'RW_give'

# Reserved Words - Function
RW_DEFINE = 'RW_define'

# Reserved Words - Scope
RW_WORLDWIDE = 'RW_worldwide'

# Reserved Words - Data Structures
RW_LIST = 'RW_list'
RW_GROUP = 'RW_group'

# Arithmetic Operators
OP_ADDITION = 'OP_ADDITION'
OP_SUBTRACTION = 'OP_SUBTRACTION'
OP_MULTIPLICATION = 'OP_MULTIPLICATION'
OP_DIVISION = 'OP_DIVISION'
OP_MODULUS = 'OP_MODULUS'
OP_EXPONENTIATION = 'OP_EXPONENTIATION'

# Assignment Operators
OP_ASSIGNMENT = 'OP_ASSIGNMENT'
OP_ADDITION_ASSIGN = 'OP_ADDITION_ASSIGN'
OP_SUBTRACTION_ASSIGN = 'OP_SUBTRACTION_ASSIGN'
OP_MULTIPLICATION_ASSIGN = 'OP_MULTIPLICATION_ASSIGN'
OP_DIVISION_ASSIGN = 'OP_DIVISION_ASSIGN'
OP_MODULUS_ASSIGN = 'OP_MODULUS_ASSIGN'

# Comparison Operators
OP_EQUAL_TO = 'OP_EQUAL_TO'
OP_NOT_EQUAL = 'OP_NOT_EQUAL'
OP_GREATER_THAN = 'OP_GREATER_THAN'
OP_LESS_THAN = 'OP_LESS_THAN'
OP_GREATER_EQUAL = 'OP_GREATER_EQUAL'
OP_LESS_EQUAL = 'OP_LESS_EQUAL'

# Logical Operators
OP_LOGICAL_AND = 'OP_LOGICAL_AND'
OP_LOGICAL_OR = 'OP_LOGICAL_OR'
OP_LOGICAL_NOT = 'OP_LOGICAL_NOT'

# Postfix Operators
OP_INCREMENT = 'OP_INCREMENT'
OP_DECREMENT = 'OP_DECREMENT'

# Delimiters
DELIM_LEFT_PAREN = 'DELIM_LEFT_PAREN'
DELIM_RIGHT_PAREN = 'DELIM_RIGHT_PAREN'
DELIM_LEFT_BRACKET = 'DELIM_LEFT_BRACKET'
DELIM_RIGHT_BRACKET = 'DELIM_RIGHT_BRACKET'
DELIM_LEFT_BRACE = 'DELIM_LEFT_BRACE'
DELIM_RIGHT_BRACE = 'DELIM_RIGHT_BRACE'
DELIM_SEMICOLON = 'DELIM_SEMICOLON'
DELIM_COLON = 'DELIM_COLON'
DELIM_COMMA = 'DELIM_COMMA'
DELIM_DOT = 'DELIM_DOT'

# Comments
COMMENT_SINGLE = 'COMMENT_SINGLE'
COMMENT_MULTI = 'COMMENT_MULTI'

# Literals
LIT_NUMBER = 'LIT_NUMBER'
LIT_DECIMAL = 'LIT_DECIMAL'
LIT_STRING = 'LIT_STRING'
LIT_CHARACTER = 'LIT_CHARACTER'
LIT_BOOLEAN = 'LIT_BOOLEAN'

# Identifier
IDENTIFIER = 'IDENTIFIER'

# Special
WHITESPACE_SPACE = 'WHITESPACE'
WHITESPACE_TAB = 'WHITESPACE'
NEWLINE = 'NEWLINE'
EOF = 'EOF'

#position


class Position:
    def __init__(self, idx, ln, col, fullText):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fullText = fullText

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fullText)

#error


class Error:
    def __init__(self, pos_start, pos_end, error_name, info):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.info = info

    def __repr__(self):
        result = f'{self.error_name}: {self.info}\n'
        result += f'Line {self.pos_start.ln + 1}, Column {self.pos_start.col + 1}\n'
        return result


class LexicalError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, 'Lexical Error', info)

#token


class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}: {self.value}'
        return f'{self.type}'

#lexer


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = Position(0, 0, 0, source)

        if len(source) > 0:
            self.current_char = self.source[0]
        else:
            self.current_char = None

    def advance(self):
        self.pos.advance(self.current_char)

        if self.pos.idx < len(self.source):
            self.current_char = self.source[self.pos.idx]
        else:
            self.current_char = None

    def peek(self, offset=1):
        peek_pos = self.pos.idx + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None

    def tokenize(self):
        tokens = []
        errors = []

        while self.current_char != None:
            #whitespace
            if self.current_char in WHITESPACE:
                pos_start = self.pos.copy()

                if self.current_char == '\n':
                    self.advance()
                    tokens.append(
                        Token(NEWLINE, 'NEWLINE', pos_start, self.pos.copy()))
                    continue
                elif self.current_char == ' ':
                    self.advance()
                    tokens.append(
                        Token(WHITESPACE_SPACE, 'WHITESPACE', pos_start, self.pos.copy()))
                    continue
                elif self.current_char == '\t':
                    self.advance()
                    tokens.append(Token(WHITESPACE_TAB, 'WHITESPACE_TAB',
                                  pos_start, self.pos.copy()))
                    continue

            #comments for both single and multi 
            elif self.current_char == '~':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '~':
                    # Multi-line comment
                    self.advance()
                    comment_val = ''
                    while self.current_char != None:
                        if self.current_char == '~' and self.peek() == '~':
                            self.advance()
                            self.advance()
                            break
                        comment_val += self.current_char
                        self.advance()
                    tokens.append(
                        Token(COMMENT_MULTI, comment_val.strip(), pos_start, self.pos.copy()))
                    continue
                else:
                    # Single-line comment
                    comment_val = ''
                    while self.current_char != None and self.current_char != '\n':
                        comment_val += self.current_char
                        self.advance()
                    tokens.append(
                        Token(COMMENT_SINGLE, comment_val.strip(), pos_start, self.pos.copy()))
                    continue

            #RW or ID
            elif self.current_char in LETTERS:  # FIXED: Must start with letter only
                pos_start = self.pos.copy()
                id_str = ''

                # First character must be a letter
                id_str += self.current_char
                self.advance()

                # Subsequent characters can be letters, digits, or underscore
                while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                    id_str += self.current_char
                    self.advance()

                pos_end = self.pos.copy()

                # Check for multi-word keywords (e.g., "otherwise check")
                if id_str == 'otherwise':
                    # Save current position to potentially rollback
                    saved_pos = self.pos.copy()
                    saved_char = self.current_char

                    # Skip whitespace
                    while self.current_char != None and self.current_char in ' \t':
                        self.advance()

                    # Check if next word is "check"
                    if self.current_char != None and self.current_char in LETTERS:
                        next_word = ''
                        while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                            next_word += self.current_char
                            self.advance()

                        if next_word == 'check':
                            # It's "otherwise check"
                            pos_end = self.pos.copy()
                            tokens.append(
                                Token(RW_OTHERWISECHECK, 'otherwise check', pos_start, pos_end))
                            continue
                        else:
                            # Not "otherwise check", rollback and process "otherwise" alone
                            self.pos = saved_pos
                            self.current_char = saved_char
                            pos_end = saved_pos
                    else:
                        # No word after "otherwise", process it alone
                        pos_end = saved_pos

                    tokens.append(
                        Token(RW_OTHERWISE, 'otherwise', pos_start, pos_end))
                    continue

                # Check if it's a keyword
                if id_str in keywords:
                    # Map to appropriate token type
                    token_map = {
                        'start': RW_START, 'finish': RW_FINISH,
                        'num': RW_NUM, 'decimal': RW_DECIMAL, 'bigdecimal': RW_BIGDECIMAL,
                        'letter': RW_LETTER, 'text': RW_TEXT, 'bool': RW_BOOL,
                        'Yes': RW_YES, 'No': RW_NO,
                        'none': RW_NONE, 'empty': RW_EMPTY,
                        'fixed': RW_FIXED,
                        'read': RW_READ, 'show': RW_SHOW,
                        'check': RW_CHECK, 'otherwise': RW_OTHERWISE,
                        'otherwise check': RW_OTHERWISECHECK,
                        'fallback': RW_FALLBACK, 'select': RW_SELECT, 'option': RW_OPTION,
                        'each': RW_EACH, 'during': RW_DURING,
                        'from': RW_FROM, 'to': RW_TO, 'step': RW_STEP,
                        'stop': RW_STOP, 'skip': RW_SKIP, 'give': RW_GIVE,
                        'define': RW_DEFINE,
                        'worldwide': RW_WORLDWIDE,
                        'list': RW_LIST, 'group': RW_GROUP
                    }

                    # Check for boolean literals
                    if id_str in ['Yes', 'No']:
                        tokens.append(
                            Token(LIT_BOOLEAN, id_str, pos_start, pos_end))
                    else:
                        tokens.append(
                            Token(token_map[id_str], id_str, pos_start, pos_end))
                else:
                    # Check identifier length (max 20 characters according to paper)
                    if len(id_str) > 20:
                        errors.append(LexicalError(pos_start, pos_end,
                                                   f'Identifier "{id_str}" exceeds maximum length: {len(id_str)}/20'))
                        continue

                    # Valid identifier
                    tokens.append(
                        Token(IDENTIFIER, id_str, pos_start, pos_end))
                continue

            #error for underscore
            elif self.current_char == '_':
                pos_start = self.pos.copy()
                errors.append(LexicalError(pos_start, pos_start,
                                           'Identifier cannot start with underscore "_"'))
                self.advance()
                continue

            #numbers
            elif self.current_char in NUM:
                pos_start = self.pos.copy()
                num_str = ''

                dot_count = 0
                int_dig_count = 0
                dec_dig_count = 0

                # Collect digits before decimal
                while self.current_char != None and self.current_char in NUM:
                    num_str += self.current_char
                    int_dig_count += 1
                    self.advance()

                # Check for decimal point
                if self.current_char == '.':
                    num_str += self.current_char
                    dot_count += 1
                    self.advance()

                    # Collect decimal digits
                    while self.current_char != None and self.current_char in NUM:
                        num_str += self.current_char
                        dec_dig_count += 1
                        self.advance()

                pos_end = self.pos.copy()

                #CHECK: If followed by letter or underscore, it's an invalid identifier
                if self.current_char != None and (self.current_char in LETTERS or self.current_char == '_'):
                    # Continue collecting the rest as part of the error
                    error_str = num_str
                    while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                        error_str += self.current_char
                        self.advance()

                    pos_end = self.pos.copy()
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Invalid identifier "{error_str}" - identifier cannot start with a digit'))
                    continue

                # Validate number according to paper rules
                # Integer: max 10 digits
                if dot_count == 0 and int_dig_count > 11:
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Integer exceeds maximum digits: {int_dig_count}/11'))
                    continue

                if dot_count > 0 and dec_dig_count == 0:
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'{num_str} must have digits after decimal point'))
                    continue

                # Decimal validation
                # decimal: up to 11 decimal places
                # bigdecimal: up to 16 decimal places
                if dec_dig_count > 16:
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Decimal part exceeds maximum digits: {dec_dig_count}/16 (bigdecimal limit)'))
                    continue

                # Integer literal
                if dot_count == 0:
                    tokens.append(
                        Token(LIT_NUMBER, num_str, pos_start, pos_end))
                else:
                    tokens.append(
                        Token(LIT_DECIMAL, num_str, pos_start, pos_end))
                continue

            #stringlit
            elif self.current_char == '"':
                pos_start = self.pos.copy()
                self.advance()
                string_val = ''

                while self.current_char != None and self.current_char != '"':
                    if self.current_char == '\\':
                        self.advance()
                        # Escape sequences from paper: \n, \t, \", \', \\
                        if self.current_char in ['n', 't', '\\', '"', "'"]:
                            string_val += '\\' + self.current_char
                            self.advance()
                        else:
                            string_val += '\\'
                    else:
                        string_val += self.current_char
                        self.advance()

                if self.current_char == '"':
                    self.advance()

                pos_end = self.pos.copy()
                tokens.append(
                    Token(LIT_STRING, string_val, pos_start, pos_end))
                continue

            #charlit
            elif self.current_char == "'":
                pos_start = self.pos.copy()
                self.advance()
                char_val = ''

                while self.current_char != None and self.current_char != "'":
                    if self.current_char == '\\':
                        self.advance()
                        if self.current_char in ['n', 't', '\\', '"', "'"]:
                            char_val += '\\' + self.current_char
                            self.advance()
                        else:
                            char_val += '\\'
                    else:
                        char_val += self.current_char
                        self.advance()

                if self.current_char == "'":
                    self.advance()

                pos_end = self.pos.copy()
                tokens.append(
                    Token(LIT_CHARACTER, char_val, pos_start, pos_end))
                continue

            #operators
            elif self.current_char == '+':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_ADDITION_ASSIGN, '+=',
                                  pos_start, self.pos.copy()))
                elif self.current_char == '+':
                    self.advance()
                    tokens.append(Token(OP_INCREMENT, '++',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(
                        Token(OP_ADDITION, '+', pos_start, self.pos.copy()))
                continue

            elif self.current_char == '-':
                pos_start = self.pos.copy()
                self.advance()

                # Check if this is a negative number (unary minus)
                if self.current_char and self.current_char in NUM:
                    # Look at previous token to determine if this is unary minus
                    if len(tokens) == 0 or tokens[-1].type in [
                        OP_ASSIGNMENT, OP_ADDITION_ASSIGN, OP_SUBTRACTION_ASSIGN,
                        OP_MULTIPLICATION_ASSIGN, OP_DIVISION_ASSIGN, OP_MODULUS_ASSIGN,
                        OP_EQUAL_TO, OP_NOT_EQUAL, OP_GREATER_THAN, OP_LESS_THAN,
                        OP_GREATER_EQUAL, OP_LESS_EQUAL, OP_LOGICAL_AND, OP_LOGICAL_OR,
                        DELIM_LEFT_PAREN, DELIM_LEFT_BRACKET, DELIM_COMMA,
                        OP_ADDITION, OP_SUBTRACTION, OP_MULTIPLICATION, OP_DIVISION,
                        OP_MODULUS, OP_EXPONENTIATION,
                        NEWLINE, WHITESPACE_SPACE, WHITESPACE_TAB, DELIM_SEMICOLON,
                        RW_START, DELIM_LEFT_BRACE
                    ]:
                        # This is a negative number
                        num_start = pos_start
                        num_str = '-'
                        dot_count = 0
                        int_dig_count = 0
                        dec_dig_count = 0

                        # Collect integer digits
                        while self.current_char != None and self.current_char in NUM:
                            num_str += self.current_char
                            int_dig_count += 1
                            self.advance()

                        # Check for decimal point
                        if self.current_char == '.':
                            num_str += self.current_char
                            dot_count += 1
                            self.advance()

                            # Collect decimal digits
                            while self.current_char != None and self.current_char in NUM:
                                num_str += self.current_char
                                dec_dig_count += 1
                                self.advance()

                        num_end = self.pos.copy()

                        # Check if followed by letter/underscore (invalid identifier)
                        if self.current_char != None and (self.current_char in LETTERS or self.current_char == '_'):
                            error_str = num_str
                            while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                                error_str += self.current_char
                                self.advance()
                            errors.append(LexicalError(num_start, self.pos.copy(),
                                                       f'Invalid identifier "{error_str}" - identifier cannot start with a digit'))
                            continue

                        # Validate number ranges
                        if dot_count == 0 and int_dig_count > 10:
                            errors.append(LexicalError(num_start, num_end,
                                                       f'Integer exceeds maximum digits: {int_dig_count}/10'))
                            continue

                        if dot_count > 0 and dec_dig_count == 0:
                            errors.append(LexicalError(num_start, num_end,
                                                       f'{num_str} must have digits after decimal point'))
                            continue

                        if dec_dig_count > 16:
                            errors.append(LexicalError(num_start, num_end,
                                                       f'Decimal part exceeds maximum digits: {dec_dig_count}/16 (bigdecimal limit)'))
                            continue

                        # Create token
                        if dot_count == 0:
                            tokens.append(
                                Token(LIT_NUMBER, num_str, num_start, num_end))
                        else:
                            tokens.append(
                                Token(LIT_DECIMAL, num_str, num_start, num_end))
                        continue

                # Not a negative number, treat as subtraction operator
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_SUBTRACTION_ASSIGN,
                                  '-=', pos_start, self.pos.copy()))
                elif self.current_char == '-':
                    self.advance()
                    tokens.append(Token(OP_DECREMENT, '--',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(Token(OP_SUBTRACTION, '-',
                                  pos_start, self.pos.copy()))
                continue

            elif self.current_char == '*':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '*':
                    self.advance()
                    tokens.append(Token(OP_EXPONENTIATION, '**',
                                  pos_start, self.pos.copy()))
                elif self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_MULTIPLICATION_ASSIGN,
                                  '*=', pos_start, self.pos.copy()))
                else:
                    tokens.append(Token(OP_MULTIPLICATION, '*',
                                  pos_start, self.pos.copy()))
                continue

            elif self.current_char == '/':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_DIVISION_ASSIGN, '/=',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(
                        Token(OP_DIVISION, '/', pos_start, self.pos.copy()))
                continue

            elif self.current_char == '%':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_MODULUS_ASSIGN, '%=',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(
                        Token(OP_MODULUS, '%', pos_start, self.pos.copy()))
                continue

            elif self.current_char == '=':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(
                        Token(OP_EQUAL_TO, '==', pos_start, self.pos.copy()))
                else:
                    tokens.append(Token(OP_ASSIGNMENT, '=',
                                  pos_start, self.pos.copy()))
                continue

            elif self.current_char == '!':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_NOT_EQUAL, '!=',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(Token(OP_LOGICAL_NOT, '!',
                                  pos_start, self.pos.copy()))
                continue

            elif self.current_char == '>':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_GREATER_EQUAL, '>=',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(Token(OP_GREATER_THAN, '>',
                                  pos_start, self.pos.copy()))
                continue

            elif self.current_char == '<':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(OP_LESS_EQUAL, '<=',
                                  pos_start, self.pos.copy()))
                else:
                    tokens.append(
                        Token(OP_LESS_THAN, '<', pos_start, self.pos.copy()))
                continue

            elif self.current_char == '&':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '&':
                    self.advance()
                    tokens.append(Token(OP_LOGICAL_AND, '&&',
                                  pos_start, self.pos.copy()))
                else:
                    errors.append(LexicalError(pos_start, self.pos.copy(),
                                               'Invalid character "&" (did you mean "&&"?)'))
                continue

            elif self.current_char == '|':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '|':
                    self.advance()
                    tokens.append(Token(OP_LOGICAL_OR, '||',
                                  pos_start, self.pos.copy()))
                else:
                    errors.append(LexicalError(pos_start, self.pos.copy(),
                                               'Invalid character "|" (did you mean "||"?)'))
                continue

            #delimiters
            elif self.current_char == '(':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(
                    Token(DELIM_LEFT_PAREN, '(', pos_start, self.pos.copy()))
                continue

            elif self.current_char == ')':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(Token(DELIM_RIGHT_PAREN, ')',
                              pos_start, self.pos.copy()))
                continue

            elif self.current_char == '[':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(Token(DELIM_LEFT_BRACKET,
                              '[', pos_start, self.pos.copy()))
                continue

            elif self.current_char == ']':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(Token(DELIM_RIGHT_BRACKET, ']',
                              pos_start, self.pos.copy()))
                continue

            elif self.current_char == '{':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(
                    Token(DELIM_LEFT_BRACE, '{', pos_start, self.pos.copy()))
                continue

            elif self.current_char == '}':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(Token(DELIM_RIGHT_BRACE, '}',
                              pos_start, self.pos.copy()))
                continue

            elif self.current_char == ';':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(Token(DELIM_SEMICOLON, ';',
                              pos_start, self.pos.copy()))
                continue

            elif self.current_char == ':':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(
                    Token(DELIM_COLON, ':', pos_start, self.pos.copy()))
                continue

            elif self.current_char == ',':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(
                    Token(DELIM_COMMA, ',', pos_start, self.pos.copy()))
                continue

            elif self.current_char == '.':
                pos_start = self.pos.copy()
                self.advance()
                tokens.append(
                    Token(DELIM_DOT, '.', pos_start, self.pos.copy()))
                continue

            #unrecognized char
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                errors.append(LexicalError(pos_start, self.pos.copy(),
                                           f'Invalid character "{char}"'))
                continue

        # Always append EOF at the end
        tokens.append(Token(EOF, '', self.pos.copy(), self.pos.copy()))
        return tokens, errors

#gui tkinter


class KuCodeLexerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KuCode Lexical Analyzer")
        self.root.geometry("1400x800")

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        bg_color = "#2b5b84"
        fg_color = "white"

        # Header Frame
        header_frame = tk.Frame(root, bg=bg_color, height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # Logo and Title
        title_label = tk.Label(header_frame, text="KuCode Lexical Analyzer",
                               font=("Arial", 18, "bold"), bg=bg_color, fg=fg_color)
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Buttons
        btn_frame = tk.Frame(header_frame, bg=bg_color)
        btn_frame.pack(side=tk.RIGHT, padx=20)

        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_all,
                              bg="#5a8bb8", fg="white", font=("Arial", 10, "bold"),
                              padx=20, pady=5, relief=tk.FLAT, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=5)

        analyze_btn = tk.Button(btn_frame, text="Analyze", command=self.analyze,
                                bg="#4a7ba7", fg="white", font=("Arial", 10, "bold"),
                                padx=20, pady=5, relief=tk.FLAT, cursor="hand2")
        analyze_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(btn_frame, text="Save", command=self.save_results,
                             bg="#3a6b97", fg="white", font=("Arial", 10, "bold"),
                             padx=20, pady=5, relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=5)

        # Main container
        main_container = tk.Frame(root, bg="#f0f0f0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel - Source Code
        left_panel = tk.Frame(main_container, bg="white",
                              relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        source_label = tk.Label(left_panel, text="Source Code",
                                font=("Arial", 12, "bold"), bg="white", anchor="w")
        source_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Line numbers frame
        line_frame = tk.Frame(left_panel, bg="white")
        line_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Line numbers
        self.line_numbers = tk.Text(line_frame, width=4, padx=5, takefocus=0,
                                    border=0, background='#e0e0e0', state='disabled',
                                    wrap='none', font=("Consolas", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Source code text area
        self.source_text = scrolledtext.ScrolledText(line_frame, wrap=tk.NONE,
                                                     font=("Consolas", 10),
                                                     bg="#1e1e1e", fg="#d4d4d4",
                                                     insertbackground="white",
                                                     selectbackground="#264f78")
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.source_text.bind('<KeyRelease>', self.update_line_numbers)
        self.source_text.bind('<MouseWheel>', self.sync_scroll)

        # Right Panel - Tokens
        right_panel = tk.Frame(
            main_container, bg="white", relief=tk.RAISED, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tokens_label = tk.Label(right_panel, text="Tokens",
                                font=("Arial", 12, "bold"), bg="white", anchor="w")
        tokens_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Tokens table
        table_frame = tk.Frame(right_panel)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        self.token_table = ttk.Treeview(table_frame,
                                        columns=("Type", "Lexeme",
                                                 "Line", "Col"),
                                        show="headings",
                                        yscrollcommand=vsb.set,
                                        xscrollcommand=hsb.set)

        vsb.config(command=self.token_table.yview)
        hsb.config(command=self.token_table.xview)

        # Configure columns
        self.token_table.heading("Type", text="Type")
        self.token_table.heading("Lexeme", text="Lexeme")
        self.token_table.heading("Line", text="Line")
        self.token_table.heading("Col", text="Col")

        self.token_table.column("Type", width=200)
        self.token_table.column("Lexeme", width=200)
        self.token_table.column("Line", width=80)
        self.token_table.column("Col", width=80)

        self.token_table.pack(fill=tk.BOTH, expand=True)

        # Bottom Panel - Terminal
        terminal_frame = tk.Frame(
            root, bg="white", relief=tk.RAISED, bd=1, height=150)
        terminal_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        terminal_frame.pack_propagate(False)

        terminal_label = tk.Label(terminal_frame, text="Terminal",
                                  font=("Arial", 12, "bold"), bg="white", anchor="w")
        terminal_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.terminal_text = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD,
                                                       font=("Consolas", 9),
                                                       bg="#1e1e1e", fg="#00ff00",
                                                       height=6)
        self.terminal_text.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    '''
        # Load sample code
        self.load_sample_code()
        self.update_line_numbers()
    
    def load_sample_code(self):
        sample = """~ Sample KuCode program
fixed num PI = 3.1416;
num x = -15-5;
decimal y = 2.5;
text name = "Axel";
start {
    show("Hello, KuCode");
    check (x > 0) {
        show("Positive");
    } otherwise check (x < 0) {
        show("Negative");
    } otherwise {
        show("Zero");
    }
}
finish"""
        self.source_text.insert(1.0, sample)
    '''

    def update_line_numbers(self, event=None):
        # Get the number of lines in the source text
        line_count = self.source_text.get("1.0", "end-1c").count('\n') + 1

        # Generate line numbers
        line_numbers_string = "\n".join(str(i)
                                        for i in range(1, line_count + 1))

        # Update line numbers text widget
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state='disabled')

    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.source_text.yview()[0])

    def clear_all(self):
        self.source_text.delete(1.0, tk.END)
        self.token_table.delete(*self.token_table.get_children())
        self.terminal_text.delete(1.0, tk.END)
        self.update_line_numbers()

    def analyze(self):
        # Clear previous results
        self.token_table.delete(*self.token_table.get_children())
        self.terminal_text.delete(1.0, tk.END)

        # Get source code
        source = self.source_text.get(1.0, tk.END)

        if not source.strip():
            self.terminal_text.insert(
                tk.END, "Error: No source code to analyze\n")
            return

        # Create lexer and tokenize
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        # Display tokens (skip only EOF)
        for token in tokens:
            if token.type not in [EOF]:
                line = token.pos_start.ln + 1
                col = token.pos_start.col + 1
                lexeme = token.value if token.value else "-"

                self.token_table.insert("", tk.END,
                                        values=(token.type, lexeme, line, col))

        # Display terminal message
        if errors:
            self.terminal_text.insert(
                tk.END, "✗ Lexical analysis completed with errors:\n\n", "error")
            for error in errors:
                self.terminal_text.insert(tk.END, str(error) + "\n", "error")
            self.terminal_text.tag_config("error", foreground="#ff6b6b")
        else:
            self.terminal_text.insert(
                tk.END, "✓ Lexically correct - no lexical errors detected.\n", "success")
            self.terminal_text.tag_config("success", foreground="#00ff00")

        # Add summary (exclude only EOF from count)
        displayable_tokens = [t for t in tokens if t.type not in [EOF]]
        self.terminal_text.insert(
            tk.END, f"\nTotal Tokens: {len(displayable_tokens)}\n")
        self.terminal_text.insert(tk.END, f"Total Errors: {len(errors)}\n")

    def save_results(self):
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write source code
                f.write("=" * 80 + "\n")
                f.write("SOURCE CODE\n")
                f.write("=" * 80 + "\n")
                f.write(self.source_text.get(1.0, tk.END))
                f.write("\n")

                # Write tokens
                f.write("=" * 80 + "\n")
                f.write("TOKENS\n")
                f.write("=" * 80 + "\n")
                f.write(
                    f"{'Type':<30} {'Lexeme':<30} {'Line':<10} {'Col':<10}\n")
                f.write("-" * 80 + "\n")

                for item in self.token_table.get_children():
                    values = self.token_table.item(item)['values']
                    f.write(
                        f"{values[0]:<30} {values[1]:<30} {values[2]:<10} {values[3]:<10}\n")

                f.write("\n")

                # Write terminal output
                f.write("=" * 80 + "\n")
                f.write("ANALYSIS RESULT\n")
                f.write("=" * 80 + "\n")
                f.write(self.terminal_text.get(1.0, tk.END))

            messagebox.showinfo("Success", f"Results saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")


#main
if __name__ == "__main__":
    root = tk.Tk()
    app = KuCodeLexerGUI(root)
    root.mainloop()
