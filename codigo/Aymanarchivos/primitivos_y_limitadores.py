import ply.lex as lex
import datetime
import os

# helpers / reserved
reserved = {
    'let': 'LET',
    'for': 'FOR',
    'in': 'IN',
    'true': 'BOOLEAN',
    'false': 'BOOLEAN',
    'print': 'PRINT',
    'readLine': 'READLINE',
    
}

tokens = [
    'INTEGER',
    'FLOAT',
    'DOUBLE',
    'STRING',
    'CHARACTER',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'SEMICOLON', 'COLON',
    'ID',
    'ASSIGN',
    'DOTDOTDOT',  
    'ARROW',
    'PLUS','MINUS','TIMES','DIVIDE', 'MOD',
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
    'AND','OR','NOT'
] + list(reserved.values())

# Single-char tokens as regex
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_COMMA     = r','
t_SEMICOLON = r';'
t_COLON     = r':'
t_ASSIGN    = r'='
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_MOD       = r'%'
t_EQ        = r'=='
t_NE        = r'!='
t_LE        = r'<='
t_GE        = r'>='
t_LT        = r'<'
t_GT        = r'>'
t_AND       = r'&&'
t_OR        = r'\|\|'
t_NOT       = r'!'
t_DOTDOTDOT     = r'\.\.\.'   # Swift 0...5
t_ARROW     = r'->' 

# ID rule (and reserved words)
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
        if t.type == 'BOOLEAN':
            t.value = (t.value == 'true')
    return t


#tipos de numeros


def t_FLOAT(t):
    r'\d+(\.\d+)?[eE][+-]?\d+'
    try:
        t.value = float(t.value)
    except:
        t.value = 0.0
    return t

def t_INTEGER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except:
        t.value = 0
    return t


# STRING and CHARACTER
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value
    return t

def t_CHARACTER(t):
    r'\'([^\\\n]|(\\.))\''
    # store inner char
    t.value = t.value[1:-1]
    return t

# ignore spaces and tabs
t_ignore = ' \t'

# newline 
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# error handling
def t_error(t):
    print(f"[LEX ERROR] Caracter ilegal: '{t.value[0]}' en linea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()


