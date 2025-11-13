import ply.lex as lex
import datetime
import os
#tokens

tokens = [
    'INTEGER',
    'FLOAT',
    'BOOLEAN',
    'STRING',
    'CHARACTER',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'SEMICOLON', 'COLON'
]

#Expresiones regulares en tokens
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_COMMA     = r','
t_SEMICOLON = r';'
t_COLON     = r':'
#Tipos primitivos
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_BOOLEAN(t):
    r'(true|false)'
    t.value = True if t.value == 'true' else False
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = str(t.value)
    return t

def t_CHARACTER(t):
    r'\'([^\\\n]|(\\.))\''
    t.value = t.value[1:-1]  # eliminar comillas simples
    return t


# Ignorar espacios y tabulaciones
t_ignore = ' \t'


#manejo de errores

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"[ERROR] Carácter ilegal: '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

def test_lexer_from_file(filepath, usuario_git="default"):
    # Crear lexer
    lexer = lex.lex()

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
        log.write(f"===== LOG DE TOKENS ({fecha_hora}) =====\n")
        while True:
            tok = lexer.token()
            if not tok:
                break
            log.write(f"Línea {tok.lineno}: {tok.type} -> {tok.value}\n")

    print(f"\nAnálisis léxico completado. Log guardado en: {log_name}")


#ejemplo tipos primitivos y limitadores
if __name__ == "__main__":
    ruta_swift = r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift"
    test_lexer_from_file(ruta_swift, usuario_git="AymanElS4")
    
