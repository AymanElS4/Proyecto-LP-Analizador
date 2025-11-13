import ply.lex as lex
import os
from datetime import datetime

reserved = {
    'class': 'CLASS',
    'deinit': 'DEINIT',
    'enum': 'ENUM',
    'extension': 'EXTENSION',
    'func': 'FUNC',
    'import': 'IMPORT',
    'init': 'INIT',
    'inout': 'INOUT',
    'let': 'LET',
    'operator': 'OPERATOR',
    'protocol': 'PROTOCOL',
    'struct': 'STRUCT',
    'subscript': 'SUBSCRIPT',
    'typealias': 'TYPEALIAS',
    'var': 'VAR',
    'break': 'BREAK',
    'case': 'CASE',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'defer': 'DEFER',
    'do': 'DO',
    'else': 'ELSE',
    'fallthrough': 'FALLTHROUGH',
    'for': 'FOR',
    'guard': 'GUARD',
    'if': 'IF',
    'in': 'IN',
    'repeat': 'REPEAT',
    'return': 'RETURN',
    'switch': 'SWITCH',
    'where': 'WHERE',
    'while': 'WHILE',
    'as': 'AS',
    'Any': 'ANY',
    'catch': 'CATCH',
    'false': 'FALSE',
    'is': 'IS',
    'nil': 'NIL',
    'rethrows': 'RETHROWS',
    'super': 'SUPER',
    'self': 'SELF',
    'Self': 'SELF_TYPE',
    'throw': 'THROW',
    'throws': 'THROWS',
    'true': 'TRUE',
    'try': 'TRY',
    '__COLUMN__': 'COLUMN',
    '__FILE__': 'FILE',
    '__FUNCTION__': 'FUNCTION',
    '__LINE__': 'LINE'
}

tokens = [
    'ID',
    'NUMBER',
    'STRING',
    'COMMENT_SINGLE',
    'COMMENT_MULTI'
] + list(reserved.values())


t_ignore = ' \t'

def t_COMMENT_SINGLE(t):
    r'//.*'
    t.value = t.value.strip()
    return t

def t_COMMENT_MULTI(t):
    r'/\*[\s\S]*?\*/'
    t.value = t.value.strip()
    return t

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
        t.is_reserved = True  
    else:
        t.is_reserved = False
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

def analizar_archivo(nombre_archivo, usuario_git="usuario"):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        data = f.read()

    lexer.input(data)

    if not os.path.exists("logs"):
        os.makedirs("logs")

    fecha_hora = datetime.now().strftime("%d-%m-%Y-%Hh%M")
    log_name = f"logs/lexico-{usuario_git}-{fecha_hora}.txt"

    with open(log_name, 'w', encoding='utf-8') as log:
        while True:
            tok = lexer.token()
            if not tok:
                break
            if hasattr(tok, 'is_reserved') and tok.is_reserved:
                log.write(f"Línea {tok.lineno}: Tipo=PALABRA_RESERVADA, Valor={tok.value}\n")
            else:
                log.write(f"Línea {tok.lineno}: Tipo={tok.type}, Valor={tok.value}\n")

    print(f" Análisis completado. Log generado en: {log_name}")

if __name__ == "__main__":
    analizar_archivo("algoritmos/algoritmo_comentarios_y_palabrasReservadas.swift", usuario_git="jorssanc")
