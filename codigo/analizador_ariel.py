from __future__ import annotations
import ply.lex as lex
import ply.yacc as yacc
from typing import Dict, List, Optional
import os
from datetime import datetime
import sys

# Forzar UTF-8 para manejo de logs
sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------
# 1. ANALIZADOR LÉXICO (PLY Lex)
# -----------------------------
# Palabras reservadas requeridas
reservadas = {
    'var': 'VAR', 'let': 'LET', 'func': 'FUNC', 'while': 'WHILE', 'if': 'IF',
    'else': 'ELSE', 'true': 'TRUE', 'false': 'FALSE',
    'return': 'RETURN', 'class': 'CLASS',
    'self': 'SELF', 'init': 'INIT',
}

tokens = [
    'IDENTIFICADOR', 'ENTERO', 'DECIMAL', 'CADENA',
    'LPAREN','RPAREN','LBRACE','LBRACE','LBRACKET','RBRACKET',
    'COMA','DOSPTOS','PUNTOYCOMA','ASIGNAR','PUNTO',
    'SUMA','RESTA','MULT','DIV','MOD',
    'AND','OR','NOT',
    'IGUAL','DIFERENTE','MENOR','MAYOR','MENORIGUAL','MAYORIGUAL',
    'FLECHA'
] + list(reservadas.values())

# Definiciones de tokens
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

errores_lexicos = []
tokens_reconocidos = [] 

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
    t.lexer.lineno += t.value.count('\n') # Contar líneas en comentarios
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

analizador_lexico = lex.lex()

# -----------------------------
# 2. NODOS DEL ÁRBOL (AST) - Requeridos
# -----------------------------
class Nodo:
    """Clase base para todos los nodos del AST."""
    def __init__(self, linea: int):
        self.linea = linea

class Programa(Nodo):
    def __init__(self, sentencias):
        super().__init__(1)
        self.sentencias = sentencias

# Variables y Asignación
class DeclaracionVariable(Nodo): 
    def __init__(self, nombre, tipo, valor, mutable, linea):
        super().__init__(linea)
        self.nombre, self.tipo, self.valor, self.mutable = nombre, tipo, valor, mutable

class Asignacion(Nodo):
    def __init__(self, nombre, expresion, linea):
        super().__init__(linea)
        self.nombre, self.expresion = nombre, expresion

# Estructuras de Control (If/Else, While)
class Si(Nodo):
    def __init__(self, condicion, cuerpo_if, cuerpo_else, linea):
        super().__init__(linea)
        self.condicion, self.cuerpo_if, self.cuerpo_else = condicion, cuerpo_if, cuerpo_else

class Mientras(Nodo):
    def __init__(self, condicion, cuerpo, linea):
        super().__init__(linea)
        self.condicion, self.cuerpo = condicion, cuerpo

# Clases y Funciones
class DefinicionClase(Nodo):
    def __init__(self, nombre, propiedades, metodos, linea):
        super().__init__(linea)
        self.nombre, self.propiedades, self.metodos = nombre, propiedades, metodos

class DefinicionFuncion(Nodo):
    def __init__(self, nombre, parametros, tipo_retorno, cuerpo, linea):
        super().__init__(linea)
        self.nombre, self.parametros, self.tipo_retorno, self.cuerpo = nombre, parametros, tipo_retorno, cuerpo

class Parametro(Nodo): # Parámetro con valor por defecto
    def __init__(self, nombre, tipo, valor_default, linea):
        super().__init__(linea)
        self.nombre, self.tipo, self.valor_default = nombre, tipo, valor_default

class Retorno(Nodo):
    def __init__(self, expresion, linea):
        super().__init__(linea)
        self.expresion = expresion

class LlamadaFuncion(Nodo):
    def __init__(self, nombre, argumentos, linea):
        super().__init__(linea)
        self.nombre, self.argumentos = nombre, argumentos

class AccesoMiembro(Nodo): 
    def __init__(self, objeto, miembro, linea):
        super().__init__(linea)
        self.objeto, self.miembro = objeto, miembro

# Expresiones y Tuplas
class Tupla(Nodo): 
    def __init__(self, elementos, linea):
        super().__init__(linea)
        self.elementos = elementos

class OperacionBinaria(Nodo): 
    def __init__(self, op, izq, der, linea):
        super().__init__(linea)
        self.operador, self.izquierda, self.derecha = op, izq, der

class OperacionUnaria(Nodo): 
    def __init__(self, op, opnd, linea):
        super().__init__(linea)
        self.operador, self.operando = op, opnd

class Literal(Nodo):
    def __init__(self, valor, tipo, linea):
        super().__init__(linea)
        self.valor, self.tipo = valor, tipo

class Identificador(Nodo): 
    def __init__(self, nombre, linea):
        super().__init__(linea)
        self.nombre = nombre
        
# -----------------------------
# 3. ANALIZADOR SINTÁCTICO (PLY Yacc)
# -----------------------------
errores_sintacticos = []

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENOR', 'MENORIGUAL', 'MAYOR', 'MAYORIGUAL'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('right', 'NOT'),
    ('left', 'PUNTO'),
)

def p_programa(p):
    'programa : lista_sentencias'
    p[0] = Programa(p[1])

def p_lista_sentencias(p):
    '''
    lista_sentencias : lista_sentencias sentencia
                     |
    '''
    if len(p) == 3:
        # Solo agregar si la sentencia no es None (e.g., retorno en métodos)
        p[0] = p[1] + ([p[2]] if p[2] is not None else []) 
    else:
        p[0] = []

def p_sentencia(p):
    '''
    sentencia : declaracion_variable
              | asignacion
              | mientras
              | si
              | funcion
              | clase
              | retorno
              | expresion PUNTOYCOMA
    '''
    p[0] = p[1]

# Variables y Asignación
def p_declaracion_variable(p):
    '''
    declaracion_variable : VAR IDENTIFICADOR tipo_opcional asignacion_opcional PUNTOYCOMA
                         | LET IDENTIFICADOR tipo_opcional asignacion_opcional PUNTOYCOMA
    '''
    mutable = (p[1] == 'var')
    p[0] = DeclaracionVariable(p[2], p[3], p[4], mutable, p.lineno(1))

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

# Estructuras de Control (While, If/Else)
def p_mientras(p):
    'mientras : WHILE LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE'
    p[0] = Mientras(p[3], p[6], p.lineno(1))

def p_si(p):
    '''
    si : IF LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE
       | IF LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE ELSE LBRACE lista_sentencias RBRACE
    '''
    p[0] = Si(p[3], p[6], p[10] if len(p) > 8 else [], p.lineno(1))

# Clases y Funciones
def p_clase(p):
    'clase : CLASS IDENTIFICADOR LBRACE lista_miembros_clase RBRACE'
    propiedades = [m for m in p[4] if isinstance(m, DeclaracionVariable)]
    metodos = [m for m in p[4] if isinstance(m, DefinicionFuncion)]
    p[0] = DefinicionClase(p[2], propiedades, metodos, p.lineno(1))

def p_lista_miembros_clase(p):
    '''
    lista_miembros_clase : lista_miembros_clase miembro_clase
                         |
    '''
    if len(p) == 3: p[0] = p[1] + [p[2]]
    else: p[0] = []

def p_miembro_clase(p):
    '''
    miembro_clase : declaracion_variable
                  | funcion
    '''
    p[0] = p[1]

def p_funcion(p):
    '''
    funcion : FUNC IDENTIFICADOR LPAREN lista_parametros RPAREN tipo_retorno LBRACE lista_sentencias RBRACE
    '''
    p[0] = DefinicionFuncion(p[2], p[4], p[6], p[8], p.lineno(1))

def p_lista_parametros(p):
    '''
    lista_parametros : lista_parametros COMA parametro
                     | parametro
                     |
    '''
    if len(p) == 4: p[0] = p[1] + [p[3]]
    elif len(p) == 2: p[0] = [p[1]]
    else: p[0] = []

def p_parametro(p):
    '''
    parametro : IDENTIFICADOR DOSPTOS IDENTIFICADOR ASIGNAR expresion
              | IDENTIFICADOR DOSPTOS IDENTIFICADOR
    '''
    p[0] = Parametro(p[1], p[3], p[5] if len(p) == 6 else None, p.lineno(1))

def p_tipo_retorno(p):
    '''
    tipo_retorno : FLECHA IDENTIFICADOR
                 |
    '''
    p[0] = p[2] if len(p) == 3 else None

def p_retorno(p):
    'retorno : RETURN expresion PUNTOYCOMA'
    p[0] = Retorno(p[2], p.lineno(1))

# Expresiones y Tuplas
def p_expresion_tupla(p):
    'expresion : LPAREN lista_expresiones RPAREN'
    if len(p[2]) >= 2:
        p[0] = Tupla(p[2], p.lineno(1))
    elif len(p[2]) == 1:
        p[0] = p[2][0] # Expresión simple entre paréntesis
    else:
        # Permite tupla vacía, aunque no es estricto Swift
        p[0] = Tupla([], p.lineno(1))

def p_expresion_llamada(p):
    'expresion : IDENTIFICADOR LPAREN lista_expresiones RPAREN'
    p[0] = LlamadaFuncion(p[1], p[3], p.lineno(1))

def p_lista_expresiones(p):
    '''
    lista_expresiones : lista_expresiones COMA expresion
                      | expresion
                      |
    '''
    if len(p) == 4: p[0] = p[1] + [p[3]]
    elif len(p) == 2: p[0] = [p[1]]
    else: p[0] = []

def p_expresion_acceso_miembro(p):
    'expresion : expresion PUNTO IDENTIFICADOR'
    p[0] = AccesoMiembro(p[1], p[3], p.lineno(2))

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

def p_expresion_unaria(p):
    '''
    expresion : NOT expresion
              | RESTA expresion %prec NOT
    '''
    p[0] = OperacionUnaria(p[1], p[2], p.lineno(1))

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

def p_error(p):
    if p:
        errores_sintacticos.append(
            f"❌ Error de sintaxis en línea {p.lineno}: token inesperado '{p.value}' (tipo: {p.type})"
        )
        analizador_sintactico.errok()
    else:
        errores_sintacticos.append("❌ Error de sintaxis: fin de archivo inesperado")

analizador_sintactico = yacc.yacc()

# -----------------------------
# 4. ANALIZADOR SEMÁNTICO - Requerido
# -----------------------------
class Simbolo:
    def __init__(self, nombre, tipo, mutable, linea):
        self.nombre, self.tipo, self.mutable, self.linea = nombre, tipo, mutable, linea

class AnalizadorSemantico:
    def __init__(self):
        self.ambitos: List[Dict[str, Simbolo]] = [{}]
        self.errores: List[str] = []

    def nuevo_ambito(self): self.ambitos.append({})
    def cerrar_ambito(self): self.ambitos.pop()

    def declarar(self, nombre, tipo, mutable, linea):
        if nombre in self.ambitos[-1]:
            self.errores.append(f"❌ Línea {linea}: variable '{nombre}' ya fue declarada en este ámbito.")
        else:
            self.ambitos[-1][nombre] = Simbolo(nombre, tipo, mutable, linea)

    def buscar(self, nombre) -> Optional[Simbolo]:
        for a in reversed(self.ambitos):
            if nombre in a: return a[nombre]
        return None

    def verificar(self, nodo: Nodo) -> Optional[str]:
        if nodo is None: return None
        metodo = f"verificar_{type(nodo).__name__}"
        if hasattr(self, metodo): return getattr(self, metodo)(nodo)
        return None

    def verificar_Programa(self, n: Programa):
        for s in n.sentencias: self.verificar(s)

    # Variables y Asignaciones
    def verificar_DeclaracionVariable(self, n: DeclaracionVariable):
        tipo_inf = self.verificar(n.valor)
        tipo_final = n.tipo or tipo_inf or 'Desconocido'
        if n.valor and n.tipo and tipo_inf and tipo_inf != n.tipo and tipo_inf != 'Desconocido':
            self.errores.append(f"❌ Línea {n.linea}: tipo de asignación incompatible para '{n.nombre}'. Esperado {n.tipo}, recibido {tipo_inf}.")
        self.declarar(n.nombre, tipo_final, n.mutable, n.linea)

    def verificar_Asignacion(self, n: Asignacion):
        simb = self.buscar(n.nombre)
        if not simb:
            self.errores.append(f"❌ Línea {n.linea}: variable '{n.nombre}' no declarada.")
            return
        if not simb.mutable:
            self.errores.append(f"❌ Línea {n.linea}: variable '{n.nombre}' es inmutable (let).")
            return
        tipo_valor = self.verificar(n.expresion)
        if tipo_valor and tipo_valor != simb.tipo and simb.tipo != 'Desconocido' and tipo_valor != 'Desconocido':
            self.errores.append(f"❌ Línea {n.linea}: tipo incompatible al reasignar a '{n.nombre}'. Esperado {simb.tipo}, recibido {tipo_valor}.")

    # Estructuras de Control
    def verificar_Mientras(self, n: Mientras):
        tipo_cond = self.verificar(n.condicion)
        if tipo_cond not in ['Bool', 'Desconocido']:
            self.errores.append(f"❌ Línea {n.linea}: la condición del while debe ser de tipo Bool, recibido {tipo_cond}.")
        self.nuevo_ambito()
        for s in n.cuerpo: self.verificar(s)
        self.cerrar_ambito()

    def verificar_Si(self, n: Si):
        tipo_cond = self.verificar(n.condicion)
        if tipo_cond not in ['Bool', 'Desconocido']:
            self.errores.append(f"❌ Línea {n.linea}: la condición del if debe ser de tipo Bool, recibido {tipo_cond}.")
        self.nuevo_ambito()
        for s in n.cuerpo_if: self.verificar(s)
        self.cerrar_ambito()
        if n.cuerpo_else:
            self.nuevo_ambito()
            for s in n.cuerpo_else: self.verificar(s)
            self.cerrar_ambito()
            
    # Clases y Funciones
    def verificar_DefinicionClase(self, n):
        self.declarar(n.nombre, 'Class', False, n.linea)
        self.nuevo_ambito()
        [self.verificar(p) for p in n.propiedades]
        [self.verificar(m) for m in n.metodos]
        self.cerrar_ambito()

    def verificar_DefinicionFuncion(self, n: DefinicionFuncion):
        # Se registra la función a nivel de ámbito actual (para uso como método o función global)
        self.declarar(n.nombre, f"Function->{n.tipo_retorno or 'Void'}", False, n.linea)
        self.nuevo_ambito()
        # Verificar parámetros y valores por defecto
        for p in n.parametros:
            tipo_param = p.tipo or (self.verificar(p.valor_default) if p.valor_default else 'Desconocido')
            self.declarar(p.nombre, tipo_param, False, p.linea)
        # Verificar cuerpo
        for s in n.cuerpo: self.verificar(s)
        self.cerrar_ambito()
        
    def verificar_AccesoMiembro(self, n): 
        self.verificar(n.objeto)
        return 'Desconocido'

    def verificar_LlamadaFuncion(self, n: LlamadaFuncion):
        [self.verificar(arg) for arg in n.argumentos]
        return 'Desconocido'

    def verificar_Retorno(self, n: Retorno): 
        return self.verificar(n.expresion)

    # Expresiones
    def verificar_Tupla(self, n: Tupla):
        tipos = [self.verificar(elem) or 'Desconocido' for elem in n.elementos]
        return f"Tuple({', '.join(tipos)})"

    def verificar_OperacionBinaria(self, n: OperacionBinaria):
        tipo_izq, tipo_der = self.verificar(n.izquierda), self.verificar(n.derecha)
        
        if n.operador in ['+', '-', '*', '/', '%']:
            if tipo_izq in ['Int', 'Double'] and tipo_der in ['Int', 'Double']:
                return 'Double' if 'Double' in [tipo_izq, tipo_der] else 'Int'
            if tipo_izq == 'String' and n.operador == '+' and tipo_der == 'String': return 'String'
            if 'Desconocido' in [tipo_izq, tipo_der]: return 'Desconocido'
            self.errores.append(f"❌ Línea {n.linea}: '{n.operador}' requiere tipos compatibles, recibido {tipo_izq} y {tipo_der}.")
            return 'Desconocido'

        elif n.operador in ['==', '!=', '<', '>', '<=', '>=']: return 'Bool'
        
        elif n.operador in ['&&', '||']:
            if tipo_izq == 'Bool' and tipo_der == 'Bool': return 'Bool'
            if 'Desconocido' in [tipo_izq, tipo_der]: return 'Desconocido'
            self.errores.append(f"❌ Línea {n.linea}: '{n.operador}' requiere tipos Bool, recibido {tipo_izq} y {tipo_der}.")
            return 'Bool'
        
        return 'Desconocido'

    def verificar_OperacionUnaria(self, n: OperacionUnaria):
        tipo = self.verificar(n.operando)
        if n.operador == '!':
            if tipo not in ['Bool', 'Desconocido']:
                self.errores.append(f"❌ Línea {n.linea}: operador '!' requiere tipo Bool, recibido {tipo}.")
            return 'Bool'
        
        elif n.operador == '-':
            if tipo not in ['Int', 'Double', 'Desconocido']:
                self.errores.append(f"❌ Línea {n.linea}: operador '-' requiere tipo numérico, recibido {tipo}.")
            return tipo
        return 'Desconocido'

    def verificar_Literal(self, n: Literal): return n.tipo
    
    def verificar_Identificador(self, n: Identificador):
        simb = self.buscar(n.nombre)
        if not simb:
            self.errores.append(f"❌ Línea {n.linea}: identificador '{n.nombre}' no declarado.")
            return 'Desconocido'
        return simb.tipo


# -----------------------------
# 5. FUNCIÓN PRINCIPAL Y RESUMEN
# -----------------------------
def analizar_archivo(ruta: str):
    if not os.path.exists(ruta):
        return

    with open(ruta, "r", encoding="utf-8") as f:
        codigo = f.read()
    
    global tokens_reconocidos, errores_lexicos, errores_sintacticos
    tokens_reconocidos = []
    errores_lexicos = []
    errores_sintacticos = []
    
    lexer = analizador_lexico
    parser = analizador_sintactico
    lexer.lineno = 1
    ast = parser.parse(codigo, lexer=lexer)

    sem = AnalizadorSemantico()
    if ast: sem.verificar(ast)

    # Preparar el nombre del archivo de log
    os.makedirs("logs", exist_ok=True)
    
    base_filename = os.path.basename(ruta)
    name_without_ext = os.path.splitext(base_filename)[0]
    timestamp = datetime.now().strftime('%Y%m%d-%Hh%M')
    
    # Formato solicitado: [nombre_del_archivo]-[ArielAT123]-[fecha]-[hora].txt
    archivo_log = f"logs/{name_without_ext}-ArielAT123-{timestamp}.txt"

    with open(archivo_log, "w", encoding="utf-8") as log:
        log.write("=" * 60 + "\n")
        log.write("ANÁLISIS DE COMPILADOR (ARIEL ARIAS TIPÁN) - VERSIÓN CORREGIDA\n")
        log.write(f"Archivo: {ruta} | Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        log.write("=" * 60 + "\n\n")

        log.write("RESPONSABILIDADES CLAVE (ARIEL):\n")
        log.write("- Declaración y Asignación de variables (var/let) con tipos.\n")
        log.write("- Expresiones y Condicionales (if/else y operadores).\n")
        log.write("- Bucles WHILE.\n")
        log.write("- Tuplas (estructura de datos).\n")
        log.write("- Funciones/Métodos con parámetros por defecto y return.\n")
        log.write("- Definición de Clases, Propiedades y Métodos.\n\n")

        log.write("✅ RESUMEN DE TOKENS RECONOCIDOS:\n")
        log.write("-" * 60 + f"\nTotal: {len(tokens_reconocidos)} tokens\n\n")

        log.write("❌ ERRORES LÉXICOS:\n")
        log.write("-" * 60 + "\n")
        if errores_lexicos: log.write('\n'.join(errores_lexicos) + '\n')
        else: log.write("No se encontraron errores léxicos.\n")
        log.write(f"\nTotal: {len(errores_lexicos)} error(es) léxico(s)\n\n")

        log.write("❌ ERRORES SINTÁCTICOS:\n")
        log.write("-" * 60 + "\n")
        if errores_sintacticos: log.write('\n'.join(errores_sintacticos) + '\n')
        else: log.write("No se encontraron errores sintácticos.\n")
        log.write(f"\nTotal: {len(errores_sintacticos)} error(es) sintáctico(s)\n\n")

        log.write("❌ ERRORES SEMÁNTICOS:\n")
        log.write("-" * 60 + "\n")
        if sem.errores: log.write('\n'.join(sem.errores) + '\n')
        else: log.write("No se encontraron errores semánticos.\n")
        log.write(f"\nTotal: {len(sem.errores)} error(es) semántico(s)\n\n")

        total_errores = len(errores_lexicos) + len(errores_sintacticos) + len(sem.errores)
        log.write("=" * 60 + "\n")
        log.write(f"RESUMEN FINAL: {total_errores} error(es) total(es).\n")
        log.write("=" * 60 + "\n")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # Cambiar la ruta del archivo a analizar
    ruta_archivo = "algoritmos/test_ariel_completo.swift"
    analizar_archivo(ruta_archivo)