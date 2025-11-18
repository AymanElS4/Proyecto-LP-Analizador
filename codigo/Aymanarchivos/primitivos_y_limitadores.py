import ply.lex as lex
import datetime
import os

tokens = [
    'INTEGER',
    'FLOAT',
    'DOUBLE',
    'BOOLEAN',
    'STRING',
    'CHARACTER',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'SEMICOLON', 'COLON',
    'LET',
    'ID',
    'ASSIGN',
    'FOR',
    'IN',
    'LAMBDA_IN',
    'PLUS','MINUS','TIMES','DIVIDE',
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
    'AND','OR','NOT'
]

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
t_LAMBDA_IN = r'->'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EQ        = r'=='
t_NE        = r'!='
t_LE        = r'<='
t_GE        = r'>='
t_LT        = r'<'
t_GT        = r'>'
t_AND       = r'&&'
t_OR        = r'\|\|'
t_NOT       = r'!'

# helpers / reserved
reserved = {
    'let': 'LET',
    'for': 'FOR',
    'in': 'IN',
    'true': 'BOOLEAN',
    'false': 'BOOLEAN',
    
}

# ID rule (and reserved words)
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    # check reserved
    if t.value in reserved:
        t.type = reserved[t.value]
        if t.type == 'BOOLEAN':
            t.value = True if t.value == 'true' else False
    return t

#para la sintaxis
def t_PRINT(t):
    r'print'
    t.type = 'ID'
    t.value = 'print'
    return t

def t_READLINE(t):
    r'readLine'
    t.type = 'ID'
    t.value = 'readLine'
    return t

def t_INPUT(t):
    r'input'
    t.type = 'ID'
    t.value = 'input'
    return t

#tipos de numeros
def t_DOUBLE(t):
    r'\d+(\.\d+)?[eE][+-]?\d+'
    try:
        t.value = float(t.value)
    except:
        t.value = 0.0
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
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

def t_BOOLEAN(t):
    r'(true|false)'
    t.value = True if t.value == 'true' else False
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

# newline tracking
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# error handling
def t_error(t):
    print(f"[LEX ERROR] Caracter ilegal: '{t.value[0]}' en linea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
def test_lexer_from_file(filepath, usuario_git="default"):
    

    # Leer archivo .swift
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {filepath}")
        return

    lexer.input(input_text)

    fecha_hora = datetime.datetime.now().strftime("%d-%m-%Y-%Hh%M")#fecha y hora
    log_name = "Proyecto-LP-Analizador\logs\lexico-" + usuario_git + "-" + fecha_hora + ".txt"

    with open(log_name, "w", encoding="utf-8") as log:
        log.write(f"LOG DE TOKENS ({fecha_hora}) \n")
        while True:
            tok = lexer.token()
            if not tok:
                break
            log.write(f"Línea {tok.lineno}: {tok.type} -> {tok.value}\n")

    print(f"\nAnalisis lexico completado. Log guardado en: {log_name}")


#ejemplo tipos primitivos y limitadores
if __name__ == "__main__":
    ruta_swift = r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift"
    test_lexer_from_file(ruta_swift, usuario_git="AymanElS4")
    
