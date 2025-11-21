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
RW_START = 'start'
RW_FINISH = 'finish'

# Reserved Words - Data Types
RW_NUM = 'num'
RW_DECIMAL = 'decimal'
RW_BIGDECIMAL = 'bigdecimal'
RW_LETTER = 'letter'
RW_TEXT = 'text'
RW_BOOL = 'bool'

# Reserved Words - Boolean Literals
RW_YES = 'Yes'
RW_NO = 'No'

# Reserved Words - Null/Empty
RW_NONE = 'none'
RW_EMPTY = 'empty'

# Reserved Words - Constant
RW_FIXED = 'fixed'

# Reserved Words - Input/Output
RW_READ = 'read'
RW_SHOW = 'show'

# Reserved Words - Conditionals
RW_CHECK = 'check'
RW_OTHERWISE = 'otherwise'
RW_OTHERWISECHECK = 'otherwise_check'

# Reserved Words - Switch
RW_FALLBACK = 'fallback'
RW_SELECT = 'select'
RW_OPTION = 'option'

# Reserved Words - Loops
RW_EACH = 'each'
RW_DURING = 'during'
RW_FROM = 'from'
RW_TO = 'to'
RW_STEP = 'step'

# Reserved Words - Control Flow
RW_STOP = 'stop'
RW_SKIP = 'skip'
RW_GIVE = 'give'

# Reserved Words - Function
RW_DEFINE = 'define'

# Reserved Words - Scope
RW_WORLDWIDE = 'worldwide'

# Reserved Words - Data Structures
RW_LIST = 'list'
RW_GROUP = 'group'

# Arithmetic Operators
OP_ADDITION = '+'
OP_SUBTRACTION = '-'
OP_MULTIPLICATION = '*'
OP_DIVISION = '/'
OP_MODULUS = '%'
OP_EXPONENTIATION = '**'

# Assignment Operators
OP_ASSIGNMENT = '='
OP_ADDITION_ASSIGN = '+='
OP_SUBTRACTION_ASSIGN = '-='
OP_MULTIPLICATION_ASSIGN = '*='
OP_DIVISION_ASSIGN = '/='
OP_MODULUS_ASSIGN = '%='

# Comparison Operators
OP_EQUAL_TO = '=='
OP_NOT_EQUAL = '!='
OP_GREATER_THAN = '>'
OP_LESS_THAN = '<'
OP_GREATER_EQUAL = '>='
OP_LESS_EQUAL = '<='

# Logical Operators
OP_LOGICAL_AND = '&&'
OP_LOGICAL_OR = '||'
OP_LOGICAL_NOT = '!'

# Postfix Operators
OP_INCREMENT = '++'
OP_DECREMENT = '--'

# Delimiters
DELIM_LEFT_PAREN = '('
DELIM_RIGHT_PAREN = ')'
DELIM_LEFT_BRACKET = '['
DELIM_RIGHT_BRACKET = ']'
DELIM_LEFT_BRACE = '{'
DELIM_RIGHT_BRACE = '}'
DELIM_SEMICOLON = ';'
DELIM_COLON = ':'
DELIM_COMMA = ','
DELIM_DOT = '.'

# Comments
COMMENT_SINGLE = '~'
COMMENT_MULTI = '~~'

# Literals
LIT_NUMBER = 'num_literal'
LIT_DECIMAL = 'decimal_literal'
LIT_STRING = 'text_literal'
LIT_CHARACTER = 'letter_literal'
LIT_BOOLEAN = 'bool_literal'

# Identifier
IDENTIFIER = 'id'

# Special
WHITESPACE_SPACE = 'space'
WHITESPACE_TAB = 'WHITESPACE_TAB'
NEWLINE = 'newline'
EOF = 'EOF'

# Delimiter sets based on regular definitions
DELIM_SETS = {
    # space only
    'space': {' '},
    # space, newline
    'space_nline': {' ', '\n', '{', '}'},
    # space, {
    'delim1': {' ', '{'},
    # space, (
    'delim2': {' ', '('},
    # space, letternum, (, ", '
    'delim3': {' ', '(', '"', "'"} | set(LETTERNUM),
    # space, id, "
    'escseq_delim': {' ', '"'} | set(LETTERNUM) | {'_'},
    # ;
    'sem_col': {';'},
    # space, letternum, (
    'op_delim': {' ', '('} | set(LETTERNUM),
    # (
    'open_paren': {'('},
    # space, letternum, (, ", {, [
    'comma_delim': {' ', '(', '"', '{', '['} | set(LETTERNUM),
    # space, num, ", [, ]
    'open_list': {' ', '"', '[', ']'} | set(NUM),
    # space, ;, ,, =
    'close_list': {' ', ';', ',', '='},
    # space, letternum, ', ", ), !
    'openparen_delim': {' ', "'", '"', ')', '!'} | set(LETTERNUM),
    # space, mathop, logicop, relop, ;, {, )
    'closeparen_delim': {' ', '+', '-', '*', '/', '%', '&', '|', '!', '=', '<', '>', ';', '{', ')'},
    # space, &, |, !, ;
    'bool_delim': {' ', '&', '|', '!', ';'},
    # space_nline, ,, +, ), ], }, ;
    'string_char': {' ', '\n', ',', '+', ')', ']', '}', ';'},
    # space_nline, null, }, ], ), ,, ;, mathop, relop, logicop, =
    'lit_delim': {' ', '\n', '}', ']', ')', ',', ';', '+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|'},
    # space_nline, mathop, =, <, >, (, ), ], ,, ;, }, &, |, !
    'identifier_del': {' ', '\n', '+', '-', '*', '/', '%', '=', '<', '>', '(', ')', ']', ',', ';', '}', '&', '|', '!'},
    # num only
    'num': set(NUM),
    # space, num
    'id3': {' '} | set(NUM),
    # any ascii character
    'ascii': set(string.printable),
    # = delimiter (special for assignment)
    'delim7': {' ', '\n', '"', "'"} | set(LETTERNUM),
}

# Token to delimiter mapping
TOKEN_DELIMITERS = {
    # Reserved Words
    RW_BIGDECIMAL: 'space',
    RW_BOOL: 'space',
    RW_CHECK: 'delim2',
    RW_DECIMAL: 'space',
    RW_DEFINE: 'space',
    RW_DURING: 'space',
    RW_EACH: 'delim2',
    RW_EMPTY: 'space',
    RW_FALLBACK: 'sem_col',  # Actually should be : but will check as ;
    RW_FINISH: 'space_nline',
    RW_FROM: 'space',
    RW_FIXED: 'space',
    RW_GIVE: 'space',
    RW_GROUP: 'space',
    RW_LETTER: 'space',
    RW_NUM: 'space',
    RW_NONE: 'sem_col',
    RW_NO: 'bool_delim',
    RW_OPTION: 'space',
    RW_OTHERWISE: 'delim1',
    RW_OTHERWISECHECK: 'delim1',
    RW_READ: 'open_paren',
    RW_SELECT: 'delim2',
    RW_SHOW: 'open_paren',
    RW_SKIP: 'sem_col',
    RW_START: 'delim1',
    RW_STEP: 'id3',
    RW_STOP: 'sem_col',
    RW_TEXT: 'space',
    RW_TO: 'space',
    RW_WORLDWIDE: 'space',
    RW_YES: 'bool_delim',
    RW_LIST: 'space',
    
    # Operators
    OP_ADDITION: 'delim3',
    OP_INCREMENT: 'sem_col',
    OP_ADDITION_ASSIGN: 'op_delim',
    OP_SUBTRACTION: 'op_delim',
    OP_DECREMENT: 'sem_col',
    OP_SUBTRACTION_ASSIGN: 'op_delim',
    OP_DIVISION: 'op_delim',
    OP_DIVISION_ASSIGN: 'op_delim',
    OP_MULTIPLICATION: 'op_delim',
    OP_MULTIPLICATION_ASSIGN: 'op_delim',
    OP_EXPONENTIATION: 'op_delim',
    OP_MODULUS: 'op_delim',
    OP_MODULUS_ASSIGN: 'op_delim',
    OP_ASSIGNMENT: 'delim7',
    OP_EQUAL_TO: 'delim3',
    OP_LOGICAL_NOT: 'open_paren',
    OP_NOT_EQUAL: 'delim3',
    OP_GREATER_THAN: 'op_delim',
    OP_GREATER_EQUAL: 'op_delim',
    OP_LESS_THAN: 'op_delim',
    OP_LESS_EQUAL: 'op_delim',
    OP_LOGICAL_AND: 'op_delim',
    OP_LOGICAL_OR: 'op_delim',
    
    # Delimiters
    DELIM_LEFT_BRACKET: 'open_list',
    DELIM_RIGHT_BRACKET: 'close_list',
    DELIM_LEFT_BRACE: 'space_nline',
    DELIM_RIGHT_BRACE: 'space_nline',
    DELIM_LEFT_PAREN: 'openparen_delim',
    DELIM_RIGHT_PAREN: 'closeparen_delim',
    DELIM_DOT: 'num',
    DELIM_COMMA: 'comma_delim',
    DELIM_SEMICOLON: 'space_nline',
    
    # Comments
    COMMENT_SINGLE: 'ascii',
    COMMENT_MULTI: 'ascii',
    
    # Literals
    LIT_NUMBER: 'lit_delim',
    LIT_DECIMAL: 'lit_delim',
    LIT_STRING: 'string_char',
    LIT_CHARACTER: 'string_char',
    
    # Identifier
    IDENTIFIER: 'identifier_del',
}

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

    def check_delimiter(self, token_type, token_value, pos_end):
        """Check if the character following a token matches the expected delimiter"""
        # Skip delimiter check for certain token types
        skip_check = [NEWLINE, WHITESPACE_SPACE, WHITESPACE_TAB, EOF, COMMENT_SINGLE, COMMENT_MULTI]
        if token_type in skip_check:
            return None
        
        # Get expected delimiter set
        if token_type not in TOKEN_DELIMITERS:
            return None
            
        delimiter_type = TOKEN_DELIMITERS[token_type]
        expected_delims = DELIM_SETS.get(delimiter_type, set())
        
        # Special case for fallback - expects ':'
        if token_type == RW_FALLBACK:
            if self.current_char != ':':
                return LexicalError(pos_end, pos_end, 
                    f'Expected ":" after "{token_value}", got "{self.current_char if self.current_char else "EOF"}"')
            return None
        
        # Check current character
        next_char = self.current_char if self.current_char else ''
        
        # EOF is valid for certain delimiters
        if next_char == '' and delimiter_type in ['space_nline', 'lit_delim', 'identifier_del', 'closeparen_delim', 'string_char']:
            return None
        
        if next_char not in expected_delims:
            # Build friendly error message
            delim_names = {
                'space': 'space',
                'space_nline': 'space or newline',
                'delim1': 'space or "{"',
                'delim2': 'space or "("',
                'delim3': 'space, letter, digit, "(", """ or "\'"',
                'sem_col': '";"',
                'op_delim': 'space, letter, digit or "("',
                'open_paren': '"("',
                'comma_delim': 'space, letter, digit, "(", """, "{" or "["',
                'open_list': 'space, digit, """, "[" or "]"',
                'close_list': 'space, ";", "," or "="',
                'openparen_delim': 'space, letter, digit, "\'", """, ")" or "!"',
                'closeparen_delim': 'space, operator, ";", "{" or ")"',
                'bool_delim': 'space, "&", "|", "!" or ";"',
                'string_char': 'space, newline, ",", "+", ")", "]", "}" or ";"',
                'lit_delim': 'space, newline, operator, delimiter or ";"',
                'identifier_del': 'space, newline, operator, delimiter or punctuation',
                'num': 'digit',
                'id3': 'space or digit',
                'delim7': 'space, newline, letter, digit, """ or "\'"',
            }
            
            expected = delim_names.get(delimiter_type, delimiter_type)
            actual = f'"{next_char}"' if next_char else 'EOF'
            
            return LexicalError(pos_end, pos_end, 
                f'Invalid delimiter after "{token_value}": expected {expected}, got {actual}')
        
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
                        Token(NEWLINE, 'newline', pos_start, self.pos.copy()))
                    continue
                elif self.current_char == ' ':
                    self.advance()
                    tokens.append(
                        Token(WHITESPACE_SPACE, 'space', pos_start, self.pos.copy()))
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
            elif self.current_char in LETTERS:
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
                    saved_pos = self.pos.copy()
                    saved_char = self.current_char

                    while self.current_char != None and self.current_char in ' \t':
                        self.advance()

                    if self.current_char != None and self.current_char in LETTERS:
                        next_word = ''
                        while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                            next_word += self.current_char
                            self.advance()

                        if next_word == 'check':
                            pos_end = self.pos.copy()
                            token = Token(RW_OTHERWISECHECK, 'otherwise check', pos_start, pos_end)
                            tokens.append(token)
                            # Check delimiter
                            delim_error = self.check_delimiter(token.type, token.value, pos_end)
                            if delim_error:
                                errors.append(delim_error)
                            continue
                        else:
                            self.pos = saved_pos
                            self.current_char = saved_char
                            pos_end = saved_pos
                    else:
                        pos_end = saved_pos

                    token = Token(RW_OTHERWISE, 'otherwise', pos_start, pos_end)
                    tokens.append(token)
                    # Check delimiter
                    delim_error = self.check_delimiter(token.type, token.value, pos_end)
                    if delim_error:
                        errors.append(delim_error)
                    continue

                # Check if it's a keyword
                if id_str in keywords:
                    token_map = {
                        'start': RW_START, 'finish': RW_FINISH,
                        'num': RW_NUM, 'decimal': RW_DECIMAL, 'bigdecimal': RW_BIGDECIMAL,
                        'letter': RW_LETTER, 'text': RW_TEXT, 'bool': RW_BOOL,
                        'Yes': RW_YES, 'No': RW_NO,
                        'none': RW_NONE, 'empty': RW_EMPTY,
                        'fixed': RW_FIXED,
                        'read': RW_READ, 'show': RW_SHOW,
                        'check': RW_CHECK, 'otherwise': RW_OTHERWISE,
                        'fallback': RW_FALLBACK, 'select': RW_SELECT, 'option': RW_OPTION,
                        'each': RW_EACH, 'during': RW_DURING,
                        'from': RW_FROM, 'to': RW_TO, 'step': RW_STEP,
                        'stop': RW_STOP, 'skip': RW_SKIP, 'give': RW_GIVE,
                        'define': RW_DEFINE,
                        'worldwide': RW_WORLDWIDE,
                        'list': RW_LIST, 'group': RW_GROUP
                    }

                    if id_str in ['Yes', 'No']:
                        token = Token(LIT_BOOLEAN, id_str, pos_start, pos_end)
                    else:
                        token = Token(token_map[id_str], id_str, pos_start, pos_end)
                    
                    tokens.append(token)
                    # Check delimiter
                    delim_error = self.check_delimiter(token.type, token.value, pos_end)
                    if delim_error:
                        errors.append(delim_error)
                else:
                    if len(id_str) > 20:
                        errors.append(LexicalError(pos_start, pos_end,
                                                   f'Identifier "{id_str}" exceeds maximum length: {len(id_str)}/20'))
                        continue

                    token = Token(IDENTIFIER, id_str, pos_start, pos_end)
                    tokens.append(token)
                    # Check delimiter
                    delim_error = self.check_delimiter(token.type, token.value, pos_end)
                    if delim_error:
                        errors.append(delim_error)
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

                while self.current_char != None and self.current_char in NUM:
                    num_str += self.current_char
                    int_dig_count += 1
                    self.advance()

                if self.current_char == '.':
                    num_str += self.current_char
                    dot_count += 1
                    self.advance()

                    while self.current_char != None and self.current_char in NUM:
                        num_str += self.current_char
                        dec_dig_count += 1
                        self.advance()

                pos_end = self.pos.copy()

                if self.current_char != None and (self.current_char in LETTERS or self.current_char == '_'):
                    error_str = num_str
                    while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                        error_str += self.current_char
                        self.advance()

                    pos_end = self.pos.copy()
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Invalid identifier "{error_str}" - identifier cannot start with a digit'))
                    continue

                if dot_count == 0 and int_dig_count > 11:
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Integer exceeds maximum digits: {int_dig_count}/11'))
                    continue

                if dot_count > 0 and dec_dig_count == 0:
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'{num_str} must have digits after decimal point'))
                    continue

                if dec_dig_count > 16:
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Decimal part exceeds maximum digits: {dec_dig_count}/16 (bigdecimal limit)'))
                    continue

                if dot_count == 0:
                    token = Token(LIT_NUMBER, num_str, pos_start, pos_end)
                else:
                    token = Token(LIT_DECIMAL, num_str, pos_start, pos_end)
                
                tokens.append(token)
                # Check delimiter
                delim_error = self.check_delimiter(token.type, token.value, pos_end)
                if delim_error:
                    errors.append(delim_error)
                continue

            #stringlit
            elif self.current_char == '"':
                pos_start = self.pos.copy()
                self.advance()
                string_val = ''
                found_closing = False

                while self.current_char != None and self.current_char != '"':
                    if self.current_char == '\\':
                        self.advance()
                        if self.current_char in ['n', 't', '\\', '"', "'"]:
                            string_val += '\\' + self.current_char
                            self.advance()
                        else:
                            string_val += '\\'
                    else:
                        string_val += self.current_char
                        self.advance()

                if self.current_char == '"':
                    found_closing = True
                    self.advance()

                pos_end = self.pos.copy()
                
                if not found_closing:
                    errors.append(LexicalError(pos_start, pos_end, 
                        'Unterminated string literal - missing closing """'))
                    continue
                
                token = Token(LIT_STRING, string_val, pos_start, pos_end)
                tokens.append(token)
                # Check delimiter
                delim_error = self.check_delimiter(token.type, token.value, pos_end)
                if delim_error:
                    errors.append(delim_error)
                continue

            #charlit
            elif self.current_char == "'":
                pos_start = self.pos.copy()
                self.advance()
                char_val = ''
                found_closing = False

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
                    found_closing = True
                    self.advance()

                pos_end = self.pos.copy()
                
                if not found_closing:
                    errors.append(LexicalError(pos_start, pos_end, 
                        'Unterminated character literal - missing closing "\'"'))
                    continue
                
                # Check if it's a single character (excluding escape sequences)
                if len(char_val) > 2 or (len(char_val) == 2 and char_val[0] != '\\'):
                    errors.append(LexicalError(pos_start, pos_end, 
                        f'Character literal must contain exactly one character, got "{char_val}"'))
                    continue
                
                token = Token(LIT_CHARACTER, char_val, pos_start, pos_end)
                tokens.append(token)
                # Check delimiter
                delim_error = self.check_delimiter(token.type, token.value, pos_end)
                if delim_error:
                    errors.append(delim_error)
                continue

            #operators
            elif self.current_char == '+':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_ADDITION_ASSIGN, '+=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                elif self.current_char == '+':
                    self.advance()
                    token = Token(OP_INCREMENT, '++', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_ADDITION, '+', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '-':
                pos_start = self.pos.copy()
                self.advance()

                # Check if this is a negative number (unary minus)
                if self.current_char and self.current_char in NUM:
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
                        num_start = pos_start
                        num_str = '-'
                        dot_count = 0
                        int_dig_count = 0
                        dec_dig_count = 0

                        while self.current_char != None and self.current_char in NUM:
                            num_str += self.current_char
                            int_dig_count += 1
                            self.advance()

                        if self.current_char == '.':
                            num_str += self.current_char
                            dot_count += 1
                            self.advance()

                            while self.current_char != None and self.current_char in NUM:
                                num_str += self.current_char
                                dec_dig_count += 1
                                self.advance()

                        num_end = self.pos.copy()

                        if self.current_char != None and (self.current_char in LETTERS or self.current_char == '_'):
                            error_str = num_str
                            while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                                error_str += self.current_char
                                self.advance()
                            errors.append(LexicalError(num_start, self.pos.copy(),
                                                       f'Invalid identifier "{error_str}" - identifier cannot start with a digit'))
                            continue

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

                        if dot_count == 0:
                            token = Token(LIT_NUMBER, num_str, num_start, num_end)
                        else:
                            token = Token(LIT_DECIMAL, num_str, num_start, num_end)
                        
                        tokens.append(token)
                        delim_error = self.check_delimiter(token.type, token.value, num_end)
                        if delim_error:
                            errors.append(delim_error)
                        continue

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_SUBTRACTION_ASSIGN, '-=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                elif self.current_char == '-':
                    self.advance()
                    token = Token(OP_DECREMENT, '--', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_SUBTRACTION, '-', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '*':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '*':
                    self.advance()
                    token = Token(OP_EXPONENTIATION, '**', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                elif self.current_char == '=':
                    self.advance()
                    token = Token(OP_MULTIPLICATION_ASSIGN, '*=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_MULTIPLICATION, '*', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '/':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_DIVISION_ASSIGN, '/=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_DIVISION, '/', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '%':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_MODULUS_ASSIGN, '%=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_MODULUS, '%', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '=':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_EQUAL_TO, '==', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_ASSIGNMENT, '=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '!':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_NOT_EQUAL, '!=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_LOGICAL_NOT, '!', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '>':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_GREATER_EQUAL, '>=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_GREATER_THAN, '>', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '<':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    token = Token(OP_LESS_EQUAL, '<=', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    token = Token(OP_LESS_THAN, '<', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                continue

            elif self.current_char == '&':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '&':
                    self.advance()
                    token = Token(OP_LOGICAL_AND, '&&', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    errors.append(LexicalError(pos_start, self.pos.copy(),
                                               'Invalid character "&" (did you mean "&&"?)'))
                continue

            elif self.current_char == '|':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '|':
                    self.advance()
                    token = Token(OP_LOGICAL_OR, '||', pos_start, self.pos.copy())
                    tokens.append(token)
                    delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                    if delim_error:
                        errors.append(delim_error)
                else:
                    errors.append(LexicalError(pos_start, self.pos.copy(),
                                               'Invalid character "|" (did you mean "||"?)'))
                continue

            #delimiters
            elif self.current_char == '(':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_LEFT_PAREN, '(', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == ')':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_RIGHT_PAREN, ')', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == '[':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_LEFT_BRACKET, '[', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == ']':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_RIGHT_BRACKET, ']', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == '{':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_LEFT_BRACE, '{', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == '}':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_RIGHT_BRACE, '}', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == ';':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_SEMICOLON, ';', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == ':':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_COLON, ':', pos_start, self.pos.copy())
                tokens.append(token)
                continue

            elif self.current_char == ',':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_COMMA, ',', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
                continue

            elif self.current_char == '.':
                pos_start = self.pos.copy()
                self.advance()
                token = Token(DELIM_DOT, '.', pos_start, self.pos.copy())
                tokens.append(token)
                delim_error = self.check_delimiter(token.type, token.value, self.pos.copy())
                if delim_error:
                    errors.append(delim_error)
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

        tokens_label = tk.Label(right_panel, text="Lexical Table",
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
                                        columns=("Lexeme", "Token"),
                                        show="headings",
                                        yscrollcommand=vsb.set,
                                        xscrollcommand=hsb.set)

        vsb.config(command=self.token_table.yview)
        hsb.config(command=self.token_table.xview)

        # Configure columns
        self.token_table.heading("Lexeme", text="Lexeme")
        self.token_table.heading("Token", text="Token")

        self.token_table.column("Lexeme", width=250)
        self.token_table.column("Token", width=250)

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

    def update_line_numbers(self, event=None):
        line_count = self.source_text.get("1.0", "end-1c").count('\n') + 1
        line_numbers_string = "\n".join(str(i)
                                        for i in range(1, line_count + 1))
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
        self.token_table.delete(*self.token_table.get_children())
        self.terminal_text.delete(1.0, tk.END)

        source = self.source_text.get(1.0, tk.END)

        if not source.strip():
            self.terminal_text.insert(
                tk.END, "Error: No source code to analyze\n")
            return

        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        for token in tokens:
            if token.type not in [EOF]:
                lexeme = token.value if token.value else "-"
                self.token_table.insert("", tk.END,
                                        values=(lexeme, token.type))

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

        displayable_tokens = [t for t in tokens if t.type not in [EOF]]
        self.terminal_text.insert(
            tk.END, f"\nTotal Tokens: {len(displayable_tokens)}\n")
        self.terminal_text.insert(tk.END, f"Total Errors: {len(errors)}\n")

    def save_results(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SOURCE CODE\n")
                f.write("=" * 80 + "\n")
                f.write(self.source_text.get(1.0, tk.END))
                f.write("\n")

                f.write("=" * 80 + "\n")
                f.write("TOKENS\n")
                f.write("=" * 80 + "\n")
                f.write(f"{'Lexeme':<40} {'Token':<40}\n")
                f.write("-" * 80 + "\n")

                for item in self.token_table.get_children():
                    values = self.token_table.item(item)['values']
                    f.write(f"{values[0]:<40} {values[1]:<40}\n")

                f.write("\n")

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