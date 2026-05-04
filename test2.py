import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import string
import re

NUM = '0123456789'
LETTERS = string.ascii_letters
LETTERNUM = NUM + LETTERS
WHITESPACE = '\n\t '


# Reserved Words - Program Structures
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

# Reserved Words - Empty
RW_EMPTY = 'empty'

# Reserved Words - Constant
RW_FIXED = 'fixed'

# Reserved Words - Input/Output
RW_READ = 'read'
RW_SHOW = 'show'
RW_DISPLAY = 'display'

# Reserved Words - Built-in Functions
RW_SIZE = 'size'
RW_TEXTLEN = 'textlen'
RW_CHARAT = 'charat'
RW_ORD = 'ord'

# Reserved Words - Conditionals
RW_CHECK = 'check'
RW_OTHERWISE = 'otherwise'
RW_OTHERWISECHECK = 'otherwisecheck'

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
OP_INTEGER_DIVISION = '//'
OP_MODULUS = '%'
OP_EXPONENTIATION = '**'
OP_EXPONENTIATION_ASSIGN = '**='

# Assignment Operators
OP_ASSIGNMENT = '='
OP_ADDITION_ASSIGN = '+='
OP_SUBTRACTION_ASSIGN = '-='
OP_MULTIPLICATION_ASSIGN = '*='
OP_DIVISION_ASSIGN = '/='
OP_INTEGER_DIVISION_ASSIGN = '//='
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
LIT_NUMBER = 'num_lit'
LIT_DECIMAL = 'decimal_lit'
LIT_STRING = 'string_lit'
LIT_CHARACTER = 'char_lit'
LIT_BOOLEAN = 'bool_literal'

# Identifier
IDENTIFIER = 'identifier'

# Special
WHITESPACE_SPACE = 'space'
WHITESPACE_TAB = 'WHITESPACE_TAB'
NEWLINE = 'newline'
EOF = 'EOF'

# Delimiter sets based on regular definitions
DELIM_SETS = {
    # space only
    'space_semcol': {' ', ';'},
    'space': {' '},
    # space, newline
    'space_nline': {' ', '\n', None},
    # space, {
    'delim1': {' ', '{'},
    # space, (
    'delim2': {' ', '('},
    # space, letternum, (, ", '
    # space, letternum, (, ", ', [
    'delim3': {' ', '(', '"', "'", '['} | set(LETTERNUM),
    # space, id, "
    'escseq_delim': {' ', '"'} | set(LETTERNUM) | {'_'},
    # ;
    'sem_col': {';'},
    # space, letternum, (
    'op_delim': {' ', '('} | set(LETTERNUM),
    # (
    'open_paren': {'('},
    # space, letternum, (, ", ', {, [
    'comma_delim': {' ', '(', '"', "'", '{', '[', '\n'} | set(LETTERNUM),
    # space, num, ", ', [, ]
    'open_list': {' ', '"', "'", '[', ']'} | set(LETTERNUM),
    # space, ;, ,, =, .
    'close_list': {' ', ';', ',', '=', ']', '[', '+', '-', '*', '/', '%', '&', '|', '!', '<', '>', ')', '.'},
    # space, letternum, ', ", (, ), !
    'openparen_delim': {' ', "'", '"', '(', ')', '!', '-'} | set(LETTERNUM),
    # space, mathop, logicop, relop, ;, {, )
    'closeparen_delim': {' ', '+', '-', '*', '/', '%', '&', '|', '!', '=', '<', '>', ';', '{', ')', ']', '\n', ','},
    # space, &, |, !, ;, arithmetic ops, relational ops
    'bool_delim': {' ', '&', '|', '!', ';', ')', ':', ',', ']', '=', '+', '-', '*', '/', '%', '>', '<'},
    # space_nline, ,, +, ), ], }, ;
    'string_char': {' ', '\n', ',', '+', ')', ']', '}', ';', ':'},
    # space_nline, null, }, ], ), ,, ;, mathop, relop, logicop, =
    'lit_delim': {' ', '\n', '}', ']', ')', ',', ';', '+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', ':', '{'},
    # space_nline, mathop, =, <, >, (, ), ], ,, ;, }, &, |, !
    'identifier_del': {' ', '\n', '+', '-', '*', '/', '%', '=', '<', '>', '(', ')', ']', ',', ';', '}', '&', '|', '!', '.', '{', '['},
    # num only
    'num': set(NUM),
    # space, num
    'id3': {' '} | set(NUM),
    # any ascii character
    'ascii': set(string.printable),
    # = delimiter (special for assignment)
    'delim7': {' ', '\n', '"', "'"} | set(LETTERNUM),
    'dot_delim': set(NUM) | set(LETTERS),
    'not_delim': {'(', '-'} | set(LETTERNUM) | {'"', "'"},

}

# Token to delimiter mapping
TOKEN_DELIMITERS = {
    # Reserved Words
    RW_BIGDECIMAL: 'space',
    RW_BOOL: 'space',
    RW_CHECK: 'delim2',
    RW_DECIMAL: 'space',
    RW_DEFINE: 'space',
    RW_DISPLAY: 'open_paren',
    RW_DURING: 'delim2',
    RW_EACH: 'delim2',
    RW_EMPTY: 'space',
    RW_FALLBACK: 'sem_col',
    RW_FINISH: 'space_nline',
    RW_FROM: 'space',
    RW_FIXED: 'space',
    RW_GIVE: 'space_semcol',
    RW_GROUP: 'space',
    RW_LETTER: 'space',
    RW_NUM: 'space',
    RW_NO: 'bool_delim',
    RW_OPTION: 'space',
    RW_OTHERWISE: 'delim1',
    RW_OTHERWISECHECK: 'delim2',
    RW_READ: 'open_paren',
    RW_SELECT: 'delim2',
    RW_SHOW: 'open_paren',
    RW_SIZE: 'open_paren',
    RW_TEXTLEN: 'open_paren',
    RW_CHARAT: 'open_paren',
    RW_ORD: 'open_paren',
    RW_SKIP: 'sem_col',
    RW_START: 'delim1',
    RW_STEP: 'id3',
    RW_STOP: 'sem_col',
    RW_TEXT: 'space',
    RW_TO: 'space',
    RW_WORLDWIDE: 'space',
    RW_YES: 'bool_delim',
    RW_LIST: 'space',
    LIT_BOOLEAN: 'bool_delim',

    # Operators
    OP_ADDITION: 'delim3',
    OP_INCREMENT: 'sem_col',
    OP_ADDITION_ASSIGN: 'op_delim',
    OP_SUBTRACTION: 'op_delim',
    OP_DECREMENT: 'sem_col',
    OP_SUBTRACTION_ASSIGN: 'op_delim',
    OP_DIVISION: 'op_delim',
    OP_DIVISION_ASSIGN: 'op_delim',
    OP_INTEGER_DIVISION: 'op_delim',
    OP_INTEGER_DIVISION_ASSIGN: 'op_delim',
    OP_MULTIPLICATION: 'op_delim',
    OP_MULTIPLICATION_ASSIGN: 'op_delim',
    OP_EXPONENTIATION: 'op_delim',
    OP_EXPONENTIATION_ASSIGN: 'op_delim',
    OP_MODULUS: 'op_delim',
    OP_MODULUS_ASSIGN: 'op_delim',
    OP_ASSIGNMENT: 'delim3',
    OP_EQUAL_TO: 'delim3',
    OP_LOGICAL_NOT: 'not_delim',
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
    DELIM_DOT: 'dot_delim',
    DELIM_COMMA: 'comma_delim',
    DELIM_SEMICOLON: 'space_nline',
    DELIM_COLON: 'space_nline',

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

# position


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

# error


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

# token


class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        self.lexeme = value

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


def map_token_type_for_parser(token_type):
    """Map lexer token types to parser-expected types"""
    mapping = {
        LIT_NUMBER: 'num_lit',
        LIT_DECIMAL: 'decimal_lit',
        LIT_STRING: 'string_lit',
        LIT_CHARACTER: 'char_lit',
        IDENTIFIER: 'identifier',
        DELIM_SEMICOLON: ';',
        DELIM_COMMA: ',',
        DELIM_LEFT_PAREN: '(',
        DELIM_RIGHT_PAREN: ')',
        DELIM_LEFT_BRACE: '{',
        DELIM_RIGHT_BRACE: '}',
        DELIM_LEFT_BRACKET: '[',
        DELIM_RIGHT_BRACKET: ']',
        DELIM_COLON: ':',
        DELIM_DOT: '.',
    }
    return mapping.get(token_type, token_type)


def prepare_tokens_for_parser(tokens):
    """Filter out whitespace/comments and map token types"""
    filtered = []
    skip_types = [NEWLINE, WHITESPACE_SPACE,
                  WHITESPACE_TAB, COMMENT_SINGLE, COMMENT_MULTI, EOF]

    for token in tokens:
        if token.type not in skip_types:
            # Create new token with mapped type
            mapped_type = map_token_type_for_parser(token.type)
            filtered.append(Token(mapped_type, token.value,
                            token.pos_start, token.pos_end))

    return filtered

# DFA for keyword recognition


class TransitionDFA:
    """Implements the complete transition diagram as a DFA"""

    def __init__(self):
        self.transitions = self._build_transitions()
        self.accept_states = self._build_accept_states()

    def _build_transitions(self):
        """Build transition table based on diagrams"""
        trans = {}

        # Start state
        trans[0] = {
            'b': 1, 'c': 14, 'd': 23, 'e': 45, 'f': 53, 'g': 72,
            'l': 80, 'N': 89, 'n': 91, 'o': 94, 'r': 115, 's': 119,
            't': 142, 'w': 150, 'Y': 159
        }

        # "bigdecimal", "bool"
        trans[1] = {'i': 2, 'o': 11}
        trans[2] = {'g': 3}
        trans[3] = {'d': 4}
        trans[4] = {'e': 5}
        trans[5] = {'c': 6}
        trans[6] = {'i': 7}
        trans[7] = {'m': 8}
        trans[8] = {'a': 9}
        trans[9] = {'l': 10}
        trans[10] = {}  # accept: bigdecimal
        trans[11] = {'o': 12}
        trans[12] = {'l': 13}
        trans[13] = {}  # accept: bool

        # "charat", "check"
        trans[14] = {'h': 15}
        trans[15] = {'a': 16, 'e': 20}
        trans[16] = {'r': 17}
        trans[17] = {'a': 18}
        trans[18] = {'t': 19}
        trans[19] = {}  # accept: charat
        trans[20] = {'c': 21}
        trans[21] = {'k': 22}
        trans[22] = {}  # accept: check

        # "decimal", "define", "display", "during"
        trans[23] = {'e': 24, 'i': 34, 'u': 40}
        trans[24] = {'c': 25, 'f': 30}
        trans[25] = {'i': 26}
        trans[26] = {'m': 27}
        trans[27] = {'a': 28}
        trans[28] = {'l': 29}
        trans[29] = {}  # accept: decimal
        trans[30] = {'i': 31}
        trans[31] = {'n': 32}
        trans[32] = {'e': 33}
        trans[33] = {}  # accept: define
        trans[34] = {'s': 35}
        trans[35] = {'p': 36}
        trans[36] = {'l': 37}
        trans[37] = {'a': 38}
        trans[38] = {'y': 39}
        trans[39] = {}  # accept: display
        trans[40] = {'r': 41}
        trans[41] = {'i': 42}
        trans[42] = {'n': 43}
        trans[43] = {'g': 44}
        trans[44] = {}  # accept: during

        # "each", "empty"
        trans[45] = {'a': 46, 'm': 49}
        trans[46] = {'c': 47}
        trans[47] = {'h': 48}
        trans[48] = {}  # accept: each
        trans[49] = {'p': 50}
        trans[50] = {'t': 51}
        trans[51] = {'y': 52}
        trans[52] = {}  # accept: empty

        # "fallback", "finish", "fixed", "from"
        trans[53] = {'a': 54, 'i': 61, 'r': 69}
        trans[54] = {'l': 55}
        trans[55] = {'l': 56}
        trans[56] = {'b': 57}
        trans[57] = {'a': 58}
        trans[58] = {'c': 59}
        trans[59] = {'k': 60}
        trans[60] = {}  # accept: fallback
        trans[61] = {'n': 62, 'x': 66}
        trans[62] = {'i': 63}
        trans[63] = {'s': 64}
        trans[64] = {'h': 65}
        trans[65] = {}  # accept: finish
        trans[66] = {'e': 67}
        trans[67] = {'d': 68}
        trans[68] = {}  # accept: fixed
        trans[69] = {'o': 70}
        trans[70] = {'m': 71}
        trans[71] = {}  # accept: from

        # "give", "group"
        trans[72] = {'i': 73, 'r': 76}
        trans[73] = {'v': 74}
        trans[74] = {'e': 75}
        trans[75] = {}  # accept: give
        trans[76] = {'o': 77}
        trans[77] = {'u': 78}
        trans[78] = {'p': 79}
        trans[79] = {}  # accept: group

        # "letter", "list"
        trans[80] = {'e': 81, 'i': 86}
        trans[81] = {'t': 82}
        trans[82] = {'t': 83}
        trans[83] = {'e': 84}
        trans[84] = {'r': 85}
        trans[85] = {}  # accept: letter
        trans[86] = {'s': 87}
        trans[87] = {'t': 88}
        trans[88] = {}  # accept: list

        # "No"
        trans[89] = {'o': 90}
        trans[90] = {}  # accept: No

        # "num"
        trans[91] = {'u': 92}
        trans[92] = {'m': 93}
        trans[93] = {}  # accept: num

        # "option", "ord", "otherwise", "otherwisecheck"
        trans[94] = {'p': 95, 'r': 100, 't': 102}
        trans[95] = {'t': 96}
        trans[96] = {'i': 97}
        trans[97] = {'o': 98}
        trans[98] = {'n': 99}
        trans[99] = {}  # accept: option
        trans[100] = {'d': 101}
        trans[101] = {}  # accept: ord
        trans[102] = {'h': 103}
        trans[103] = {'e': 104}
        trans[104] = {'r': 105}
        trans[105] = {'w': 106}
        trans[106] = {'i': 107}
        trans[107] = {'s': 108}
        trans[108] = {'e': 109}
        # accept: otherwise (continues to otherwisecheck)
        trans[109] = {'c': 110}
        trans[110] = {'h': 111}
        trans[111] = {'e': 112}
        trans[112] = {'c': 113}
        trans[113] = {'k': 114}
        trans[114] = {}  # accept: otherwisecheck

        # "read"
        trans[115] = {'e': 116}
        trans[116] = {'a': 117}
        trans[117] = {'d': 118}
        trans[118] = {}  # accept: read

        # "select", "show", "size", "skip", "start", "step", "stop"
        trans[119] = {'e': 120, 'h': 125, 'i': 128, 'k': 131, 't': 134}
        trans[120] = {'l': 121}
        trans[121] = {'e': 122}
        trans[122] = {'c': 123}
        trans[123] = {'t': 124}
        trans[124] = {}  # accept: select
        trans[125] = {'o': 126}
        trans[126] = {'w': 127}
        trans[127] = {}  # accept: show
        trans[128] = {'z': 129}
        trans[129] = {'e': 130}
        trans[130] = {}  # accept: size
        trans[131] = {'i': 132}
        trans[132] = {'p': 133}
        trans[133] = {}  # accept: skip
        trans[134] = {'a': 135, 'e': 138, 'o': 140}
        trans[135] = {'r': 136}
        trans[136] = {'t': 137}
        trans[137] = {}  # accept: start
        trans[138] = {'p': 139}
        trans[139] = {}  # accept: step
        trans[140] = {'p': 141}
        trans[141] = {}  # accept: stop

        # "text", "textlen", "to"
        trans[142] = {'e': 143, 'o': 149}
        trans[143] = {'x': 144}
        trans[144] = {'t': 145}
        trans[145] = {'l': 146}  # accept: text (continues to textlen)
        trans[146] = {'e': 147}
        trans[147] = {'n': 148}
        trans[148] = {}  # accept: textlen
        trans[149] = {}  # accept: to

        # "worldwide"
        trans[150] = {'o': 151}
        trans[151] = {'r': 152}
        trans[152] = {'l': 153}
        trans[153] = {'d': 154}
        trans[154] = {'w': 155}
        trans[155] = {'i': 156}
        trans[156] = {'d': 157}
        trans[157] = {'e': 158}
        trans[158] = {}  # accept: worldwide

        # "Yes"
        trans[159] = {'e': 160}
        trans[160] = {'s': 161}
        trans[161] = {}  # accept: Yes

        return trans

    def _build_accept_states(self):
        """Map accept states to token types"""
        return {
            10:  RW_BIGDECIMAL,
            13:  RW_BOOL,
            19:  RW_CHARAT,
            22:  RW_CHECK,
            29:  RW_DECIMAL,
            33:  RW_DEFINE,
            39:  RW_DISPLAY,
            44:  RW_DURING,
            48:  RW_EACH,
            52:  RW_EMPTY,
            60:  RW_FALLBACK,
            65:  RW_FINISH,
            68:  RW_FIXED,
            71:  RW_FROM,
            75:  RW_GIVE,
            79:  RW_GROUP,
            85:  RW_LETTER,
            88:  RW_LIST,
            90:  RW_NO,
            93:  RW_NUM,
            99:  RW_OPTION,
            101: RW_ORD,
            109: RW_OTHERWISE,
            114: RW_OTHERWISECHECK,
            118: RW_READ,
            124: RW_SELECT,
            127: RW_SHOW,
            130: RW_SIZE,
            133: RW_SKIP,
            137: RW_START,
            139: RW_STEP,
            141: RW_STOP,
            145: RW_TEXT,
            148: RW_TEXTLEN,
            149: RW_TO,
            158: RW_WORLDWIDE,
            161: RW_YES,
        }

    def recognize_keyword(self, source, start_idx):
        """Try to recognize a keyword from source starting at start_idx"""
        state = 0
        idx = start_idx
        matched_text = ""
        last_accept_state = None
        last_accept_idx = start_idx
        last_accept_text = ""

        while idx < len(source):
            char = source[idx]

            if state in self.transitions and char in self.transitions[state]:
                next_state = self.transitions[state][char]
                state = next_state
                matched_text += char
                idx += 1

                if state in self.accept_states:
                    last_accept_state = state
                    last_accept_idx = idx
                    last_accept_text = matched_text
            else:
                break

        # Special handling for "otherwise check"

        if last_accept_state is not None:
            token_type = self.accept_states[last_accept_state]
            return token_type, last_accept_text, last_accept_idx

        return None, None, start_idx


# lexer
class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = Position(0, 0, 0, source)
        self.dfa = TransitionDFA()

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
        # Single-char punctuation is self-delimiting — no check needed
        skip_check = [NEWLINE, WHITESPACE_SPACE,
                      WHITESPACE_TAB, EOF, COMMENT_SINGLE, COMMENT_MULTI,
                      DELIM_LEFT_BRACE, DELIM_RIGHT_BRACE,
                      DELIM_SEMICOLON, DELIM_COLON]
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

        # Check current character (None means EOF)
        next_char = self.current_char

        # Handle EOF - only these specific delimiter types accept EOF
        if next_char is None:
            eof_allowed_types = ['space_nline']

            if delimiter_type not in eof_allowed_types:
                # EOF not allowed for this delimiter type
                delim_names = {
                    'space': 'space',
                    'space_nline': 'space or newline',
                    'delim1': 'space or "{"',
                    'delim2': 'space or "("',
                    'sem_col': '";"',
                    'id3': 'space or digit',
                }
                expected = delim_names.get(delimiter_type, delimiter_type)
                return LexicalError(pos_end, pos_end,
                                    f'Invalid delimiter after "{token_value}": expected {expected}, got EOF')
            else:
                # EOF is allowed for this type
                return None

        # Not EOF - check if current char is in expected delimiters
        if next_char not in expected_delims:
            delim_names = {
                'space': 'space',
                'space_nline': 'space or newline',
                'delim1': 'space or "{"',
                'delim2': 'space or "("',
                'delim3': 'space, letter, digit, (, “, ‘, [',
                'sem_col': '";"',
                'op_delim': 'space, letter, digit, (',
                'open_paren': '"("',
                'comma_delim': 'space, letter, digit, "(", """, "{", "[", or "\'",\n',
                'open_list': 'space, digit, """, "\'", "[" or "]"',
                'close_list': 'space, ";", ",", "=" or "."',
                'openparen_delim': 'space, letter, digit, "\'", """, ")" or "!"',
                'closeparen_delim': 'space, operator, ";", "{" or ")"',
                'bool_delim': 'space, "&", "|", "!", ";", ")", ":", ",", "]" or "="',
                'string_char': 'space, newline, ",", "+", ")", "]", "}" or ";"',
                'lit_delim': 'space, newline, }, ] ,) , ",\', ;, mathop, =, <, >, &, |, !',
                'identifier_del': 'space, newline, mathop, =, <, >, (, ), ], ,, ;, }, &, |, !,[',
                'num': 'digit',
                'id3': 'space or digit',
                'delim7': 'space, letter, digit, (, “, ‘, [',
                'dot_delim': 'digit or letter',
            }

            expected = delim_names.get(delimiter_type, delimiter_type)
            actual = f'"{next_char}"'

            return LexicalError(pos_end, pos_end,
                                f'Invalid delimiter after "{token_value}": expected {expected}, got {actual}')

        return None

    def tokenize(self):
        tokens = []
        errors = []

        while self.current_char != None:
            # whitespace
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

            # comments for both single and multi
            elif self.current_char == '~':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '~':
                    # Multi-line comment
                    self.advance()
                    comment_val = ''
                    found_closing = False

                    while self.current_char != None:
                        if self.current_char == '~' and self.peek() == '~':
                            found_closing = True
                            self.advance()
                            self.advance()
                            break
                        comment_val += self.current_char
                        self.advance()

                    pos_end = self.pos.copy()

                    if not found_closing:
                        errors.append(LexicalError(pos_start, pos_end,
                                                   'Unterminated multi-line comment - missing closing "~~"'))
                        continue

                    tokens.append(
                        Token(COMMENT_MULTI, comment_val.strip(), pos_start, pos_end))
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

            # RW or ID using DFA
            elif self.current_char in LETTERS:
                pos_start = self.pos.copy()

                # Try to recognize keyword using DFA
                token_type, matched_text, end_idx = self.dfa.recognize_keyword(
                    self.source, self.pos.idx)

                if token_type is not None:
                    # Check if next character is valid delimiter for keyword
                    next_char = self.source[end_idx] if end_idx < len(
                        self.source) else None
                    if next_char is None or (next_char not in LETTERNUM and next_char != '_'):
                        # Valid keyword match
                        for _ in range(len(matched_text)):
                            self.advance()

                        pos_end = self.pos.copy()

                        print(
                            f"Matched keyword: {matched_text}, next char: '{self.current_char}', EOF: {self.current_char is None}")

                        # Create token
                        if matched_text in ['Yes', 'No']:
                            token = Token(
                                matched_text, matched_text, pos_start, pos_end)  # Use value as type
                        else:
                            token = Token(token_type, matched_text,
                                          pos_start, pos_end)

                        # Check delimiter BEFORE adding token
                        delim_error = self.check_delimiter(
                            token.type, token.value, pos_end)
                        if delim_error:
                            errors.append(delim_error)
                            continue  # Drop token, don't add it

                            # Only add if delimiter is valid
                        tokens.append(token)
                        continue

                # Not a keyword, treat as identifier
                id_str = ''
                char_count = 0

                # Read up to 20 characters
                while self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_') and char_count < 20:
                    id_str += self.current_char
                    char_count += 1
                    self.advance()

                # Check what comes after the 20 characters
                if char_count == 20 and self.current_char != None and (self.current_char in LETTERNUM or self.current_char == '_'):
                    # Invalid delimiter after 20 characters
                    pos_error = self.pos.copy()

                    # Report improper delimiter error
                    errors.append(LexicalError(pos_start, pos_error,
                                               f'Invalid delimiter after "{id_str}": expected identifier_del, got "{self.current_char}"'))

                    continue

                pos_end = self.pos.copy()

                if len(id_str) == 0:
                    continue

                token = Token(IDENTIFIER, id_str, pos_start, pos_end)

                # Check delimiter BEFORE adding token
                delim_error = self.check_delimiter(
                    token.type, token.value, pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue  # Drop token

                # Only add if delimiter is valid
                tokens.append(token)
                continue

            # error for underscore
            elif self.current_char == '_':
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                errors.append(LexicalError(pos_start, self.pos.copy(),
                                           f'Invalid character "{char}"'))
                continue

            # numbers

            # numbers
            elif self.current_char in NUM or (self.current_char == '.' and self.peek() and self.peek() in NUM):
                pos_start = self.pos.copy()
                num_str = ''

                dot_count = 0
                int_dig_count = 0
                dec_dig_count = 0
                starts_with_dot = False

                # Handle leading decimal point (e.g., .4)
                if self.current_char == '.':
                    starts_with_dot = True
                    num_str += self.current_char
                    dot_count += 1
                    self.advance()

                    # Get decimal digits (up to 16)
                    while self.current_char != None and self.current_char in NUM and dec_dig_count < 16:
                        num_str += self.current_char
                        dec_dig_count += 1
                        self.advance()

                    # Check if there's a 17th decimal digit (invalid delimiter)
                    if dec_dig_count == 16 and self.current_char != None and self.current_char in NUM:
                        pos_error = self.pos.copy()
                        errors.append(LexicalError(pos_start, pos_error,
                                                   f'Invalid delimiter after "{num_str}": lit_delim, got "{self.current_char}"'))
                        continue
                else:
                    # Normal number starting with digit
                    # Read integer part (up to 11 digits)
                    while self.current_char != None and self.current_char in NUM and int_dig_count < 11:
                        num_str += self.current_char
                        int_dig_count += 1
                        self.advance()

                    # Check for leading zeros
                    # Check for leading zeros - invalid delimiter after 0
                    if len(num_str) > 1 and num_str[0] == '0':
                        # Drop the leading 0 and rewind to process remaining digits
                        errors.append(LexicalError(
                            pos_start,
                            pos_start,
                            f'Invalid delimiter after "0": expected lit_delim, got "{num_str[1]}"'
                        ))

                        # Rewind position to the second digit (after the 0)
                        self.pos = pos_start.copy()
                        self.pos.advance()  # Move past the '0'
                        if self.pos.idx < len(self.source):
                            self.current_char = self.source[self.pos.idx]
                        else:
                            self.current_char = None

                        continue

                    # Check if there's a 12th digit (invalid delimiter for integer)
                    if int_dig_count == 11 and self.current_char != None and self.current_char in NUM:
                        pos_error = self.pos.copy()
                        errors.append(LexicalError(pos_start, pos_error,
                                                   f'Invalid delimiter after "{num_str}": expected lit_delim, got "{self.current_char}"'))
                        continue

                    if self.current_char == '.':
                        # Check if next char is a digit (valid decimal point)
                        if self.peek() and self.peek() in NUM:
                            # FIRST decimal point
                            num_str += self.current_char
                            dot_count += 1
                            self.advance()

                            # DIGITS after decimal (up to 16)
                            while self.current_char != None and self.current_char in NUM and dec_dig_count < 16:
                                num_str += self.current_char
                                dec_dig_count += 1
                                self.advance()

                            # Check if there's a 17th decimal digit (invalid delimiter)
                            if dec_dig_count == 16 and self.current_char != None and self.current_char in NUM:
                                pos_error = self.pos.copy()
                                errors.append(LexicalError(pos_start, pos_error,
                                                           f'Invalid delimiter after "{num_str}": expected lit_delim, got "{self.current_char}"'))
                                continue
                        else:
                            # Dot not followed by digit - invalid delimiter
                            num_str += self.current_char  # Include the dot in error message
                            self.advance()  # Move past the dot
                            pos_error = self.pos.copy()
                            errors.append(LexicalError(pos_start, pos_error,
                                                       f'Invalid character after "{num_str}": expected digit, got "{self.current_char if self.current_char else "EOF"}"'))
                            continue

                pos_end = self.pos.copy()

                pos_end = self.pos.copy()

                # Create appropriate token
                if dot_count == 0:
                    token = Token(LIT_NUMBER, num_str, pos_start, pos_end)
                else:
                    token = Token(LIT_DECIMAL, num_str, pos_start, pos_end)

                # Check delimiter BEFORE adding token
                delim_error = self.check_delimiter(
                    token.type, token.value, pos_end)
                if delim_error:
                    errors.append(delim_error)
                    # Invalid delimiter - discard this token, don't add it
                    # Continue from current position (the invalid delimiter)
                    continue

                # Only add token if delimiter was valid
                tokens.append(token)
                continue

            # stringlit
            # stringlit
            elif self.current_char == '"':
                pos_start = self.pos.copy()
                string_val = '"'  # Start with opening quote
                self.advance()
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
                    string_val += '"'  # Add closing quote
                    self.advance()  # Move past closing quote

                pos_end = self.pos.copy()

                if not found_closing:
                    errors.append(LexicalError(pos_start, pos_end,
                                               'Unterminated string literal - missing closing """'))
                    continue

                # Check delimiter after string
                delim_error = self.check_delimiter(
                    LIT_STRING, string_val, pos_end)
                if delim_error:
                    errors.append(delim_error)
                    # Drop the string token, continue from current position (invalid delimiter)
                    continue

                # Valid delimiter - add token
                token = Token(LIT_STRING, string_val, pos_start, pos_end)
                tokens.append(token)
                continue

            # charlit
            # charlit
            # charlit
            # Replace the character literal section (around line 1050) with this:

            elif self.current_char == "'":
                pos_start = self.pos.copy()
                char_val = "'"  # Start with opening quote
                self.advance()

                # Check for EOF immediately after opening quote
                if self.current_char == None:
                    errors.append(LexicalError(pos_start, self.pos.copy(),
                                               'Unterminated character literal - missing closing "\'"'))
                    continue

                # Check for immediate closing quote (empty literal) - accept it as valid
                if self.current_char == "'":
                    # Empty character literal '' - this is VALID, tokenize it
                    char_val += "'"
                    self.advance()
                    pos_end = self.pos.copy()

                    # Check delimiter after character literal
                    delim_error = self.check_delimiter(
                        LIT_CHARACTER, char_val, pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue

                    # Valid empty character literal - add token
                    token = Token(LIT_CHARACTER, char_val, pos_start, pos_end)
                    tokens.append(token)
                    continue

                # Read exactly ONE character (or escape sequence)
                if self.current_char == '\\':
                    # Escape sequence
                    char_val += self.current_char
                    self.advance()

                    if self.current_char in ['n', 't', '\\', '"', "'"]:
                        char_val += self.current_char
                        self.advance()
                    else:
                        # Invalid escape sequence
                        errors.append(LexicalError(pos_start, self.pos.copy(),
                                                   f'Invalid escape sequence "\\{self.current_char if self.current_char else "EOF"}"'))
                        continue
                else:
                    # Regular single character (including space ' ')
                    char_val += self.current_char
                    self.advance()

                # Now we MUST have closing quote '
                if self.current_char != "'":
                    # More content before closing quote - invalid delimiter
                    errors.append(LexicalError(pos_start, self.pos.copy(),
                                               f'Invalid character after "{char_val}": expected closing single quote "\'", got "{self.current_char if self.current_char else "EOF"}"'))
                    continue

                # Found closing quote
                char_val += "'"
                self.advance()
                pos_end = self.pos.copy()

                # Check delimiter after character literal
                delim_error = self.check_delimiter(
                    LIT_CHARACTER, char_val, pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                # Valid character literal - add token
                token = Token(LIT_CHARACTER, char_val, pos_start, pos_end)
                tokens.append(token)
                continue

            # operators
            # operators
            elif self.current_char == '+':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_ADDITION_ASSIGN, '+=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_ADDITION_ASSIGN,
                                  '+=', pos_start, pos_end))
                elif self.current_char == '+':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_INCREMENT, '++', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_INCREMENT, '++', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_ADDITION, '+', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_ADDITION, '+', pos_start, pos_end))
                continue

            elif self.current_char == '-':
                pos_start = self.pos.copy()
                self.advance()

                # Negative number: -digit (no space) always tokenized as negative literal
                if self.current_char and self.current_char != ' ' and (self.current_char in NUM or (self.current_char == '.' and self.peek() and self.peek() in NUM)):
                    num_start = pos_start
                    num_str = '-'
                    dot_count = 0
                    int_dig_count = 0
                    dec_dig_count = 0

                    # Special handling for -0
                    if self.current_char == '0':
                        num_str += '0'
                        self.advance()

                        # -0 can ONLY continue to decimal, not standalone
                        if self.current_char == '.' and self.peek() and self.peek() in NUM:
                            # Valid: -0.5
                            num_str += self.current_char
                            dot_count += 1
                            self.advance()

                            while self.current_char != None and self.current_char in NUM and dec_dig_count < 16:
                                num_str += self.current_char
                                dec_dig_count += 1
                                self.advance()

                            # Check if there's a 17th decimal digit (invalid delimiter)
                            if dec_dig_count == 16 and self.current_char != None and self.current_char in NUM:
                                pos_error = self.pos.copy()
                                errors.append(LexicalError(num_start, pos_error,
                                                           f'Invalid delimiter after "{num_str}": expected lit_delim "{self.current_char}"'))
                                continue

                            num_end = self.pos.copy()

                            # Create decimal token
                            token = Token(LIT_DECIMAL, num_str,
                                          num_start, num_end)

                            # Check delimiter
                            delim_error = self.check_delimiter(
                                token.type, token.value, num_end)
                            if delim_error:
                                errors.append(delim_error)
                                continue

                            tokens.append(token)
                            continue
                        else:
                            # -0 NOT followed by .digit - incomplete number literal
                            if self.current_char == '.':
                                # Has dot but no digits after - advance past the dot
                                self.advance()  # Move past the '.'
                                errors.append(LexicalError(
                                    num_start,
                                    self.pos.copy(),
                                    f'Invalid character after "-0.": expected digits, got "{self.current_char if self.current_char else "EOF"}"'
                                ))
                            else:
                                # No dot at all
                                errors.append(LexicalError(
                                    num_start,
                                    self.pos.copy(),
                                    f'Invalid character after "-0": expected decimal point and digits, got "{self.current_char if self.current_char else "EOF"}"'
                                ))
                            # Position is now ready to continue from the invalid character
                            continue

                    # Normal negative number (not starting with 0): -1, -2, -999, etc.
                    while self.current_char != None and self.current_char in NUM and int_dig_count < 10:
                        num_str += self.current_char
                        int_dig_count += 1
                        self.advance()

                    # Check if there's an 11th digit (invalid delimiter)
                    if int_dig_count == 10 and self.current_char != None and self.current_char in NUM:
                        pos_error = self.pos.copy()
                        errors.append(LexicalError(num_start, pos_error,
                                                   f'Invalid delimiter after "{num_str}" expected lit_delim, got "{self.current_char}"'))
                        continue

                    # Handle optional decimal point for non-zero numbers
                    if self.current_char == '.':
                        if self.peek() and self.peek() in NUM:
                            num_str += self.current_char
                            dot_count += 1
                            self.advance()

                            while self.current_char != None and self.current_char in NUM and dec_dig_count < 16:
                                num_str += self.current_char
                                dec_dig_count += 1
                                self.advance()

                            # Check if there's a 17th decimal digit (invalid delimiter)
                            if dec_dig_count == 16 and self.current_char != None and self.current_char in NUM:
                                pos_error = self.pos.copy()
                                errors.append(LexicalError(num_start, pos_error,
                                                           f'Invalid delimiter after "{num_str}" expected lit_delim, got "{self.current_char}"'))
                                continue
                        else:
                            # Dot not followed by digit
                            num_str += self.current_char
                            self.advance()
                            errors.append(LexicalError(num_start, self.pos.copy(),
                                                       f'Invalid delimiter after "{num_str}": expected digit, got "{self.current_char if self.current_char else "EOF"}"'))
                            continue

                    num_end = self.pos.copy()

                    # Create token
                    if dot_count == 0:
                        token = Token(LIT_NUMBER, num_str,
                                      num_start, num_end)
                    else:
                        token = Token(LIT_DECIMAL, num_str,
                                      num_start, num_end)

                    # Check delimiter
                    delim_error = self.check_delimiter(
                        token.type, token.value, num_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue

                    tokens.append(token)
                    continue

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_SUBTRACTION_ASSIGN, '-=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue
                    tokens.append(Token(OP_SUBTRACTION_ASSIGN,
                                  '-=', pos_start, pos_end))
                elif self.current_char == '-':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_DECREMENT, '--', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue
                    tokens.append(
                        Token(OP_DECREMENT, '--', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_SUBTRACTION, '-', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue
                    tokens.append(
                        Token(OP_SUBTRACTION, '-', pos_start, pos_end))
                continue

            elif self.current_char == '*':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '*':
                    self.advance()
                    # Check for **=
                    if self.current_char == '=':
                        self.advance()
                        pos_end = self.pos.copy()
                        delim_error = self.check_delimiter(
                            OP_EXPONENTIATION_ASSIGN, '**=', pos_end)
                        if delim_error:
                            errors.append(delim_error)
                            continue  # Drop token
                        tokens.append(
                            Token(OP_EXPONENTIATION_ASSIGN, '**=', pos_start, pos_end))
                    else:
                        pos_end = self.pos.copy()
                        delim_error = self.check_delimiter(
                            OP_EXPONENTIATION, '**', pos_end)
                        if delim_error:
                            errors.append(delim_error)
                            continue  # Drop token
                        tokens.append(
                            Token(OP_EXPONENTIATION, '**', pos_start, pos_end))
                elif self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_MULTIPLICATION_ASSIGN, '*=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_MULTIPLICATION_ASSIGN,
                                  '*=', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_MULTIPLICATION, '*', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_MULTIPLICATION, '*', pos_start, pos_end))
                continue

            elif self.current_char == '/':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '/':
                    # // or //=
                    self.advance()
                    if self.current_char == '=':
                        self.advance()
                        pos_end = self.pos.copy()
                        delim_error = self.check_delimiter(
                            OP_INTEGER_DIVISION_ASSIGN, '//=', pos_end)
                        if delim_error:
                            errors.append(delim_error)
                            continue
                        tokens.append(Token(OP_INTEGER_DIVISION_ASSIGN,
                                      '//=', pos_start, pos_end))
                    else:
                        pos_end = self.pos.copy()
                        delim_error = self.check_delimiter(
                            OP_INTEGER_DIVISION, '//', pos_end)
                        if delim_error:
                            errors.append(delim_error)
                            continue
                        tokens.append(Token(OP_INTEGER_DIVISION,
                                      '//', pos_start, pos_end))
                elif self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_DIVISION_ASSIGN, '/=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_DIVISION_ASSIGN,
                                  '/=', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_DIVISION, '/', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_DIVISION, '/', pos_start, pos_end))
                continue

            elif self.current_char == '%':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_MODULUS_ASSIGN, '%=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_MODULUS_ASSIGN, '%=', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_MODULUS, '%', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_MODULUS, '%', pos_start, pos_end))
                continue

            elif self.current_char == '=':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_EQUAL_TO, '==', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_EQUAL_TO, '==', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_ASSIGNMENT, '=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_ASSIGNMENT, '=', pos_start, pos_end))
                continue

            elif self.current_char == '!':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_NOT_EQUAL, '!=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_NOT_EQUAL, '!=', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_LOGICAL_NOT, '!', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_LOGICAL_NOT, '!', pos_start, pos_end))
                continue

            elif self.current_char == '>':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_GREATER_EQUAL, '>=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_GREATER_EQUAL, '>=', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_GREATER_THAN, '>', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_GREATER_THAN, '>', pos_start, pos_end))
                continue

            elif self.current_char == '<':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '=':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_LESS_EQUAL, '<=', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_LESS_EQUAL, '<=', pos_start, pos_end))
                else:
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_LESS_THAN, '<', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(Token(OP_LESS_THAN, '<', pos_start, pos_end))
                continue

            elif self.current_char == '&':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '&':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_LOGICAL_AND, '&&', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_LOGICAL_AND, '&&', pos_start, pos_end))
                else:
                    # Single & - invalid delimiter (expected another &)
                    pos_end = self.pos.copy()
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Invalid character after "&": expected "&", got "{self.current_char if self.current_char else "EOF"}"'))
                continue

            elif self.current_char == '|':
                pos_start = self.pos.copy()
                self.advance()

                if self.current_char == '|':
                    self.advance()
                    pos_end = self.pos.copy()
                    delim_error = self.check_delimiter(
                        OP_LOGICAL_OR, '||', pos_end)
                    if delim_error:
                        errors.append(delim_error)
                        continue  # Drop token
                    tokens.append(
                        Token(OP_LOGICAL_OR, '||', pos_start, pos_end))
                else:
                    # Single | - invalid delimiter (expected another |)
                    pos_end = self.pos.copy()
                    errors.append(LexicalError(pos_start, pos_end,
                                               f'Invalid character after "|": expected "|", got "{self.current_char if self.current_char else "EOF"}"'))
                continue

            # delimiters
            elif self.current_char == '(':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_LEFT_PAREN, '(', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_LEFT_PAREN, '(', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == ')':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_RIGHT_PAREN, ')', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_RIGHT_PAREN, ')', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == '[':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_LEFT_BRACKET, '[', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_LEFT_BRACKET, '[', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == ']':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_RIGHT_BRACKET, ']', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_RIGHT_BRACKET, ']', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == '{':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_LEFT_BRACE, '{', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_LEFT_BRACE, '{', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == '}':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_RIGHT_BRACE, '}', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_RIGHT_BRACE, '}', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == ';':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(
                    DELIM_SEMICOLON, ';', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue  # Drop semicolon token

                token = Token(DELIM_SEMICOLON, ';', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == ':':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(DELIM_COLON, ':', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_COLON, ':', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == ',':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()

                delim_error = self.check_delimiter(DELIM_COMMA, ',', pos_end)
                if delim_error:
                    errors.append(delim_error)
                    continue

                token = Token(DELIM_COMMA, ',', pos_start, pos_end)
                tokens.append(token)
                continue

            elif self.current_char == '.':
                pos_start = self.pos.copy()
                self.advance()
                pos_end = self.pos.copy()
                token = Token(DELIM_DOT, '.', pos_start, pos_end)

                # Check delimiter BEFORE adding token
                delim_error = self.check_delimiter(
                    token.type, token.value, pos_end)
                if delim_error:
                    errors.append(delim_error)
                    # Invalid delimiter - discard this token
                    continue

                # Only add token if delimiter was valid
                tokens.append(token)
                continue

            # unrecognized char
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


# gui tkinter


class EditorTab(tk.Frame):
    """One notebook page: source editor + token table + terminal + subprocess.

    Owns all per-file state. The parent KuCodeLexerGUI is a thin shell that
    delegates Analyze/Clear/Save/Open/Toggle-Tokens to the active tab.
    """

    # Shared color palette (mirrors original KuCodeLexerGUI values)
    BG_PANEL = "#1a1a2e"
    BG_DARK = "#152238"

    def __init__(self, master, gui, filepath=None):
        super().__init__(master, bg="#0d1b2a")
        self.gui = gui
        self.filepath = filepath
        self.dirty = False
        self.token_table_visible = False

        # Subprocess state
        self._subprocess = None
        self._temp_file_path = None
        self._running = False
        self._run_id = 0
        self._stdout_thread = None
        self._stderr_thread = None
        self._watcher_thread = None
        self._input_buffer = ""

        # Per-tab zoom state for source editor and terminal
        self._SOURCE_FONT_DEFAULT = 10
        self._TERMINAL_FONT_DEFAULT = 9
        self._FONT_MIN = 6
        self._FONT_MAX = 48
        self._source_font_size = self._SOURCE_FONT_DEFAULT
        self._terminal_font_size = self._TERMINAL_FONT_DEFAULT

        panel_bg = self.BG_PANEL
        dark_blue = self.BG_DARK

        # Vertical PanedWindow: (source + tokens) on top, terminal on bottom
        self.paned = tk.PanedWindow(self, orient=tk.VERTICAL,
                                    bg="#0d1b2a", sashwidth=8,
                                    sashrelief=tk.RAISED, bd=0)
        self.paned.pack(fill=tk.BOTH, expand=True)

        main_container = tk.Frame(self.paned, bg="#0d1b2a")
        self.paned.add(main_container, minsize=200)

        # Left Panel - Source Code
        left_panel = tk.Frame(main_container, bg=panel_bg,
                              relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        source_label = tk.Label(left_panel, text="Source Code",
                                font=("Courier New", 12, "bold"),
                                bg=panel_bg, fg="white", anchor="w")
        source_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        line_frame = tk.Frame(left_panel, bg="white")
        line_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.line_numbers = tk.Text(line_frame, width=4, padx=5, takefocus=0,
                                    border=0, background='#0d1b2a', fg='#6c757d',
                                    state='disabled', wrap='none',
                                    font=("Courier New", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.bind('<MouseWheel>', lambda e: 'break')
        self.line_numbers.bind('<Button-1>', lambda e: 'break')
        self.line_numbers.bind('<B1-Motion>', lambda e: 'break')

        self.source_text = scrolledtext.ScrolledText(
            line_frame, wrap=tk.NONE, font=("Courier New", 10),
            bg=dark_blue, fg="#e0e0e0", insertbackground="white",
            selectbackground="#264f78",
            undo=True, autoseparators=False, maxundo=-1)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.source_text.bind('<KeyRelease>', self.update_line_numbers)
        self.source_text.bind('<Tab>', self._on_indent_key)
        self.source_text.bind('<KeyPress>', self._on_maybe_undo_sep)
        self.source_text.bind('<Control-y>', self._redo)
        self.source_text.bind('<Control-Y>', self._redo)
        self.source_text.bind('<Control-Shift-z>', self._redo)
        self.source_text.bind('<Control-Shift-Z>', self._redo)
        self.source_text.vbar.config(command=self._synced_yview)
        self.source_text.bind('<MouseWheel>', self._on_source_scroll)
        self.source_text.bind('<Button-4>', self._on_source_scroll)
        self.source_text.bind('<Button-5>', self._on_source_scroll)

        # Source editor zoom (Ctrl+= / Ctrl+- / Ctrl+0 / Ctrl+MouseWheel)
        self.source_text.bind('<Control-plus>', lambda e: self._zoom_source(1))
        self.source_text.bind(
            '<Control-equal>', lambda e: self._zoom_source(1))
        self.source_text.bind('<Control-KP_Add>',
                              lambda e: self._zoom_source(1))
        self.source_text.bind(
            '<Control-minus>', lambda e: self._zoom_source(-1))
        self.source_text.bind('<Control-KP_Subtract>',
                              lambda e: self._zoom_source(-1))
        self.source_text.bind(
            '<Control-0>', lambda e: self._reset_zoom_source())
        self.source_text.bind(
            '<Control-KP_0>', lambda e: self._reset_zoom_source())
        self.source_text.bind('<Control-MouseWheel>',
                              self._on_source_ctrl_wheel)

        # Dirty tracking via Tk's built-in modified flag
        self.source_text.edit_modified(False)
        self.source_text.bind('<<Modified>>', self._on_source_modified)

        # Right Panel - Tokens (hidden by default, toggle with header button)
        self.right_panel = tk.Frame(main_container, bg=panel_bg,
                                    relief=tk.RAISED, bd=1)
        self._main_container = main_container

        tokens_label = tk.Label(self.right_panel, text="Lexical Table",
                                font=("Courier New", 12, "bold"),
                                bg=panel_bg, fg="white", anchor="w")
        tokens_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        table_frame = tk.Frame(self.right_panel)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.token_table = ttk.Treeview(table_frame,
                                        columns=("Lexeme", "Token"),
                                        show="headings",
                                        yscrollcommand=vsb.set,
                                        xscrollcommand=hsb.set,
                                        style="Treeview")
        vsb.config(command=self.token_table.yview)
        hsb.config(command=self.token_table.xview)

        self.token_table.heading("Lexeme", text="LEXEME", anchor="center")
        self.token_table.heading("Token", text="TOKEN", anchor="center")
        self.token_table.column("Lexeme", width=250, anchor="center")
        self.token_table.column("Token", width=250, anchor="center")
        self.token_table.pack(fill=tk.BOTH, expand=True)

        # Bottom Panel - Terminal
        terminal_frame = tk.Frame(self.paned, bg=panel_bg,
                                  relief=tk.RAISED, bd=1)
        self.paned.add(terminal_frame, minsize=100)

        terminal_label = tk.Label(terminal_frame, text="Terminal",
                                  font=("Courier New", 12, "bold"),
                                  bg=panel_bg, fg="white", anchor="w")
        terminal_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.terminal_text = scrolledtext.ScrolledText(
            terminal_frame, wrap=tk.WORD, font=("Courier New", 9),
            bg=dark_blue, fg="#00ff00", height=6)
        self.terminal_text.pack(fill=tk.BOTH, expand=True,
                                padx=10, pady=(0, 10))

        # Terminal zoom (Ctrl+= / Ctrl+- / Ctrl+0 / Ctrl+MouseWheel)
        self.terminal_text.bind(
            '<Control-plus>', lambda e: self._zoom_terminal(1))
        self.terminal_text.bind(
            '<Control-equal>', lambda e: self._zoom_terminal(1))
        self.terminal_text.bind(
            '<Control-KP_Add>', lambda e: self._zoom_terminal(1))
        self.terminal_text.bind(
            '<Control-minus>', lambda e: self._zoom_terminal(-1))
        self.terminal_text.bind('<Control-KP_Subtract>',
                                lambda e: self._zoom_terminal(-1))
        self.terminal_text.bind(
            '<Control-0>', lambda e: self._reset_zoom_terminal())
        self.terminal_text.bind(
            '<Control-KP_0>', lambda e: self._reset_zoom_terminal())
        self.terminal_text.bind('<Control-MouseWheel>',
                                self._on_terminal_ctrl_wheel)

        self.update_line_numbers()

    # ── Title / dirty ─────────────────────────────────────────

    def title(self):
        import os
        base = os.path.basename(
            self.filepath) if self.filepath else self._untitled_name
        return ("*" if self.dirty else "") + base

    @property
    def _untitled_name(self):
        return getattr(self, "_untitled_label", "Untitled")

    def set_untitled_name(self, name):
        self._untitled_label = name

    def _on_source_modified(self, event=None):
        # <<Modified>> fires on every insert/delete (user or programmatic).
        # We latch it; callers that load content should clear it via mark_clean.
        if self.source_text.edit_modified():
            self.source_text.edit_modified(False)
            if not self.dirty:
                self.dirty = True
                self.gui._refresh_tab_title(self)

    def mark_clean(self):
        self.dirty = False
        self.source_text.edit_modified(False)
        self.gui._refresh_tab_title(self)

    _UNDO_SEP_CHARS = frozenset(' \n\r\t.,;:!?()[]{}"\'/\\+-=<>*&|^~@#')

    def _on_maybe_undo_sep(self, event):
        if event.char in self._UNDO_SEP_CHARS or event.keysym in ('Delete', 'BackSpace'):
            self.source_text.edit_separator()

    def _redo(self, event=None):
        try:
            self.source_text.edit_redo()
        except Exception:
            pass
        return 'break'

    # ── Editor helpers ────────────────────────────────────────

    def highlight_syntax(self, event=None):
        self.source_text.tag_remove("keyword", "1.0", "end")
        self.source_text.tag_remove("string", "1.0", "end")
        self.source_text.tag_remove("comment", "1.0", "end")
        self.source_text.tag_remove("number", "1.0", "end")
        self.source_text.tag_remove("operator", "1.0", "end")

        content = self.source_text.get("1.0", "end-1c")

        string_ranges = []
        comment_ranges = []

        string_pattern = r'"[^"]*"|\'[^\']*\''
        for match in re.finditer(string_pattern, content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("string", start_idx, end_idx)
            string_ranges.append((match.start(), match.end()))

        comment_pattern = r'~[^\n]*|~~.*?~~'
        for match in re.finditer(comment_pattern, content, re.DOTALL):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("comment", start_idx, end_idx)
            comment_ranges.append((match.start(), match.end()))

        def is_inside_string_or_comment(pos):
            for start, end in string_ranges:
                if start <= pos < end:
                    return True
            for start, end in comment_ranges:
                if start <= pos < end:
                    return True
            return False

        keywords_pattern = r'\b(' + '|'.join([
            'start', 'finish', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool',
            'Yes', 'No', 'empty', 'read', 'show', 'display', 'check', 'otherwise', 'otherwisecheck',
            'fallback', 'select', 'option', 'each', 'during', 'from', 'to', 'step',
            'stop', 'skip', 'give', 'define', 'worldwide', 'fixed', 'list', 'group', 'size', 'textlen', 'charat', 'ord'
        ]) + r')\b'

        for match in re.finditer(keywords_pattern, content):
            if not is_inside_string_or_comment(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.source_text.tag_add("keyword", start_idx, end_idx)

        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, content):
            if not is_inside_string_or_comment(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.source_text.tag_add("number", start_idx, end_idx)

        operator_pattern = r'[+\-*/%=<>!&|]+'
        for match in re.finditer(operator_pattern, content):
            if not is_inside_string_or_comment(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.source_text.tag_add("operator", start_idx, end_idx)

        self.source_text.tag_config("keyword", foreground="#c678dd")
        self.source_text.tag_config("string", foreground="#98c379")
        self.source_text.tag_config("comment", foreground="#5c6370")
        self.source_text.tag_config("number", foreground="#d19a66")
        self.source_text.tag_config("operator", foreground="#61afef")

    def update_line_numbers(self, event=None):
        line_count = self.source_text.get("1.0", "end-1c").count('\n') + 1
        line_numbers_string = "\n".join(str(i)
                                        for i in range(1, line_count + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.source_text.yview()[0])
        self.highlight_syntax()

    def _synced_yview(self, *args):
        self.source_text.yview(*args)
        self.line_numbers.yview_moveto(self.source_text.yview()[0])

    def _on_source_scroll(self, event=None):
        self.after_idle(
            lambda: self.line_numbers.yview_moveto(self.source_text.yview()[0])
        )

    # ── Zoom (font size) ─────────────────────────────────────
    def _apply_source_font(self):
        font = ("Courier New", self._source_font_size)
        self.source_text.configure(font=font)
        self.line_numbers.configure(font=font)

    def _apply_terminal_font(self):
        self.terminal_text.configure(
            font=("Courier New", self._terminal_font_size))

    def _zoom_source(self, delta):
        new_size = max(self._FONT_MIN,
                       min(self._FONT_MAX, self._source_font_size + delta))
        if new_size != self._source_font_size:
            self._source_font_size = new_size
            self._apply_source_font()
        return 'break'

    def _zoom_terminal(self, delta):
        new_size = max(self._FONT_MIN,
                       min(self._FONT_MAX, self._terminal_font_size + delta))
        if new_size != self._terminal_font_size:
            self._terminal_font_size = new_size
            self._apply_terminal_font()
        return 'break'

    def _reset_zoom_source(self):
        if self._source_font_size != self._SOURCE_FONT_DEFAULT:
            self._source_font_size = self._SOURCE_FONT_DEFAULT
            self._apply_source_font()
        return 'break'

    def _reset_zoom_terminal(self):
        if self._terminal_font_size != self._TERMINAL_FONT_DEFAULT:
            self._terminal_font_size = self._TERMINAL_FONT_DEFAULT
            self._apply_terminal_font()
        return 'break'

    def _on_source_ctrl_wheel(self, event):
        delta = 1 if event.delta > 0 else -1
        return self._zoom_source(delta)

    def _on_terminal_ctrl_wheel(self, event):
        delta = 1 if event.delta > 0 else -1
        return self._zoom_terminal(delta)

    def _on_indent_key(self, event):
        self.source_text.insert(tk.INSERT, '    ')
        return 'break'

    def toggle_token_table(self):
        if self.token_table_visible:
            self.right_panel.pack_forget()
            self.token_table_visible = False
        else:
            self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH,
                                  expand=True, padx=(5, 0))
            self.token_table_visible = True

    def clear_all(self):
        self._cleanup_subprocess()
        self.source_text.delete(1.0, tk.END)
        self.token_table.delete(*self.token_table.get_children())
        self.terminal_text.delete(1.0, tk.END)
        self.update_line_numbers()
        self.mark_clean()

    # ── Subprocess execution ─────────────────────────────────

    def _execute_code(self, python_code):
        import subprocess
        import threading
        import tempfile
        import sys

        self._cleanup_subprocess()
        self._run_id += 1
        current_run_id = self._run_id
        self._running = True

        self._temp_file_path = tempfile.mktemp(suffix='.py')
        with open(self._temp_file_path, 'w', encoding='utf-8') as f:
            f.write(python_code)

        self._subprocess = subprocess.Popen(
            [sys.executable, '-u', self._temp_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        self._input_buffer = ""
        self.terminal_text.bind('<Key>', self._on_terminal_key)

        self._stdout_thread = threading.Thread(
            target=self._read_stream,
            args=(self._subprocess.stdout, False),
            daemon=True)
        self._stderr_thread = threading.Thread(
            target=self._read_stream,
            args=(self._subprocess.stderr, True),
            daemon=True)
        self._watcher_thread = threading.Thread(
            target=self._watch_process,
            args=(current_run_id,),
            daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()
        self._watcher_thread.start()

    def _read_stream(self, stream, is_error=False):
        tag = "error" if is_error else ""
        try:
            while True:
                char = stream.read(1)
                if not char:
                    break
                self.after(0, self._append_output, char, tag)
        except (ValueError, OSError):
            pass

    def _append_output(self, text, tag=""):
        self.terminal_text.insert(tk.END, text, tag if tag else None)
        self.terminal_text.see(tk.END)

    def _on_terminal_key(self, event):
        if event.state & 0x4 and event.keysym in ('c', 'C', 'a', 'A'):
            return

        if not self._running:
            return 'break'

        if event.keysym == 'Return':
            if self._subprocess and self._subprocess.poll() is None:
                self.terminal_text.insert(tk.END, '\n')
                self.terminal_text.see(tk.END)
                try:
                    self._subprocess.stdin.write(self._input_buffer + '\n')
                    self._subprocess.stdin.flush()
                except (BrokenPipeError, OSError):
                    pass
                self._input_buffer = ""
            return 'break'

        if event.keysym == 'BackSpace':
            if self._input_buffer:
                self._input_buffer = self._input_buffer[:-1]
                self.terminal_text.delete('end-2c', 'end-1c')
            return 'break'

        if event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                            'Alt_L', 'Alt_R', 'Caps_Lock', 'Escape', 'Tab',
                            'Left', 'Right', 'Up', 'Down', 'Home', 'End',
                            'Delete', 'Insert', 'F1', 'F2', 'F3', 'F4',
                            'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'):
            return 'break'

        if event.char and event.char.isprintable():
            self._input_buffer += event.char
            self.terminal_text.insert(tk.END, event.char)
            self.terminal_text.see(tk.END)

        return 'break'

    def _watch_process(self, run_id):
        proc = self._subprocess
        if proc:
            proc.wait()
            if self._stdout_thread:
                self._stdout_thread.join(timeout=3)
            if self._stderr_thread:
                self._stderr_thread.join(timeout=3)
            exit_code = proc.returncode
            self.after(0, self._on_process_done, exit_code, run_id)

    def _on_process_done(self, exit_code, run_id=None):
        if run_id is not None and run_id != self._run_id:
            return
        self._running = False
        self.terminal_text.insert(tk.END, f"\n{'='*50}\n")
        if exit_code == 0:
            self.terminal_text.insert(
                tk.END, "Program finished successfully.\n", "success")
        else:
            self.terminal_text.insert(
                tk.END, f"Program exited with code {exit_code}.\n", "error")
        self.terminal_text.see(tk.END)
        self.terminal_text.unbind('<Key>')
        self.terminal_text.tag_config("error", foreground="#ff6b6b")
        self.terminal_text.tag_config("success", foreground="#00ff00")

    def _cleanup_subprocess(self):
        import os
        if self._subprocess and self._subprocess.poll() is None:
            self._subprocess.terminate()
            try:
                self._subprocess.wait(timeout=5)
            except Exception:
                self._subprocess.kill()
        self._subprocess = None
        if self._temp_file_path:
            try:
                os.unlink(self._temp_file_path)
            except OSError:
                pass
            self._temp_file_path = None
        self._running = False

    # ── Pipeline entry ────────────────────────────────────────

    def analyze(self):
        self._cleanup_subprocess()
        self.token_table.delete(*self.token_table.get_children())
        self.terminal_text.delete(1.0, tk.END)

        source = self.source_text.get(1.0, "end-1c")
        if not source.strip():
            self.terminal_text.insert(tk.END,
                                      "Error: No source code to analyze\n")
            return

        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        for token in tokens:
            if token.type not in [EOF]:
                lexeme = token.value if token.value else "-"
                if token.type == LIT_STRING:
                    display_type = "string_lit"
                elif token.type == LIT_CHARACTER:
                    display_type = "char_lit"
                elif token.type == LIT_NUMBER:
                    display_type = "num_lit"
                elif token.type == LIT_DECIMAL:
                    display_type = "decimal_lit"
                else:
                    display_type = token.type
                self.token_table.insert("", tk.END,
                                        values=(lexeme, display_type))

        if errors:
            self.terminal_text.insert(
                tk.END, "✗ Lexical analysis failed:\n\n", "error")
            for error in errors:
                self.terminal_text.insert(tk.END, str(error) + "\n", "error")
            self.terminal_text.tag_config("error", foreground="#ff6b6b")
            return

        self.terminal_text.insert(
            tk.END, "✓ Lexical analysis passed.\n", "success")
        self.terminal_text.insert(
            tk.END, "\nStarting syntax analysis...\n\n", "info")

        parser_tokens = prepare_tokens_for_parser(tokens)

        from table_driven_parser import TableDrivenParser as Parser
        parser = Parser(parser_tokens)

        try:
            ast = parser.parse()
            self.terminal_text.insert(
                tk.END, "✓ Syntax analysis passed.\n", "success")

            self.terminal_text.insert(
                tk.END, "\nStarting semantic analysis...\n\n", "info")

            from semantic_analyzer import SemanticAnalyzer
            analyzer = SemanticAnalyzer(ast)
            quadruples, sem_errors = analyzer.analyze()

            if sem_errors:
                self.terminal_text.insert(
                    tk.END,
                    f"✗ Semantic analysis failed "
                    f"({len(sem_errors)} error(s)):\n\n",
                    "error")
                for err in sem_errors:
                    self.terminal_text.insert(tk.END, f"  {err}\n", "error")
            else:
                self.terminal_text.insert(
                    tk.END, "✓ Semantic analysis passed.\n", "success")

                if analyzer.warnings:
                    for w in analyzer.warnings:
                        self.terminal_text.insert(
                            tk.END, f"  {w}\n", "warning")

                self.terminal_text.insert(
                    tk.END, "\nStarting code generation...\n\n", "info")

                from code_generator import TACCodeGenerator
                gen = TACCodeGenerator(analyzer.quadruples,
                                       analyzer.symbol_table)
                python_code = gen.generate()

                self.terminal_text.insert(
                    tk.END, "✓ Code generation passed.\n", "success")
                self.terminal_text.insert(
                    tk.END, f"\n{'='*50}\n", "info")
                self.terminal_text.insert(
                    tk.END, "Program Output:\n\n", "info")

                self.terminal_text.tag_config("error", foreground="#ff6b6b")
                self.terminal_text.tag_config("success", foreground="#00ff00")
                self.terminal_text.tag_config("info", foreground="#61afef")
                self.terminal_text.tag_config("warning", foreground="#e5c07b")

                self._execute_code(python_code)
                return

        except SyntaxError as e:
            self.terminal_text.insert(
                tk.END, "✗ Syntax analysis failed:\n\n", "error")
            self.terminal_text.insert(tk.END, str(e) + "\n", "error")

        self.terminal_text.tag_config("error", foreground="#ff6b6b")
        self.terminal_text.tag_config("success", foreground="#00ff00")
        self.terminal_text.tag_config("info", foreground="#61afef")

        displayable_tokens = [t for t in tokens if t.type not in [EOF]]
        self.terminal_text.insert(tk.END, f"\n{'='*50}\n")
        self.terminal_text.insert(
            tk.END, f"Total Tokens: {len(displayable_tokens)}\n")

    # ── File I/O ──────────────────────────────────────────────

    def save_file(self):
        """Save this tab. Returns True on success, False on cancel/error."""
        if self.filepath:
            return self._write_to_path(self.filepath)
        return self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".kc",
            filetypes=[("KuCode files", "*.kc"), ("All files", "*.*")])
        if not path:
            return False
        if self._write_to_path(path):
            self.filepath = path
            self.mark_clean()
            return True
        return False

    def _write_to_path(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.source_text.get(1.0, tk.END).rstrip('\n'))
            self.mark_clean()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
            return False

    def load_from_path(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open:\n{str(e)}")
            return False
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, content)
        self.filepath = path
        self.update_line_numbers()
        self.mark_clean()
        return True


class KuCodeLexerGUI:
    """Shell: header + ttk.Notebook of EditorTab pages."""

    def __init__(self, root):
        self.root = root
        self.root.title("KuCode Compiler")
        self.root.geometry("1400x800")

        self._untitled_counter = 0
        self._closing = False

        # Style setup (unchanged)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#152238",
                        foreground="#e0e0e0",
                        fieldbackground="#152238",
                        borderwidth=0,
                        rowheight=25,
                        font=("Arial", 10))
        style.configure("Treeview.Heading",
                        background="#1e3a5f",
                        foreground="white",
                        borderwidth=1,
                        relief="flat",
                        font=("Arial Black", 10, "bold"))
        style.map("Treeview.Heading",
                  background=[('active', '#2d5a8a')])
        style.map("Treeview",
                  background=[('selected', '#264f78')],
                  foreground=[('selected', 'white')])
        style.configure("Vertical.TScrollbar",
                        background="#1e3a5f",
                        troughcolor="#0d1b2a",
                        borderwidth=0,
                        arrowcolor="white")
        style.configure("Horizontal.TScrollbar",
                        background="#1e3a5f",
                        troughcolor="#0d1b2a",
                        borderwidth=0,
                        arrowcolor="white")

        bg_color = "#1e3a5f"
        fg_color = "white"

        # Header
        header_frame = tk.Frame(root, bg=bg_color, height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="KuCode Compiler",
                               font=("Courier New", 18, "bold"),
                               bg=bg_color, fg=fg_color)
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        btn_frame = tk.Frame(header_frame, bg=bg_color)
        btn_frame.pack(side=tk.RIGHT, padx=20)

        def mkbtn(text, bg, cmd):
            return tk.Button(btn_frame, text=text, command=cmd,
                             bg=bg, fg="white",
                             font=("Courier New", 10, "bold"),
                             padx=20, pady=5, relief=tk.FLAT, cursor="hand2",
                             activebackground="#3d6a9a")

        mkbtn("Analyze", "#2d5a8a",
              self._cmd_analyze).pack(side=tk.LEFT, padx=5)
        mkbtn("Clear", "#3d6a9f",
              self._cmd_clear).pack(side=tk.LEFT, padx=5)
        mkbtn("Save", "#1d4a7a",
              self._cmd_save).pack(side=tk.LEFT, padx=5)
        mkbtn("Open", "#1d4a7a",
              self._cmd_open).pack(side=tk.LEFT, padx=5)
        mkbtn("Toggle Tokens", "#4a3a6a",
              self._cmd_toggle_tokens).pack(side=tk.LEFT, padx=5)
        # Custom browser-style tab bar
        self._tabs = []
        self._active = None
        self._tab_widgets = {}

        self._tabbar_frame = tk.Frame(root, bg="#0d1b2a", height=36)
        self._tabbar_frame.pack(fill=tk.X, side=tk.TOP)
        self._tabbar_frame.pack_propagate(False)

        self._add_btn = tk.Label(
            self._tabbar_frame, text="+", bg="#0d1b2a", fg="#aaaaaa",
            font=("Courier New", 14, "bold"), padx=10, pady=4, cursor="hand2")
        self._add_btn.pack(side=tk.LEFT, padx=(2, 0))
        self._add_btn.bind("<Button-1>", lambda e: self.new_tab())
        self._add_btn.bind(
            "<Enter>", lambda e: self._add_btn.config(fg="white"))
        self._add_btn.bind(
            "<Leave>", lambda e: self._add_btn.config(fg="#aaaaaa"))

        self._content_frame = tk.Frame(root, bg="#0d1b2a")
        self._content_frame.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Global shortcuts
        root.bind_all('<Control-t>', lambda e: self._cmd_new_tab())
        root.bind_all('<Control-T>', lambda e: self._cmd_new_tab())
        root.bind_all('<Control-w>', lambda e: self._cmd_close_active())
        root.bind_all('<Control-W>', lambda e: self._cmd_close_active())
        root.bind_all('<Control-Tab>', self._on_ctrl_tab_next)
        root.bind_all('<Control-Shift-Tab>', self._on_ctrl_tab_prev)
        try:
            root.bind_all('<Control-ISO_Left_Tab>', self._on_ctrl_tab_prev)
        except Exception:
            pass

        # Intercept window close to flush dirty tabs and kill subprocesses
        root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Start with one blank scratchpad
        self.new_tab()

    # ── Active tab / title ────────────────────────────────────

    def active_tab(self):
        return self._active

    def _refresh_tab_title(self, tab):
        if tab in self._tab_widgets:
            self._tab_widgets[tab]["label"].config(text=tab.title())

    def _build_tab_entry(self, tab):
        _ACTIVE_BG = "#2d5a8a"
        _INACTIVE_BG = "#1e3a5f"
        self._add_btn.pack_forget()

        entry = tk.Frame(self._tabbar_frame, bg=_INACTIVE_BG, cursor="hand2")
        entry.pack(side=tk.LEFT, padx=(2, 0), pady=(4, 0))

        lbl = tk.Label(entry, text=tab.title(), bg=_INACTIVE_BG, fg="#cccccc",
                       font=("Courier New", 10, "bold"), padx=10, pady=6)
        lbl.pack(side=tk.LEFT)

        close = tk.Label(entry, text="×", bg=_INACTIVE_BG, fg="#888888",
                         font=("Courier New", 12, "bold"), padx=6, pady=6, cursor="hand2")
        close.pack(side=tk.LEFT)

        self._tab_widgets[tab] = {"frame": entry, "label": lbl, "close": close}

        self._add_btn.pack(side=tk.LEFT, padx=(2, 0))

        for widget in (entry, lbl):
            widget.bind("<Button-1>", lambda e, t=tab: self._select_tab(t))
        close.bind("<Button-1>", lambda e, t=tab: self.close_tab(t))
        close.bind("<Enter>", lambda e, w=close: w.config(fg="#ff6b6b"))
        close.bind("<Leave>", lambda e, w=close, t=tab: w.config(
            fg="white" if t is self._active else "#888888"))

    def _select_tab(self, tab):
        _ACTIVE_BG = "#2d5a8a"
        _INACTIVE_BG = "#1e3a5f"
        if self._active is not None and self._active is not tab:
            prev = self._tab_widgets.get(self._active)
            if prev:
                prev["frame"].config(bg=_INACTIVE_BG)
                prev["label"].config(bg=_INACTIVE_BG, fg="#cccccc")
                prev["close"].config(bg=_INACTIVE_BG, fg="#888888")
            self._active.pack_forget()
        self._active = tab
        widgets = self._tab_widgets[tab]
        widgets["frame"].config(bg=_ACTIVE_BG)
        widgets["label"].config(bg=_ACTIVE_BG, fg="white")
        widgets["close"].config(bg=_ACTIVE_BG, fg="white")
        tab.pack(fill=tk.BOTH, expand=True)
        tab.source_text.focus_set()

    # ── Tab lifecycle ────────────────────────────────────────

    def new_tab(self, filepath=None):
        tab = EditorTab(self._content_frame, gui=self, filepath=filepath)
        if not filepath:
            self._untitled_counter += 1
            tab.set_untitled_name(f"Untitled {self._untitled_counter}")
        self._tabs.append(tab)
        self._build_tab_entry(tab)
        self._select_tab(tab)
        return tab

    def close_tab(self, tab=None):
        if tab is None:
            tab = self.active_tab()
        if tab is None:
            return False

        if tab.dirty:
            answer = messagebox.askyesnocancel(
                "Save changes?",
                f"Save changes to {tab.title().lstrip('*')}?")
            if answer is None:  # Cancel
                return False
            if answer:  # Yes
                if not tab.save_file():
                    return False

        tab._cleanup_subprocess()

        was_active = (tab is self._active)
        idx = self._tabs.index(tab)
        self._tabs.remove(tab)

        if tab in self._tab_widgets:
            self._tab_widgets[tab]["frame"].destroy()
            del self._tab_widgets[tab]

        if was_active:
            self._active = None
            if self._tabs:
                self._select_tab(self._tabs[max(0, idx - 1)])

        tab.destroy()

        if not self._tabs:
            self.new_tab()
        return True

    def _on_ctrl_tab_next(self, event):
        if not self._tabs:
            return 'break'
        idx = self._tabs.index(self._active)
        self._select_tab(self._tabs[(idx + 1) % len(self._tabs)])
        return 'break'

    def _on_ctrl_tab_prev(self, event):
        if not self._tabs:
            return 'break'
        idx = self._tabs.index(self._active)
        self._select_tab(self._tabs[(idx - 1) % len(self._tabs)])
        return 'break'

    def _on_window_close(self):
        if self._closing:
            return
        self._closing = True
        for tab in list(self._tabs):
            self._select_tab(tab)
            if tab.dirty:
                answer = messagebox.askyesnocancel(
                    "Save changes?",
                    f"Save changes to {tab.title().lstrip('*')}?")
                if answer is None:
                    self._closing = False
                    return
                if answer and not tab.save_file():
                    self._closing = False
                    return
            tab._cleanup_subprocess()
        self.root.destroy()

    # ── Header button handlers ───────────────────────────────

    def _cmd_analyze(self):
        t = self.active_tab()
        if t is not None:
            t.analyze()

    def _cmd_clear(self):
        t = self.active_tab()
        if t is not None:
            t.clear_all()

    def _cmd_save(self):
        t = self.active_tab()
        if t is not None:
            t.save_file()

    def _cmd_open(self):
        path = filedialog.askopenfilename(
            filetypes=[("KuCode files", "*.kc"), ("All files", "*.*")])
        if not path:
            return
        # If the active tab is an empty/untouched scratchpad, reuse it;
        # otherwise open in a new tab.
        t = self.active_tab()
        empty = (t is not None and not t.filepath and not t.dirty and
                 not t.source_text.get(1.0, "end-1c").strip())
        if empty:
            t.load_from_path(path)
            self._refresh_tab_title(t)
        else:
            tab = self.new_tab(filepath=path)
            tab.load_from_path(path)
            self._refresh_tab_title(tab)

    def _cmd_toggle_tokens(self):
        t = self.active_tab()
        if t is not None:
            t.toggle_token_table()

    def _cmd_new_tab(self):
        self.new_tab()

    def _cmd_close_active(self):
        self.close_tab()


# main
if __name__ == "__main__":
    root = tk.Tk()
    app = KuCodeLexerGUI(root)
    root.mainloop()
