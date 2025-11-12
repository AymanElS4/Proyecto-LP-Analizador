# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# List of token names.   This is always required
reserved = {
    "if" : "IF",
    "else" : "ELSE",
    "while" : "WHILE",
    "for" : "FOR",
    "else if" : "ELSEIF",
    "return" : "RETURN",

}
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'DOLLAR',
   'ARROBA',
   'VARIABLE',
    'IGUAL',
    'DOUBLEEQUAL',
    'PERCENT',
    'CUADRO',

) + tuple(reserved.values())

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_DOLLAR = r'\$'
t_ARROBA = r'@'
t_IGUAL =  r'='
t_VARIABLE = r'_?var?|\s|[a-zA-Z]+\s*\s*([\w*|\d*]+)?'
t_DOUBLEEQUAL = r'=='
t_PERCENT = r'%'
t_CUADRO = r'\#'

# A regular expression rule with some action code


def t_FLOAT(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t



def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("El caracter no es reconocido en este lenguaje '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Test it out
data = '''
3 + 4 * 10 $
  + -20 *2 % #
var myVariable = 42
myVariable = 50
  
'''
"""
var myVariable = 42
    myVariable = 50
"""

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)
