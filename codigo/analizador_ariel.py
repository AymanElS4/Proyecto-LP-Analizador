# analizador_ariel.py
# Analizador léxico, sintáctico y semántico realizado por Ariel Arias Tipán
# Ahora guarda en logs tanto los errores como los elementos reconocidos correctamente.

from __future__ import annotations
import ply.lex as lex
import ply.yacc as yacc
from typing import Any, Dict, List, Optional, Tuple
import os
from datetime import datetime
import sys

# Forzar UTF-8 para impresión
sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------
# ANALIZADOR LÉXICO
# -----------------------------
reservadas = {
    'var': 'VAR',
    'func': 'FUNC',
    'while': 'WHILE',
    'true': 'TRUE',
    'false': 'FALSE',
    'return': 'RETURN',
}

tokens = [
    'IDENTIFICADOR', 'ENTERO', 'DECIMAL', 'CADENA',
    'LPAREN','RPAREN','LBRACE','RBRACE','LBRACKET','RBRACKET',
    'COMA','DOSPTOS','PUNTOYCOMA','ASIGNAR',
    'SUMA','RESTA','MULT','DIV','MOD',
    'AND','OR','NOT',
    'IGUAL','DIFERENTE','MENOR','MAYOR','MENORIGUAL','MAYORIGUAL',
    'FLECHA'
] + list(reservadas.values())

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
t_ignore = ' \t'

tokens_reconocidos = []
errores_lexicos = []
errores_sintacticos = []

def t_DECIMAL(t):
    r'([0-9]+\.[0-9]+)'
    t.value = float(t.value)
    tokens_reconocidos.append(f"Línea {t.lineno}: Decimal -> {t.value}")
    return t

def t_ENTERO(t):
    r'([0-9]+)'
    t.value = int(t.value)
    tokens_reconocidos.append(f"Línea {t.lineno}: Entero -> {t.value}")
    return t

def t_CADENA(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
    tokens_reconocidos.append(f"Línea {t.lineno}: Cadena -> \"{t.value}\"")
    return t

def t_IDENTIFICADOR(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    tokens_reconocidos.append(f"Línea {t.lineno}: {t.type} -> {t.value}")
    return t

def t_comentario_multilinea(t):
    r'/\*([^*]|\*+[^*/])*\*+/'
    pass

def t_comentario_linea(t):
    r'//.*'
    pass

def t_nueva_linea(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    errores_lexicos.append(f"Error léxico: carácter no reconocido '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

analizador_lexico = lex.lex()

# -----------------------------
# NODOS DEL ÁRBOL
# -----------------------------
class Nodo: 
    def __init__(self, linea: int): self.linea = linea
class Programa(Nodo): 
    def __init__(self, sentencias): super().__init__(1); self.sentencias = sentencias
class DeclaracionVariable(Nodo):
    def __init__(self, nombre, tipo, valor, linea): super().__init__(linea); self.nombre, self.tipo, self.valor = nombre, tipo, valor
class Asignacion(Nodo):
    def __init__(self, nombre, expresion, linea): super().__init__(linea); self.nombre, self.expresion = nombre, expresion
class Mientras(Nodo):
    def __init__(self, condicion, cuerpo, linea): super().__init__(linea); self.condicion, self.cuerpo = condicion, cuerpo
class OperacionBinaria(Nodo):
    def __init__(self, op, izq, der, linea): super().__init__(linea); self.operador, self.izquierda, self.derecha = op, izq, der
class OperacionUnaria(Nodo):
    def __init__(self, op, opnd, linea): super().__init__(linea); self.operador, self.operando = op, opnd
class Literal(Nodo):
    def __init__(self, valor, tipo, linea): super().__init__(linea); self.valor, self.tipo = valor, tipo
class Identificador(Nodo):
    def __init__(self, nombre, linea): super().__init__(linea); self.nombre = nombre

# -----------------------------
# ANALIZADOR SINTÁCTICO
# -----------------------------
precedence = (
    ('left', 'OR'), 
    ('left', 'AND'),
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENOR', 'MENORIGUAL', 'MAYOR', 'MAYORIGUAL'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('right', 'NOT'),
)

def p_programa(p):
    'programa : lista_sentencias'
    p[0] = Programa(p[1])

def p_lista_sentencias(p):
    '''
    lista_sentencias : lista_sentencias sentencia
                     | 
    '''
    if len(p) == 3: p[0] = p[1] + [p[2]]
    else: p[0] = []

def p_sentencia(p):
    '''
    sentencia : declaracion_variable
              | asignacion
              | mientras
              | expresion PUNTOYCOMA
    '''
    p[0] = p[1]

def p_declaracion_variable(p):
    'declaracion_variable : VAR IDENTIFICADOR tipo_opcional asignacion_opcional PUNTOYCOMA'
    p[0] = DeclaracionVariable(p[2], p[3], p[4], p.lineno(1))
    tokens_reconocidos.append(f"Declaración de variable '{p[2]}' detectada correctamente (tipo: {p[3]})")

def p_tipo_opcional(p):
    '''
    tipo_opcional : DOSPTOS IDENTIFICADOR
                  | 
    '''
    p[0] = p[2] if len(p) == 3 else None

def p_asignacion_opcional(p):
    '''
    asignacion_opcional : ASIGNAR expresion
                        | 
    '''
    p[0] = p[2] if len(p) == 3 else None

def p_asignacion(p):
    'asignacion : IDENTIFICADOR ASIGNAR expresion PUNTOYCOMA'
    p[0] = Asignacion(p[1], p[3], p.lineno(1))
    tokens_reconocidos.append(f"Asignación detectada correctamente -> {p[1]} = ...")

def p_mientras(p):
    'mientras : WHILE LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE'
    p[0] = Mientras(p[3], p[6], p.lineno(1))
    tokens_reconocidos.append(f"Estructura while detectada correctamente en línea {p.lineno(1)}")

def p_expresion_binaria(p):
    '''
    expresion : expresion SUMA expresion
              | expresion RESTA expresion
              | expresion MULT expresion
              | expresion DIV expresion
              | expresion MOD expresion
              | expresion IGUAL expresion
              | expresion DIFERENTE expresion
              | expresion MENOR expresion
              | expresion MENORIGUAL expresion
              | expresion MAYOR expresion
              | expresion MAYORIGUAL expresion
              | expresion AND expresion
              | expresion OR expresion
    '''
    p[0] = OperacionBinaria(p[2], p[1], p[3], p.lineno(2))
    tokens_reconocidos.append(f"Operador '{p[2]}' reconocido entre expresiones en línea {p.lineno(2)}")

def p_expresion_unaria(p):
    '''
    expresion : NOT expresion
              | RESTA expresion %prec NOT
    '''
    p[0] = OperacionUnaria(p[1], p[2], p.lineno(1))
    tokens_reconocidos.append(f"Operador unario '{p[1]}' reconocido correctamente")

def p_expresion_literal(p):
    '''
    expresion : ENTERO
              | DECIMAL
              | CADENA
              | TRUE
              | FALSE
    '''
    val = p[1]
    if isinstance(val, int): t = 'Int'
    elif isinstance(val, float): t = 'Double'
    elif val in ['true', 'TRUE']: t, val = 'Bool', True
    elif val in ['false', 'FALSE']: t, val = 'Bool', False
    else: t = 'String'
    p[0] = Literal(val, t, p.lineno(1))

def p_expresion_identificador(p):
    'expresion : IDENTIFICADOR'
    p[0] = Identificador(p[1], p.lineno(1))

def p_sentencia_ignorada(p):
    '''
    sentencia : IDENTIFICADOR
    '''
    tokens_reconocidos.append(
        f"Línea {p.lineno(1)}: línea ignorada ('{p[1]}')"
    )
    p[0] = None


# -------------------------------------------------------
# Manejador general de errores sintácticos
# -------------------------------------------------------
def p_error(p):
    if p:
        errores_sintacticos.append(
            f"Error de sintaxis en línea {p.lineno}: token inesperado '{p.value}'"
        )
        # Recuperación básica: descartar el token y continuar
        parser = p.lexer.parser if hasattr(p.lexer, 'parser') else None
        if parser:
            parser.errok()
    else:
        errores_sintacticos.append("Error de sintaxis: fin de archivo inesperado")

analizador_sintactico = yacc.yacc()

# -----------------------------
# ANALIZADOR SEMÁNTICO
# -----------------------------
class Simbolo:
    def __init__(self, nombre, tipo, mutable, linea):
        self.nombre, self.tipo, self.mutable, self.linea = nombre, tipo, mutable, linea

class AnalizadorSemantico:
    def __init__(self):
        self.ambitos: List[Dict[str, Simbolo]] = [{}]
        self.errores: List[str] = []
        self.correctos: List[str] = []

    def nuevo_ambito(self): self.ambitos.append({})
    def cerrar_ambito(self): self.ambitos.pop()
    def declarar(self, nombre, tipo, mutable, linea):
        if nombre in self.ambitos[-1]:
            self.errores.append(f"Línea {linea}: variable '{nombre}' ya fue declarada.")
        else:
            self.ambitos[-1][nombre] = Simbolo(nombre, tipo, mutable, linea)
            self.correctos.append(f"Línea {linea}: variable '{nombre}' declarada correctamente con tipo '{tipo}'.")

    def buscar(self, nombre) -> Optional[Simbolo]:
        for a in reversed(self.ambitos):
            if nombre in a: return a[nombre]
        return None

    def verificar(self, nodo: Nodo):
        metodo = f"verificar_{type(nodo).__name__}"
        if hasattr(self, metodo): return getattr(self, metodo)(nodo)

    def verificar_Programa(self, nodo: Programa):
        for s in nodo.sentencias: self.verificar(s)

    def verificar_DeclaracionVariable(self, n: DeclaracionVariable):
        tipo_inf = self.verificar(n.valor) if n.valor else None
        tipo_final = n.tipo or tipo_inf or 'Desconocido'
        self.declarar(n.nombre, tipo_final, True, n.linea)

    def verificar_Asignacion(self, n: Asignacion):
        simb = self.buscar(n.nombre)
        if not simb:
            self.errores.append(f"Línea {n.linea}: variable '{n.nombre}' no declarada.")
            return
        tipo_valor = self.verificar(n.expresion)
        if tipo_valor and tipo_valor != simb.tipo:
            self.errores.append(f"Línea {n.linea}: tipo incompatible al asignar a '{n.nombre}'. Esperado {simb.tipo}, recibido {tipo_valor}.")
        else:
            self.correctos.append(f"Línea {n.linea}: asignación válida a '{n.nombre}'.")

    def verificar_Mientras(self, n: Mientras):
        tipo_cond = self.verificar(n.condicion)
        if tipo_cond != 'Bool':
            self.errores.append(f"Línea {n.linea}: la condición del while debe ser de tipo Bool.")
        else:
            self.correctos.append(f"Línea {n.linea}: estructura while válida.")
        self.nuevo_ambito()
        for s in n.cuerpo: self.verificar(s)
        self.cerrar_ambito()

    def verificar_Literal(self, n: Literal): return n.tipo
    def verificar_Identificador(self, n: Identificador):
        simb = self.buscar(n.nombre)
        if not simb:
            self.errores.append(f"Línea {n.linea}: identificador '{n.nombre}' no declarado.")
            return 'Desconocido'
        return simb.tipo

# -----------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------
def analizar_archivo(ruta: str):
    if not os.path.exists(ruta):
        print(f"No se encontró el archivo: {ruta}")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        codigo = f.read()

    print(f"Analizando archivo: {ruta}\n")
    lexer = analizador_lexico
    parser = analizador_sintactico
    lexer.lineno = 1
    ast = parser.parse(codigo, lexer=lexer)

    sem = AnalizadorSemantico()
    if ast: sem.verificar(ast)

    # Crear carpeta logs
    os.makedirs("logs", exist_ok=True)
    archivo_log = f"logs/analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    with open(archivo_log, "w", encoding="utf-8") as log:
        log.write(f"--- RESULTADOS DEL ANÁLISIS ({ruta}) ---\n\n")

        log.write("✔ TOKENS Y ELEMENTOS RECONOCIDOS:\n")
        for t in tokens_reconocidos:
            log.write("  " + t + "\n")

        log.write("\n⚠ ERRORES LÉXICOS:\n")
        for e in errores_lexicos:
            log.write("  " + e + "\n")

        log.write("\n⚠ ERRORES SINTÁCTICOS:\n")
        for e in errores_sintacticos:
            log.write("  " + e + "\n")

        log.write("\n⚠ ERRORES SEMÁNTICOS:\n")
        for e in sem.errores:
            log.write("  " + e + "\n")

        log.write("\n✔ RECONOCIMIENTOS CORRECTOS SEMÁNTICOS:\n")
        for c in sem.correctos:
            log.write("  " + c + "\n")

    print("Análisis completado. Revisa:", archivo_log)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    ruta_archivo = "algoritmos/algoritmo_identificadores_y_operadores.swift"
    analizar_archivo(ruta_archivo)
