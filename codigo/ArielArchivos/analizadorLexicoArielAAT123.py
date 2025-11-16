import ply.lex as lex
from typing import List

# =========================================================================
# 1. ANALIZADOR LÉXICO (PLY Lex) - Definición de Tokens
# =========================================================================

# Palabras reservadas requeridas
reservadas = {
    'var': 'VAR', 'let': 'LET', 'func': 'FUNC', 'while': 'WHILE', 'if': 'IF',
    'else': 'ELSE', 'true': 'TRUE', 'false': 'FALSE',
    'return': 'RETURN', 'class': 'CLASS',
    'self': 'SELF', 'init': 'INIT',
}

# Lista principal de tokens
tokens = [
    'IDENTIFICADOR', 'ENTERO', 'DECIMAL', 'CADENA',
    'LPAREN','RPAREN','LBRACE','RBRACE','LBRACKET','RBRACKET',
    'COMA','DOSPTOS','PUNTOYCOMA','ASIGNAR','PUNTO',
    'SUMA','RESTA','MULT','DIV','MOD',
    'AND','OR','NOT',
    'IGUAL','DIFERENTE','MENOR','MAYOR','MENORIGUAL','MAYORIGUAL',
    'FLECHA'
] + list(reservadas.values())

# Definiciones de tokens simples
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'%'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MENOR = r'<'
t_MAYOR = r'>'
t_MENORIGUAL = r'<='
t_MAYORIGUAL = r'>='
t_ASIGNAR = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMA = r','
t_DOSPTOS = r':'
t_PUNTOYCOMA = r';'
t_FLECHA = r'->'
t_PUNTO = r'\.'
t_ignore = ' \t'

# Listas para almacenar resultados globales
errores_lexicos: List[str] = []
tokens_reconocidos: List[lex.LexToken] = [] 

# Definiciones de tokens complejos
def t_DECIMAL(t):
    r'([0-9]+\.[0-9]+)'
    t.value = float(t.value)
    tokens_reconocidos.append(t)
    return t

def t_ENTERO(t):
    r'([0-9]+)'
    t.value = int(t.value)
    tokens_reconocidos.append(t)
    return t

def t_CADENA(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
    tokens_reconocidos.append(t)
    return t

def t_IDENTIFICADOR(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    tokens_reconocidos.append(t)
    return t

def t_comentario_multilinea(t):
    r'/\*([^*]|\*+[^*/])*\*+/'
    t.lexer.lineno += t.value.count('\n') 
    pass

def t_comentario_linea(t):
    r'//.*'
    pass

def t_nueva_linea(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    errores_lexicos.append(f"❌ Error léxico: carácter no reconocido '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# Inicialización del analizador léxico
analizador_lexico = lex.lex()

# Exportamos los tokens para ser usados por PLY Yacc en el otro archivo
# Usamos 'tokens' (la lista de nombres de tokens) directamente.