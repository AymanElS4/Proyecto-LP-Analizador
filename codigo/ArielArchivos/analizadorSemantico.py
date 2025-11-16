from __future__ import annotations
import ply.yacc as yacc
from typing import Dict, List, Optional
# Importamos la lista de tokens del lexer
from analizadorLexicoArielAAT123 import tokens, errores_lexicos, tokens_reconocidos

# =========================================================================
# 2. NODOS DEL ÁRBOL (AST) - Clases mínimas requeridas
# =========================================================================
class Nodo:
    """Clase base para todos los nodos del AST."""
    def __init__(self, linea: int):
        self.linea = linea
    def get_linea(self): return self.linea

class Programa(Nodo):
    def __init__(self, sentencias):
        super().__init__(1)
        self.sentencias = sentencias

class DeclaracionVariable(Nodo): 
    def __init__(self, nombre, tipo, valor, mutable, linea):
        super().__init__(linea)
        self.nombre, self.tipo, self.valor, self.mutable = nombre, tipo, valor, mutable

class Asignacion(Nodo):
    def __init__(self, nombre, expresion, linea):
        super().__init__(linea)
        self.nombre, self.expresion = nombre, expresion

class Si(Nodo):
    def __init__(self, condicion, cuerpo_if, cuerpo_else, linea):
        super().__init__(linea)
        self.condicion, self.cuerpo_if, self.cuerpo_else = condicion, cuerpo_if, cuerpo_else

class Mientras(Nodo):
    def __init__(self, condicion, cuerpo, linea):
        super().__init__(linea)
        self.condicion, self.cuerpo = condicion, cuerpo

class DefinicionClase(Nodo):
    def __init__(self, nombre, propiedades, metodos, linea):
        super().__init__(linea)
        self.nombre, self.propiedades, self.metodos = nombre, propiedades, metodos

class DefinicionFuncion(Nodo):
    def __init__(self, nombre, parametros, tipo_retorno, cuerpo, linea):
        super().__init__(linea)
        self.nombre, self.parametros, self.tipo_retorno, self.cuerpo = nombre, parametros, tipo_retorno, cuerpo

class Parametro(Nodo):
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
        
# =========================================================================
# 3. ANALIZADOR SINTÁCTICO (PLY Yacc) - Reglas Ariel + Mínimas
# =========================================================================
errores_sintacticos: List[str] = []

# La variable tokens ya está importada del archivo lexer
# tokens = tokens # no es necesario, pero aquí se usaría si no se importara directamente.

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
        p[0] = p[1] + ([p[2]] if p[2] is not None else []) 
    else:
        p[0] = []

def p_sentencia(p):
    '''
    sentencia : declaracion_variable_ariel
              | asignacion_ariel
              | mientras_ariel
              | si_minimo
              | definicion_funcion_ariel
              | definicion_clase_minimo
              | retorno_completo
              | expresion PUNTOYCOMA
    '''
    p[0] = p[1]

# --- REGLAS SINTÁCTICAS DE ARIEL: Declaración VAR (Incluye LET para Semántico) ---
def p_declaracion_variable_ariel(p):
    '''
    declaracion_variable_ariel : VAR IDENTIFICADOR tipo_opcional asignacion_opcional PUNTOYCOMA
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

# --- REGLA SINTÁCTICA MÍNIMA: Asignación (Re-asignación) ---
def p_asignacion_ariel(p):
    'asignacion_ariel : IDENTIFICADOR ASIGNAR expresion PUNTOYCOMA'
    p[0] = Asignacion(p[1], p[3], p.lineno(1))

# --- REGLAS SINTÁCTICAS DE ARIEL: While Loops ---
def p_mientras_ariel(p):
    'mientras_ariel : WHILE LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE'
    p[0] = Mientras(p[3], p[6], p.lineno(1))

# --- REGLAS SINTÁCTICAS MÍNIMAS: Condicionales (If/Else) ---
def p_si_minimo(p):
    '''
    si_minimo : IF LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE
              | IF LPAREN expresion RPAREN LBRACE lista_sentencias RBRACE ELSE LBRACE lista_sentencias RBRACE
    '''
    p[0] = Si(p[3], p[6], p[10] if len(p) > 8 else [], p.lineno(1))

# --- REGLAS SINTÁCTICAS MÍNIMAS: Clases ---
def p_definicion_clase_minimo(p):
    'definicion_clase_minimo : CLASS IDENTIFICADOR LBRACE lista_miembros_clase RBRACE'
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
    miembro_clase : declaracion_variable_ariel
                  | definicion_funcion_ariel
    '''
    p[0] = p[1]

# --- REGLAS SINTÁCTICAS DE ARIEL: Funciones con Default ---
def p_definicion_funcion_ariel(p):
    'definicion_funcion_ariel : FUNC IDENTIFICADOR LPAREN lista_parametros_ariel RPAREN tipo_retorno LBRACE lista_sentencias RBRACE'
    p[0] = DefinicionFuncion(p[2], p[4], p[6], p[8], p.lineno(1))

def p_lista_parametros_ariel(p):
    '''
    lista_parametros_ariel : lista_parametros_ariel COMA parametro_ariel
                           | parametro_ariel
                           |
    '''
    if len(p) == 4: p[0] = p[1] + [p[3]]
    elif len(p) == 2: p[0] = [p[1]]
    else: p[0] = []

def p_parametro_ariel(p):
    '''
    parametro_ariel : IDENTIFICADOR DOSPTOS IDENTIFICADOR asignacion_opcional
    '''
    linea = p.lineno(1) 
    nombre = p[1]
    tipo = p[3]
    valor_default = p[4] 
    p[0] = Parametro(nombre, tipo, valor_default, linea)

def p_tipo_retorno(p):
    '''
    tipo_retorno : FLECHA IDENTIFICADOR
                 |
    '''
    p[0] = p[2] if len(p) == 3 else None

def p_retorno_completo(p):
    'retorno_completo : RETURN expresion PUNTOYCOMA'
    p[0] = Retorno(p[2], p.lineno(1))

# --- REGLAS SINTÁCTICAS DE ARIEL: Tuples ---
def p_expresion_tupla_ariel(p):
    'expresion : LPAREN lista_expresiones_ariel RPAREN'
    if len(p[2]) >= 2:
        p[0] = Tupla(p[2], p.lineno(1))
    elif len(p[2]) == 1:
        p[0] = p[2][0]
    else:
        p[0] = Tupla([], p.lineno(1))

def p_expresion_llamada(p):
    'expresion : IDENTIFICADOR LPAREN lista_expresiones_ariel RPAREN'
    p[0] = LlamadaFuncion(p[1], p[3], p.lineno(1))

def p_lista_expresiones_ariel(p):
    '''
    lista_expresiones_ariel : lista_expresiones_ariel COMA expresion
                            | expresion
                            |
    '''
    if len(p) == 4: p[0] = p[1] + [p[3]]
    elif len(p) == 2: p[0] = [p[1]]
    else: p[0] = []

# --- REGLAS SINTÁCTICAS: Expresiones (Mínimo Requerido) ---
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
    elif val in ['true', 'TRUE', True, 'false', 'FALSE', False]: t, val = 'Bool', (val in ['true', 'TRUE', True])
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


# =========================================================================
# 4. ANALIZADOR SEMÁNTICO (Reglas Ariel)
# =========================================================================
class Simbolo:
    def __init__(self, nombre, tipo, mutable, linea):
        self.nombre, self.tipo, self.mutable, self.linea = nombre, tipo, mutable, linea

class AnalizadorSemantico:
    def __init__(self):
        self.ambitos: List[Dict[str, Simbolo]] = [{}]
        self.errores: List[str] = []
        self.tipos_numericos = ['Int', 'Double']
        self.tipos_compatibles = {
            'Int': ['Int', 'Double'],
            'Double': ['Int', 'Double'],
            'String': ['String'],
            'Bool': ['Bool']
        }

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

    def verificar(self, nodo) -> Optional[str]:
        if nodo is None: return None
        metodo = f"verificar_{type(nodo).__name__}"
        if hasattr(self, metodo): return getattr(self, metodo)(nodo)
        elif hasattr(nodo, 'sentencias'):
             [self.verificar(s) for s in nodo.sentencias]
        return None

    def verificar_DeclaracionVariable(self, n: DeclaracionVariable):
        tipo_inf = self.verificar(n.valor)
        tipo_final = n.tipo or tipo_inf or 'Desconocido'
        
        if n.valor and n.tipo and tipo_inf and tipo_inf not in self.tipos_compatibles.get(n.tipo, []):
            self.errores.append(f"❌ Línea {n.linea}: Tipo de inicialización incompatible para '{n.nombre}'. Esperado {n.tipo}, recibido {tipo_inf}.")
            
        self.declarar(n.nombre, tipo_final, n.mutable, n.linea)

    def verificar_Asignacion(self, n: Asignacion):
        simb = self.buscar(n.nombre)
        if not simb:
            self.errores.append(f"❌ Línea {n.linea}: variable '{n.nombre}' no declarada.")
            return
            
        if not simb.mutable:
            self.errores.append(f"❌ Línea {n.linea}: variable '{n.nombre}' es inmutable (let) y no puede ser reasignada.")
            return
            
        tipo_valor = self.verificar(n.expresion)
        if tipo_valor and tipo_valor not in self.tipos_compatibles.get(simb.tipo, []):
             self.errores.append(f"❌ Línea {n.linea}: Tipo incompatible al reasignar a '{n.nombre}'. Esperado {simb.tipo}, recibido {tipo_valor}.")

    def verificar_OperacionBinaria(self, n: OperacionBinaria):
        tipo_izq, tipo_der = self.verificar(n.izquierda), self.verificar(n.derecha)
        
        if n.operador in ['+', '-', '*', '/', '%']:
            if tipo_izq in self.tipos_numericos and tipo_der in self.tipos_numericos:
                return 'Double' if 'Double' in [tipo_izq, tipo_der] else 'Int'
            
            if tipo_izq == 'String' and n.operador == '+' and tipo_der == 'String': return 'String'
            
            if 'Desconocido' in [tipo_izq, tipo_der]: return 'Desconocido'
            
            self.errores.append(f"❌ Línea {n.get_linea()}: '{n.operador}' requiere operandos compatibles ({self.tipos_numericos} o String + String), recibido {tipo_izq} y {tipo_der}.")
            return 'Desconocido'

        elif n.operador in ['&&', '||']:
            if tipo_izq == 'Bool' and tipo_der == 'Bool': return 'Bool'
            if 'Desconocido' in [tipo_izq, tipo_der]: return 'Desconocido'
            self.errores.append(f"❌ Línea {n.get_linea()}: '{n.operador}' requiere tipos Bool, recibido {tipo_izq} y {tipo_der}.")
            return 'Bool'
            
        elif n.operador in ['==', '!=', '<', '>', '<=', '>=']: return 'Bool'
        
        return 'Desconocido'
        
    def verificar_Mientras(self, n: Mientras):
        tipo_cond = self.verificar(n.condicion)
        if tipo_cond not in ['Bool', 'Desconocido']:
            self.errores.append(f"❌ Línea {n.get_linea()}: La condición de WHILE debe ser de tipo Bool, recibido {tipo_cond}.")
        self.nuevo_ambito()
        [self.verificar(s) for s in n.cuerpo]
        self.cerrar_ambito()
        
    def verificar_Si(self, n: Si):
        tipo_cond = self.verificar(n.condicion)
        if tipo_cond not in ['Bool', 'Desconocido']:
            self.errores.append(f"❌ Línea {n.get_linea()}: La condición de IF debe ser de tipo Bool, recibido {tipo_cond}.")
            
        self.nuevo_ambito()
        [self.verificar(s) for s in n.cuerpo_if]
        self.cerrar_ambito()
        
        if n.cuerpo_else:
            self.nuevo_ambito()
            [self.verificar(s) for s in n.cuerpo_else]
            self.cerrar_ambito()
            
    def verificar_DefinicionClase(self, n: DefinicionClase):
        self.declarar(n.nombre, 'Class', False, n.linea)
        self.nuevo_ambito()
        [self.verificar(m) for m in n.propiedades + n.metodos]
        self.cerrar_ambito()
        
    def verificar_DefinicionFuncion(self, n: DefinicionFuncion):
        self.declarar(n.nombre, f"Function->{n.tipo_retorno or 'Void'}", False, n.linea)
        self.nuevo_ambito()
        for p in n.parametros:
             if p.valor_default: self.verificar(p.valor_default)
             self.declarar(p.nombre, p.tipo, False, p.linea)
        for s in n.cuerpo: self.verificar(s)
        self.cerrar_ambito()
        
    def verificar_Tupla(self, n: Tupla):
        tipos = [self.verificar(elem) or 'Desconocido' for elem in n.elementos]
        return f"Tuple<{', '.join(tipos)}>"

    def verificar_Literal(self, n: Literal): return n.tipo
    def verificar_Identificador(self, n: Identificador):
        simb = self.buscar(n.nombre)
        if not simb:
            self.errores.append(f"❌ Línea {n.get_linea()}: identificador '{n.nombre}' no declarado.")
            return 'Desconocido'
        return simb.tipo
    def verificar_OperacionUnaria(self, n: OperacionUnaria):
        tipo = self.verificar(n.operando)
        if n.operador == '!':
            if tipo not in ['Bool', 'Desconocido']:
                self.errores.append(f"❌ Línea {n.get_linea()}: operador '!' requiere tipo Bool.")
            return 'Bool'
        elif n.operador == '-':
            if tipo not in self.tipos_numericos and tipo != 'Desconocido':
                self.errores.append(f"❌ Línea {n.get_linea()}: operador '-' requiere tipo numérico.")
            return tipo
        return 'Desconocido'
    def verificar_LlamadaFuncion(self, n: LlamadaFuncion):
        [self.verificar(arg) for arg in n.argumentos]
        return 'Desconocido'
    def verificar_Retorno(self, n: Retorno): return self.verificar(n.expresion)
    def verificar_AccesoMiembro(self, n: AccesoMiembro):
        self.verificar(n.objeto)
        return 'Desconocido'
        
# Inicialización del analizador semántico (Se mueve a main.py para la ejecución)
# analizador_sintactico = yacc.yacc()