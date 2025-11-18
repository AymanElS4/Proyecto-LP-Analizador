# analizador_swift.py
# Lexer + Parser + Semántica para Swift-lite
# Guarda como Proyecto-LP-Analizador/codigo/analizador_swift.py
# Ejecuta: python analizador_swift.py

import ply.lex as lex
import ply.yacc as yacc
import datetime
import os

# --------------------
# LEXER
# --------------------

tokens = [
    'INTEGER','FLOAT','DOUBLE','BOOLEAN','STRING','CHARACTER',
    'LPAREN','RPAREN','LBRACE','RBRACE','LBRACKET','RBRACKET',
    'COMMA','SEMICOLON','COLON',
    'LET','IF','ELSE','FOR','IN',
    'ID','ASSIGN','LAMBDA_IN',
    'PLUS','MINUS','TIMES','DIVIDE','MOD',
    'EQ','NE','LT','GT','LE','GE',
    'AND','OR','NOT','DOTDOTDOT'
]

# simple token regex
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
t_DOTDOTDOT = r'\.\.\.'

# reserved words mapping
reserved = {
    'let': 'LET',
    'for': 'FOR',
    'in': 'IN',
    'if': 'IF',
    'else': 'ELSE',
    'true': 'BOOLEAN',
    'false': 'BOOLEAN'
}

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
        if t.type == 'BOOLEAN':
            t.value = True if t.value == 'true' else False
    return t

# specific IDs for print and readLine to preserve their name as ID tokens
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

# numeric tokens
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
    t.type = 'BOOLEAN'
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value
    return t

def t_CHARACTER(t):
    r'\'([^\\\n]|(\\.))\''
    t.value = t.value[1:-1]
    return t

# ignore spaces and tabs
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # print lex error (also recorded later)
    print(f"[LEX ERROR] Caracter ilegal: '{t.value[0]}' en linea {t.lexer.lineno}")
    t.lexer.skip(1)

# build lexer
lexer = lex.lex()

# symbol table with scopes
tabla_simbolos = {"scopes": [ {} ]}

def abrir_scope():
    tabla_simbolos["scopes"].append({})

def cerrar_scope():
    if len(tabla_simbolos["scopes"]) > 1:
        tabla_simbolos["scopes"].pop()

def agregar_variable(nombre, tipo):
    scope = tabla_simbolos["scopes"][-1]
    if nombre in scope:
        semantic_errors.append(f"[SEM ERROR] Variable '{nombre}' ya declarada en este ámbito")
    else:
        scope[nombre] = tipo

def buscar_variable(nombre):
    for s in reversed(tabla_simbolos["scopes"]):
        if nombre in s:
            return s[nombre]
    return None

# type helpers
tipos_numericos = {"Int", "Float", "Double"}
tipos_booleanos = {"Bool"}
tipos_textuales = {"String", "Character"}

def tipo_binop(op, t1, t2):
    if t1 == "Unknown" or t2 == "Unknown":
        return "Unknown"
    if op in ("<","<=",">=",">","==","!="):
        return "Bool"
    if op in ("&&","||"):
        if t1 == t2 == "Bool":
            return "Bool"
        semantic_errors.append(f"[SEM ERROR] Operación lógica inválida: {t1} {op} {t2}")
        return "Unknown"
    if op in ("+","-","*","/","%"):
        if t1 in tipos_numericos and t2 in tipos_numericos:
            if "Double" in (t1,t2):
                return "Double"
            if "Float" in (t1,t2):
                return "Float"
            return "Int"
        if op == "+" and t1 == t2 == "String":
            return "String"
    semantic_errors.append(f"[SEM ERROR] Tipos incompatibles: {t1} {op} {t2}")
    return "Unknown"

def get_tipo(expr):
    if expr is None:
        return "Unknown"
    if isinstance(expr, tuple):
        kind = expr[0]
        if kind == 'literal':
            return expr[1]
        if kind == 'id':
            return expr[2]
        if kind == 'binop':
            return expr[4]
        if kind in ('not','postfix_unwrap','uminus'):
            return expr[2]
        if kind in ('lambda','lambda_simple'):
            return expr[3]
        if kind == 'dict':
            return expr[2]
        if kind == 'list':
            return expr[2]
        if kind == 'range':
            return expr[3]
    return "Unknown"

# operator precedence
precedence = (
    ('left','OR'),
    ('left','AND'),
    ('left','EQ','NE'),
    ('left','LT','LE','GT','GE'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE','MOD'),
    ('right','NOT'),
    ('right','UMINUS'),
)

# errors collectors
parse_errors = []
semantic_errors = []
#gramatica

# program & statements
def p_program(p):
    "program : statements"
    p[0] = ('program', p[1])

def p_statements_multiple(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    "statements : statement"
    p[0] = [p[1]]

# statement variants
def p_statement(p):
    """statement : decl_stmt optional_semicolon
                 | expr_stmt optional_semicolon
                 | for_stmt
                 | if_stmt
                 | block
                 | SEMICOLON"""
    if p[1] == ';':
        p[0] = ('empty',)
    else:
        p[0] = p[1]

def p_optional_semicolon(p):
    """optional_semicolon : SEMICOLON
                          | """
    pass

# declaration: let ID [: type] = expression
def p_decl_stmt(p):
    """decl_stmt : LET ID decl_type ASSIGN expression"""
    nombre = p[2]
    tipo_anot = p[3]  # None or ('type', tipo)
    expr = p[5]
    tipo_expr = get_tipo(expr)
    tipo_final = tipo_expr
    if tipo_anot is not None:
        anot = tipo_anot[1]
        if anot != tipo_expr and tipo_expr != "Unknown":
            semantic_errors.append(f"[SEM ERROR] Asignación: tipo anotado '{anot}' != tipo expresión '{tipo_expr}'")
        tipo_final = anot
    agregar_variable(nombre, tipo_final)
    p[0] = ('let_decl', nombre, tipo_final, expr)

def p_decl_type(p):
    """decl_type : COLON type
                 | """
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = ('type', p[2])

# simple type, array type, dict type (as annotation)
def p_type_basic(p):
    "type : ID"
    p[0] = p[1]

def p_type_array(p):
    "type : LBRACKET type RBRACKET"
    p[0] = f"[{p[2]}]"

def p_type_dict(p):
    "type : LBRACKET type COLON type RBRACKET"
    p[0] = f"[{p[2]}:{p[4]}]"

# block opens a new scope
def p_block(p):
    "block : LBRACE block_enter statements RBRACE"
    contenido = p[3]
    cerrar_scope()
    p[0] = ('block', contenido)

def p_block_enter(p):
    "block_enter :"
    abrir_scope()

# for-in
def p_for_stmt(p):
    "for_stmt : FOR ID IN expression block"
    agregar_variable(p[2], "Int")
    p[0] = ('for', p[2], p[4], p[5])

def p_if_stmt(p):
    """if_stmt : IF expression block
               | IF expression block ELSE block"""
    if len(p) == 4:
       
        p[0] = ('if', p[2], p[3], None)
    else:
        
        p[0] = ('if', p[2], p[3], p[5])


# expr statement (call or expression)
def p_expr_stmt(p):
    """expr_stmt : call_expr
                 | expression"""
    p[0] = p[1]

def p_call_expr(p):
    "call_expr : ID LPAREN arg_list RPAREN"
    func = p[1]
    args = p[3]
    if func == 'print':
        p[0] = ('print', args)
    elif func == 'readLine':
        p[0] = ('readLine', ('literal','String','String'))
    else:
        p[0] = ('call', func, args)

def p_arg_list(p):
    """arg_list : expression
                | arg_list COMMA expression
                | """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


# list/dict 


def p_empty(p):
    "empty :"
    p[0] = None

def p_bracket_item_kv(p):
    "bracket_item : expression COLON expression"
    p[0] = ('kv', p[1], p[3])

def p_bracket_item_expr(p):
    "bracket_item : expression"
    p[0] = ('expr', p[1])

def p_bracket_items_recursive(p):
    "bracket_items : bracket_items COMMA bracket_item"
    p[0] = p[1] + [p[3]]

def p_bracket_items_single(p):
    "bracket_items : bracket_item"
    p[0] = [p[1]]

def p_bracket_items_empty(p):
    "bracket_items : empty"
    p[0] = []

def p_expression_bracket(p):
    "expression : LBRACKET bracket_items RBRACKET"
    items = p[2]
    if not items:
        p[0] = ('list', [], 'List')
        return

    is_all_kv = all(it[0] == 'kv' for it in items)
    is_any_kv = any(it[0] == 'kv' for it in items)

    if is_all_kv:
        tkey = get_tipo(items[0][1])
        tval = get_tipo(items[0][2])
        for it in items:
            k = it[1]; v = it[2]
            if get_tipo(k) != tkey:
                semantic_errors.append(f"[SEM ERROR] Clave de diccionario incompatible: {get_tipo(k)} != {tkey}")
            if get_tipo(v) != tval:
                semantic_errors.append(f"[SEM ERROR] Valor de diccionario incompatible: {get_tipo(v)} != {tval}")
        p[0] = ('dict', items, f"Dictionary({tkey},{tval})")
        return
    elif is_any_kv:
        semantic_errors.append("[SEM ERROR] Mezcla de pares y elementos en literal de corchetes no permitida (usar solo lista o diccionario)")
        p[0] = ('mixed_bracket', items, "Mixed")
        return
    else:
        exprs = [it[1] for it in items]
        p[0] = ('list', exprs, 'List')
        return

# LAMBDA: (x,y) -> expr   o  x -> expr
def p_expression_lambda_paren(p):
    "expression : LPAREN params RPAREN LAMBDA_IN expression"
    params = p[2]
    abrir_scope()
    for param in params:
        agregar_variable(param, "Unknown")
    cuerpo = p[5]
    tipo_retorno = get_tipo(cuerpo)
    cerrar_scope()
    p[0] = ('lambda', params, cuerpo, f"Lambda({tipo_retorno})")

def p_expression_lambda_simple(p):
    "expression : ID LAMBDA_IN expression"
    param = p[1]
    abrir_scope()
    agregar_variable(param, "Unknown")
    cuerpo = p[3]
    tipo_retorno = get_tipo(cuerpo)
    cerrar_scope()
    p[0] = ('lambda_simple', [param], cuerpo, f"Lambda({tipo_retorno})")

def p_params(p):
    """params : ID
              | params COMMA ID
              | """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# BINOPS y rango
def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression"""
    left = p[1]; right = p[3]; op = p[2]
    tipo_res = tipo_binop(op, get_tipo(left), get_tipo(right))
    p[0] = ('binop', op, left, right, tipo_res)

def p_expression_range(p):
    "expression : expression DOTDOTDOT expression"
    t1 = get_tipo(p[1]); t2 = get_tipo(p[3])
    if t1 in tipos_numericos and t2 in tipos_numericos:
        tipo = "Range"
    else:
        tipo = "Unknown"
    p[0] = ('range', p[1], p[3], tipo)

# NOT prefix and postfix unwrap
def p_expression_not(p):
    "expression : NOT expression"
    if get_tipo(p[2]) != "Bool":
        semantic_errors.append(f"[SEM ERROR] '!' (prefijo) solo aplica a Bool, no a {get_tipo(p[2])}")
    p[0] = ('not', p[2], "Bool")

def p_expression_postfix_unwrap(p):
    "expression : expression NOT"
    t = get_tipo(p[1])
    if t == "Unknown":
        semantic_errors.append(f"[SEM ERROR] Force unwrap '!' aplicado a valor desconocido")
    p[0] = ('postfix_unwrap', p[1], t)

def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"
    if get_tipo(p[2]) not in tipos_numericos:
        semantic_errors.append(f"[SEM ERROR] '-' unario solo aplica a números")
    p[0] = ('uminus', p[2], get_tipo(p[2]))

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_literal(p):
    """expression : INTEGER
                  | FLOAT
                  | DOUBLE
                  | BOOLEAN
                  | STRING
                  | CHARACTER"""
    tipo_map = {
        "INTEGER":"Int","FLOAT":"Float","DOUBLE":"Double",
        "BOOLEAN":"Bool","STRING":"String","CHARACTER":"Character"
    }
    tipo = tipo_map[p.slice[1].type]
    p[0] = ('literal', tipo, tipo)

def p_expression_id(p):
    "expression : ID"
    nombre = p[1]
    if nombre == 'print':
        p[0] = ('id', nombre, 'BuiltInFunction')
        return
    tipo = buscar_variable(nombre)
    if tipo is None:
        semantic_errors.append(f"[SEM ERROR] Variable '{nombre}' usada sin declarar")
        p[0] = ('id', nombre, "Unknown")
    else:
        p[0] = ('id', nombre, tipo)

# error handler
def p_error(p):
    global parse_errors
    if p:
        parse_errors.append(f"[SYN ERROR] Token inesperado '{p.value}' (tipo {p.type}) en línea {p.lineno}")
    else:
        parse_errors.append("[SYN ERROR] EOF inesperado: estructura incompleta")

parser = yacc.yacc()


def ejecutar_y_generalog(codigo_fuente: str, parser_obj=parser, usuario_git="AymanElS4", carpeta_base="Proyecto-LP-Analizador"):
    """
    codigo_fuente: path a archivo o string con codigo
    genera logs: lexico, sintactico+semantico
    """
    global parse_errors, semantic_errors, tabla_simbolos
    parse_errors = []
    semantic_errors = []
    tabla_simbolos = {"scopes": [ {} ]}

    # leer archivo
    if os.path.exists(codigo_fuente):
        try:
            with open(codigo_fuente, "r", encoding="utf-8") as f:
                codigo = f.read()
        except Exception as e:
            parse_errors.append(f"[SYN ERROR] No se pudo leer el archivo: {e}")
            codigo = ""
    else:
        codigo = codigo_fuente

    # crear carpeta logs
    carpeta_logs = os.path.join(carpeta_base, "logs")
    os.makedirs(carpeta_logs, exist_ok=True)

    fecha_hora = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # --- LOG LEXICO ---
    try:
        lx = lex.lex()
        lx.input(codigo)
        lex_log = os.path.join(carpeta_logs, f"lexico-{usuario_git}-{fecha_hora}.txt")
        with open(lex_log, "w", encoding="utf-8") as lf:
            while True:
                tok = lx.token()
                if not tok: break
                lf.write(f"Línea {tok.lineno}: {tok.type} -> {tok.value}\n")
    except Exception as e:
        parse_errors.append(f"[SYN ERROR] Error tokenizando: {e}")


    try:
        lexer_local = lex.lex()
        parser_obj.parse(codigo, lexer=lexer_local)
    except Exception as e:
        parse_errors.append(f"[SYN ERROR] Excepción durante el parseo: {str(e)}")

    nombre_archivo = f"sintactico_semantico-{usuario_git}-{fecha_hora}.txt"
    ruta_log = os.path.join(carpeta_logs, nombre_archivo)

    with open(ruta_log, "w", encoding="utf-8") as f:
        f.write("Log de análisis sintáctico + semántico\n")
        f.write(f"Usuario Git: {usuario_git}\n")
        f.write(f"Fecha/Hora: {fecha_hora}\n")
        f.write("=------------------=\n\n")

        if parse_errors:
            f.write("Errores sintácticos:\n")
            for err in parse_errors:
                f.write(err + "\n")
            f.write("\n")
        else:
            f.write("No se encontraron errores sintácticos.\n\n")

        if semantic_errors:
            f.write("Errores semánticos:\n")
            for err in semantic_errors:
                f.write(err + "\n")
            f.write("\n")
        else:
            f.write("No se encontraron errores semánticos.\n\n")

        # resumen tabla global
        f.write("= Tabla de símbolos (scope global) =\n")
        for k,v in tabla_simbolos["scopes"][0].items():
            f.write(f"{k} : {v}\n")

    print(f"[OK] Log generado en: {ruta_log}")
    print(f"[OK] Log léxico en: {lex_log if 'lex_log' in locals() else '(no generado)'}")
    return ruta_log

if __name__ == "__main__":
    ruta_swift = r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift"
    ejecutar_y_generalog(ruta_swift, usuario_git="AymanElS4")
