import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import string
import re

NUM = '0123456789'
LETTERS = string.ascii_letters
LETTERNUM = NUM + LETTERS
WHITESPACE = '\n\t '

# RESERVED WORDS - FROM OUR PAPER
keywords = {
    'start', 'finish', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool',
    'Yes', 'No', 'none', 'empty', 'read', 'show', 'check', 'otherwise', 'otherwisecheck',
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
OP_MODULUS = '%'
OP_EXPONENTIATION = '**'
OP_EXPONENTIATION_ASSIGN = '**='

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
    'space_semcol': {' ', ';'},
    'space': {' '},
    # space, newline
    'space_nline': {' ', '\n', '{', },
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
    'comma_delim': {' ', '(', '"', "'", '{', '['} | set(LETTERNUM),
    # space, num, ", ', [, ]
    'open_list': {' ', '"', "'", '[', ']'} | set(LETTERNUM),
    # space, ;, ,, =
    'close_list': {' ', ';', ',', '=', ']', '[', '+', '-', '*', '/', '%', '&', '|', '!', '<', '>', ')'},
    # space, letternum, ', ", (, ), !
    'openparen_delim': {' ', "'", '"', '(', ')', '!', '-'} | set(LETTERNUM),
    # space, mathop, logicop, relop, ;, {, )
    'closeparen_delim': {' ', '+', '-', '*', '/', '%', '&', '|', '!', '=', '<', '>', ';', '{', ')'},
    # space, &, |, !, ;
    'bool_delim': {' ', '&', '|', '!', ';', ')', ':'},
    # space_nline, ,, +, ), ], }, ;
    'string_char': {' ', '\n', ',', '+', ')', ']', '}', ';', ':'},
    # space_nline, null, }, ], ), ,, ;, mathop, relop, logicop, =
    'lit_delim': {' ', '\n', '}', ']', ')', ',', ';', '+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', ':'},
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
    RW_NONE: 'sem_col',
    RW_NO: 'bool_delim',
    RW_OPTION: 'space',
    RW_OTHERWISE: 'delim1',
    RW_OTHERWISECHECK: 'delim2',
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
        LIT_NUMBER: 'NUM_LIT',
        LIT_DECIMAL: 'DECIMAL_LIT',
        LIT_STRING: 'STRING_LIT',
        LIT_CHARACTER: 'CHAR_LIT',
        IDENTIFIER: 'IDENTIFIER',
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
            's': 1, 'f': 51, 'n': 92, 'd': 22, 'b': 180,
            'l': 85, 't': 156, 'w': 163, 'Y': 173, 'e': 41,
            'r': 125, 'c': 16, 'o': 103, 'g': 80, 'N': 100
        }

        # "start", "select", "show", "skip", "step", "stop"
        trans[1] = {'t': 2, 'h': 137, 'k': 141, 'e': 130}
        # 'a' for start, 'o' for stop, 'e' for step
        trans[2] = {'a': 3, 'o': 153, 'e': 150}
        trans[3] = {'r': 4}
        trans[4] = {'t': 5}
        trans[5] = {}  # accept: start

        trans[130] = {'l': 131}
        trans[131] = {'e': 132}
        trans[132] = {'c': 133}
        trans[133] = {'t': 134}
        trans[134] = {}  # accept: select

        trans[137] = {'o': 138}
        trans[138] = {'w': 139}
        trans[139] = {}  # accept: show

        trans[141] = {'i': 142}
        trans[142] = {'p': 143}
        trans[143] = {}  # accept: skip

        trans[150] = {'p': 151}
        trans[151] = {}  # accept: step

        trans[153] = {'p': 154}
        trans[154] = {}  # accept: stop

        # "text", "to"
        trans[156] = {'e': 157, 'o': 161}
        trans[157] = {'x': 158}
        trans[158] = {'t': 159}
        trans[159] = {}  # accept: text
        trans[161] = {}  # accept: to

        # "worldwide"
        trans[163] = {'o': 164}
        trans[164] = {'r': 165}
        trans[165] = {'l': 166}
        trans[166] = {'d': 167}
        trans[167] = {'w': 168}
        trans[168] = {'i': 169}
        trans[169] = {'d': 170}
        trans[170] = {'e': 171}
        trans[171] = {}  # accept: worldwide

        # "Yes"
        trans[173] = {'e': 174}
        trans[174] = {'s': 175}
        trans[175] = {}  # accept: Yes

        # "check"
        trans[16] = {'h': 17}
        trans[17] = {'e': 18}
        trans[18] = {'c': 19}
        trans[19] = {'k': 20}
        trans[20] = {}  # accept: check

        # "decimal", "define", "during"
        trans[22] = {'e': 23, 'u': 35}
        trans[23] = {'c': 24, 'f': 30}
        trans[24] = {'i': 25}
        trans[25] = {'m': 26}
        trans[26] = {'a': 27}
        trans[27] = {'l': 28}
        trans[28] = {}  # accept: decimal

        trans[30] = {'i': 31}
        trans[31] = {'n': 32}
        trans[32] = {'e': 33}
        trans[33] = {}  # accept: define

        trans[35] = {'r': 36}
        trans[36] = {'i': 37}
        trans[37] = {'n': 38}
        trans[38] = {'g': 39}
        trans[39] = {}  # accept: during

        # "each", "empty"
        trans[41] = {'a': 42, 'm': 46}
        trans[42] = {'c': 43}
        trans[43] = {'h': 44}
        trans[44] = {}  # accept: each

        trans[46] = {'p': 47}
        trans[47] = {'t': 48}
        trans[48] = {'y': 49}
        trans[49] = {}  # accept: empty

        # "finish", "fixed", "from", "fallback"
        trans[51] = {'i': 60, 'a': 52, 'r': 66}

        trans[52] = {'l': 53}
        trans[53] = {'l': 54}
        trans[54] = {'b': 55}
        trans[55] = {'a': 56}
        trans[56] = {'c': 57}
        trans[57] = {'k': 58}
        trans[58] = {}  # accept: fallback

        trans[60] = {'n': 61, 'x': 71}
        trans[61] = {'i': 62}
        trans[62] = {'s': 63}
        trans[63] = {'h': 64}
        trans[64] = {}  # accept: finish

        trans[66] = {'o': 67}
        trans[67] = {'m': 68}
        trans[68] = {}  # accept: from

        trans[71] = {'e': 72}
        trans[72] = {'d': 73}
        trans[73] = {}  # accept: fixed

        trans[80] = {'r': 81, 'i': 76}  # ADD 'i': 76 for "give"
        trans[76] = {'v': 77}
        trans[77] = {'e': 78}
        trans[78] = {}  # accept: give

        trans[81] = {'o': 82}
        trans[82] = {'u': 83}
        trans[83] = {'p': 84}
        trans[84] = {}  # accept: group

        # "letter", "list"
        trans[85] = {'e': 86, 'i': 176}
        trans[86] = {'t': 87}
        trans[87] = {'t': 88}
        trans[88] = {'e': 89}
        trans[89] = {'r': 90}
        trans[90] = {}  # accept: letter

        trans[176] = {'s': 177}
        trans[177] = {'t': 178}
        trans[178] = {}  # accept: list

        # "num", "none", "No"
        trans[92] = {'u': 93, 'o': 96}
        trans[93] = {'m': 94}
        trans[94] = {}  # accept: num

        trans[96] = {'n': 97}
        trans[97] = {'e': 98}
        trans[98] = {}  # accept: none

        trans[100] = {'o': 101}
        trans[101] = {}  # accept: No

        # "option", "otherwise"
        trans[103] = {'p': 104, 't': 110}
        trans[104] = {'t': 105}
        trans[105] = {'i': 106}
        trans[106] = {'o': 107}
        trans[107] = {'n': 108}
        trans[108] = {}  # accept: option

        trans[110] = {'h': 111}
        trans[111] = {'e': 112}
        trans[112] = {'r': 113}
        trans[113] = {'w': 114}
        trans[114] = {'i': 115}
        trans[115] = {'s': 116}
        trans[116] = {'e': 117}
        trans[117] = {'c': 200}  # - continue to 'c'
        trans[200] = {'h': 201}  # - continue to 'h'
        trans[201] = {'e': 202}  # - continue to 'e'
        trans[202] = {'c': 203}  # - continue to 'c'
        trans[203] = {'k': 204}  # - continue to 'k'
        trans[204] = {}  # accept: otherwisecheck

        # "read"
        trans[125] = {'e': 126}
        trans[126] = {'a': 127}
        trans[127] = {'d': 128}
        trans[128] = {}  # accept: read

        # "bool", "bigdecimal"
        trans[180] = {'o': 181, 'i': 184}
        trans[181] = {'o': 182}
        trans[182] = {'l': 183}
        trans[183] = {}  # accept: bool

        trans[184] = {'g': 185}
        trans[185] = {'d': 186}
        trans[186] = {'e': 187}
        trans[187] = {'c': 188}
        trans[188] = {'i': 189}
        trans[189] = {'m': 190}
        trans[190] = {'a': 191}
        trans[191] = {'l': 192}
        trans[192] = {}  # accept: bigdecimal

        return trans

    def _build_accept_states(self):
        """Map accept states to token types"""
        return {
            5: RW_START,
            20: RW_CHECK,
            28: RW_DECIMAL,
            33: RW_DEFINE,
            39: RW_DURING,
            44: RW_EACH,
            49: RW_EMPTY,
            58: RW_FALLBACK,
            64: RW_FINISH,
            68: RW_FROM,
            73: RW_FIXED,
            78: RW_GIVE,
            84: RW_GROUP,
            90: RW_LETTER,
            94: RW_NUM,
            98: RW_NONE,
            101: RW_NO,
            108: RW_OPTION,
            117: RW_OTHERWISE,
            204: RW_OTHERWISECHECK,
            128: RW_READ,
            134: RW_SELECT,
            139: RW_SHOW,
            143: RW_SKIP,
            154: RW_STOP,
            151: RW_STEP,
            159: RW_TEXT,
            161: RW_TO,
            171: RW_WORLDWIDE,
            175: RW_YES,
            178: RW_LIST,
            183: RW_BOOL,
            192: RW_BIGDECIMAL,
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
        skip_check = [NEWLINE, WHITESPACE_SPACE,
                      WHITESPACE_TAB, EOF, COMMENT_SINGLE, COMMENT_MULTI]
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
            eof_allowed_types = []

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
            # Build friendly error message
            delim_names = {
                'space': 'space',
                'space_nline': 'space or newline',
                'delim1': 'space or "{"',
                'delim2': 'space or "("',
                'delim3': 'delim3',
                'sem_col': '";"',
                'op_delim': 'op_delim',
                'open_paren': '"("',
                'comma_delim': 'space, letter, digit, "(", """, "{", "[", or "\'"',
                'open_list': 'space, digit, """, "\'", "[" or "]"',
                'close_list': 'space, ";", "," or "="',
                'openparen_delim': 'space, letter, digit, "\'", """, ")" or "!"',
                'closeparen_delim': 'space, operator, ";", "{" or ")"',
                'bool_delim': 'space, "&", "|", "!" or ";"',
                'string_char': 'space, newline, ",", "+", ")", "]", "}" or ";"',
                'lit_delim': 'lit_delim',
                'identifier_del': 'space, newline, operator, or punctuation',
                'num': 'digit',
                'id3': 'space or digit',
                'delim7': 'delim3',
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

                # Check if this is a negative number (unary minus)
                if self.current_char and self.current_char != ' ' and (self.current_char in NUM or (self.current_char == '.' and self.peek() and self.peek() in NUM)):
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

                if self.current_char == '=':
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


class KuCodeLexerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KuCode Lexical & Syntax Analyzer")
        self.root.geometry("1400x800")

        # Configure style
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
                  background=[('active', '#2d5a8a')])  # Lighter blue on hover

        style.map("Treeview",
                  background=[('selected', '#264f78')],  # Selection color
                  foreground=[('selected', 'white')])

        # Configure colors
        bg_color = "#1e3a5f"
        fg_color = "white"
        accent_blue = "#2d5a8a"
        dark_blue = "#152238"
        panel_bg = "#1a1a2e"

        # Header Frame
        header_frame = tk.Frame(root, bg=bg_color, height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # Logo and Title
        title_label = tk.Label(header_frame, text="KuCode Lexical & Syntax Analyzer",
                               font=("Courier New", 18, "bold"), bg=bg_color, fg=fg_color)
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Buttons
        btn_frame = tk.Frame(header_frame, bg=bg_color)
        btn_frame.pack(side=tk.RIGHT, padx=20)

        analyze_btn = tk.Button(btn_frame, text="Analyze", command=self.analyze,
                                bg="#2d5a8a", fg="white", font=("Courier New", 10, "bold"),
                                padx=20, pady=5, relief=tk.FLAT, cursor="hand2",
                                activebackground="#3d6a9a")
        analyze_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_all,
                              bg="#3d6a9f", fg="white", font=("Courier New", 10, "bold"),
                              padx=20, pady=5, relief=tk.FLAT, cursor="hand2",
                              activebackground="#4d7aaf")
        clear_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(btn_frame, text="Save", command=self.save_results,
                             bg="#1d4a7a", fg="white", font=("Courier New", 10, "bold"),
                             padx=20, pady=5, relief=tk.FLAT, cursor="hand2",
                             activebackground="#2d5a8a")
        save_btn.pack(side=tk.LEFT, padx=5)

        # Main container
        # Container for everything below header (for PanedWindow)
        content_container = tk.Frame(root, bg="#0d1b2a")
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create PanedWindow for draggable divider
        paned_window = tk.PanedWindow(content_container, orient=tk.VERTICAL,
                                      bg="#0d1b2a", sashwidth=8,
                                      sashrelief=tk.RAISED, bd=0)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Main container (source code + tokens)
        main_container = tk.Frame(paned_window, bg="#0d1b2a")
        paned_window.add(main_container, minsize=200)

        # Left Panel - Source Code
        left_panel = tk.Frame(main_container, bg=panel_bg,
                              relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        source_label = tk.Label(left_panel, text="Source Code",
                                font=("Courier New", 12, "bold"), bg=panel_bg, fg="white", anchor="w")
        source_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        # Line numbers frame
        line_frame = tk.Frame(left_panel, bg="white")
        line_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Line numbers
        self.line_numbers = tk.Text(line_frame, width=4, padx=5, takefocus=0,
                                    border=0, background='#0d1b2a', fg='#6c757d',
                                    state='disabled', wrap='none', font=("Courier New", 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

# Source code text area
        self.source_text = scrolledtext.ScrolledText(line_frame, wrap=tk.NONE,
                                                     font=("Courier New", 10),
                                                     bg=dark_blue, fg="#e0e0e0",
                                                     insertbackground="white",
                                                     selectbackground="#264f78")
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.source_text.bind('<KeyRelease>', self.update_line_numbers)
        self.source_text.bind('<MouseWheel>', self.sync_scroll)

        # Right Panel - Tokens
        right_panel = tk.Frame(
            main_container, bg=panel_bg, relief=tk.RAISED, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tokens_label = tk.Label(right_panel, text="Lexical Table",
                                font=("Courier New", 12, "bold"), bg=panel_bg, fg="white", anchor="w")
        tokens_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Tokens table
        table_frame = tk.Frame(right_panel)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars

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

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        self.token_table = ttk.Treeview(table_frame,
                                        columns=("Lexeme", "Token"),
                                        show="headings",
                                        yscrollcommand=vsb.set,
                                        xscrollcommand=hsb.set,
                                        style="Treeview")

        vsb.config(command=self.token_table.yview)
        hsb.config(command=self.token_table.xview)

        # Configure columns
        self.token_table.heading("Lexeme", text="LEXEME", anchor="center")
        self.token_table.heading("Token", text="TOKEN", anchor="center")

        self.token_table.column("Lexeme", width=250, anchor="center")
        self.token_table.column("Token", width=250, anchor="center")

        self.token_table.pack(fill=tk.BOTH, expand=True)

        # Bottom Panel - Terminal (resizable)
        # Bottom Panel - Terminal (in PanedWindow for draggable resize)
        terminal_frame = tk.Frame(
            paned_window, bg=panel_bg, relief=tk.RAISED, bd=1)
        paned_window.add(terminal_frame, minsize=100)

        terminal_label = tk.Label(terminal_frame, text="Terminal",
                                  font=("Courier New", 12, "bold"), bg=panel_bg, fg="white", anchor="w")
        terminal_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.terminal_text = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD,
                                                       font=("Courier New", 9),
                                                       bg=dark_blue, fg="#00ff00",
                                                       height=6)
        self.terminal_text.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def highlight_syntax(self, event=None):

        self.source_text.tag_remove("keyword", "1.0", "end")
        self.source_text.tag_remove("string", "1.0", "end")
        self.source_text.tag_remove("comment", "1.0", "end")
        self.source_text.tag_remove("number", "1.0", "end")
        self.source_text.tag_remove("operator", "1.0", "end")

        content = self.source_text.get("1.0", "end-1c")

    # Keywords - purple/pink
        keywords_pattern = r'\b(' + '|'.join([
            'start', 'finish', 'num', 'decimal', 'bigdecimal', 'letter', 'text', 'bool',
            'Yes', 'No', 'none', 'empty', 'read', 'show', 'check', 'otherwise', 'otherwisecheck',
            'fallback', 'select', 'option', 'each', 'during', 'from', 'to', 'step',
            'stop', 'skip', 'give', 'define', 'worldwide', 'fixed', 'list', 'group'
        ]) + r')\b'

        import re
        for match in re.finditer(keywords_pattern, content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("keyword", start_idx, end_idx)

    # Strings - green
        string_pattern = r'"[^"]*"|\'[^\']*\''
        for match in re.finditer(string_pattern, content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("string", start_idx, end_idx)

    # Comments - gray
        comment_pattern = r'~[^\n]*|~~.*?~~'
        for match in re.finditer(comment_pattern, content, re.DOTALL):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("comment", start_idx, end_idx)

    # Numbers - orange
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("number", start_idx, end_idx)

    # Operators - light blue
        operator_pattern = r'[+\-*/%=<>!&|]+'
        for match in re.finditer(operator_pattern, content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.source_text.tag_add("operator", start_idx, end_idx)

    # Configure tag colors
        self.source_text.tag_config("keyword", foreground="#c678dd")  # Purple
        self.source_text.tag_config("string", foreground="#98c379")   # Green
        self.source_text.tag_config("comment", foreground="#5c6370")  # Gray
        self.source_text.tag_config("number", foreground="#d19a66")   # Orange
        self.source_text.tag_config(
            "operator", foreground="#61afef")  # Light blue

    def update_line_numbers(self, event=None):
        line_count = self.source_text.get("1.0", "end-1c").count('\n') + 1
        line_numbers_string = "\n".join(str(i)
                                        for i in range(1, line_count + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state='disabled')

        self.highlight_syntax()

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

        source = self.source_text.get(1.0, "end-1c")

        if not source.strip():
            self.terminal_text.insert(
                tk.END, "Error: No source code to analyze\n")
            return

        # LEXICAL ANALYSIS
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        # Display tokens in table
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
                self.token_table.insert(
                    "", tk.END, values=(lexeme, display_type))

        # Check for lexical errors
        if errors:
            self.terminal_text.insert(
                tk.END, "✗ Lexical analysis failed:\n\n", "error")
            for error in errors:
                self.terminal_text.insert(tk.END, str(error) + "\n", "error")
            self.terminal_text.tag_config("error", foreground="#ff6b6b")
            return  # Stop here if lexical errors exist

        # SYNTAX ANALYSIS (only if no lexical errors)
        self.terminal_text.insert(
            tk.END, "✓ Lexical analysis passed.\n", "success")
        self.terminal_text.insert(
            tk.END, "\nStarting syntax analysis...\n\n", "info")

        # Prepare tokens for parser
        parser_tokens = prepare_tokens_for_parser(tokens)

        # Import and run parser
        from syntaxtest import Parser
        parser = Parser(parser_tokens)

        try:
            result = parser.parse()
            self.terminal_text.insert(
                tk.END, "✓ Syntax analysis passed.\n", "success")
            self.terminal_text.insert(
                tk.END, f"\nResult: {result}\n", "success")
        except SyntaxError as e:
            self.terminal_text.insert(
                tk.END, "✗ Syntax analysis failed:\n\n", "error")
            self.terminal_text.insert(tk.END, str(e) + "\n", "error")

        # Configure tags
        self.terminal_text.tag_config("error", foreground="#ff6b6b")
        self.terminal_text.tag_config("success", foreground="#00ff00")
        self.terminal_text.tag_config("info", foreground="#61afef")

        # Display statistics
        displayable_tokens = [t for t in tokens if t.type not in [EOF]]
        self.terminal_text.insert(tk.END, f"\n{'='*50}\n")
        self.terminal_text.insert(
            tk.END, f"Total Tokens: {len(displayable_tokens)}\n")
        self.terminal_text.insert(tk.END, f"Lexical Errors: {len(errors)}\n")

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


# main
if __name__ == "__main__":
    root = tk.Tk()
    app = KuCodeLexerGUI(root)
    root.mainloop()
