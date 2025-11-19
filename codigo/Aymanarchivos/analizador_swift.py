import ply.lex as lex
import ply.yacc as yacc
import datetime
import os

#lexer (el otro funciona, pero me he visto en la necesidad de agregar a cada analizador uno, para no tener que ver qeu cambios causan errores)

tabla_simbolos = {"scopes":[{}]}
tabla_simbolos["scopes"][0]["print"] = "BuiltInFunction"
tabla_simbolos["scopes"][0]["readLine"] = "BuiltInFunction"
semantic_errors = []

tokens = [
    'INTEGER','FLOAT','DOUBLE','BOOLEAN','STRING','CHARACTER',
    'LPAREN','RPAREN','LBRACE','RBRACE','LBRACKET','RBRACKET',
    'COMMA','SEMICOLON','COLON',
    'LET','FOR','IN','IF','ELSE',
    'ID','ASSIGN',
    'PLUS','MINUS','TIMES','DIVIDE','MOD',
    'EQ','NE','LT','LE','GT','GE',
    'AND','OR','NOT',
    'LAMBDA_IN', 
    'DOTDOTDOT'
]

# tokens simples
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

reserved = {
    'let':'LET',
    'for':'FOR',
    'in':'IN',
    'if':'IF',
    'else':'ELSE',
    'true':'BOOLEAN',
    'false':'BOOLEAN',
}

tipos_nativos = {"Int","Float","Double","Bool","String","Character","Any"}

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
        if t.type == 'BOOLEAN':
            t.value = True if t.value == 'true' else False
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value
    return t

def t_CHARACTER(t):
    r'\'([^\\\n]|(\\.))\''
    t.value = t.value[1:-1]
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"[LEX ERROR] Caracter ilegal: '{t.value[0]}' en linea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
#semantico
def abrir_scope():
    tabla_simbolos["scopes"].append({})

def cerrar_scope():
    if len(tabla_simbolos["scopes"])>1:
        tabla_simbolos["scopes"].pop()

def agregar_variable(nombre, tipo):
    scope = tabla_simbolos["scopes"][-1]
    if nombre in scope:
        semantic_errors.append(f"[SEM ERROR] Variable '{nombre}' ya declarada en este scope")
    else:
        scope[nombre] = tipo

def buscar_variable(nombre):
    for s in reversed(tabla_simbolos["scopes"]):
        if nombre in s:
            return s[nombre]
    return None
#divide la tabla con todos los tipos
tipos_numericos = {"Int","Float","Double"}
tipos_booleanos = {"Bool"}
tipos_textuales = {"String","Character"}

def tipo_binop(op, t1, t2):
    if t1=="Unknown" or t2=="Unknown":
        return "Unknown"
    if op in ("<","<=",">=",">","==","!="):
        return "Bool"
    if op in ("&&","||"):
        if t1==t2=="Bool":
            return "Bool"
        semantic_errors.append(f"[SEM ERROR] Operación lógica inválida: {t1} {op} {t2}")
        return "Unknown"
    if op in ("+","-","*","/","%"):
        if t1 in tipos_numericos and t2 in tipos_numericos:
            if "Double" in (t1,t2): return "Double"
            if "Float" in (t1,t2): return "Float"
            return "Int"
        if op=="+" and t1==t2=="String":
            return "String"
    semantic_errors.append(f"[SEM ERROR] Tipos incompatibles: {t1} {op} {t2}")
    return "Unknown"

def get_tipo(expr):
    if expr is None: return "Unknown"
    if isinstance(expr, tuple):
        kind = expr[0]
        if kind=="literal": return expr[1]
        if kind=="id": return expr[2]
        if kind=="binop": return expr[4]
        if kind == 'logic':
            return "Bool"
        if kind == 'cmp':
            return "Bool"
        if kind in ("lambda","lambda_simple"): return expr[3]
        if kind=="dict": return expr[2]
        if kind=="list": return expr[2]
        if kind=="range": return expr[3]
        if kind=="call": return expr[3]
    return "Unknown"

def type_to_string(struct_type):
    """Convierte la estructura de tipo ('id', 'Int') o ('array','T') o ('dict','K','V') a una cadena legible."""
    if struct_type is None:
        return "Unknown"
    if isinstance(struct_type, tuple):
        if struct_type[0] == 'id':
            return struct_type[1]
        if struct_type[0] == 'array':
            return f"[{struct_type[1]}]"
        if struct_type[0] == 'dict':
            return f"[{struct_type[1]}:{struct_type[2]}]"
    return str(struct_type)
#parser

precedence = (
    ('left','OR'),
    ('left','AND'),
    ('left','EQ','NE'),
    ('left','LT','LE','GT','GE'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE','MOD'),
    ('right','NOT'),
)

parse_errors = []
# variable temporal para pasar la variable del for al block_enter
pending_for_var = None

def p_program(p):
    "program : statements"
    p[0] = ('program',p[1])

def p_statements_multiple(p):
    "statements : statements statement"
    p[0] = p[1]+[p[2]]

def p_statements_single(p):
    "statements : statement"
    p[0] = [p[1]]

def p_statement(p):
    """statement : decl_stmt
                 | expr_stmt
                 | for_stmt
                 | SEMICOLON"""
    if p[1]==';':
        p[0] = ('empty',)
    else:
        p[0]=p[1]

# ---------------- LET ----------------
def p_decl_stmt(p):
    '''decl_stmt : LET ID decl_type ASSIGN expression
                 | LET ID ASSIGN expression'''
    nombre = p[2]
    if len(p) == 5:
        # let x = expr
        tipo_anot = None
        expr = p[4]
    else:
        # let x: Type = expr
        tipo_anot = p[3]
        expr = p[5]
    if expr is None:
        semantic_errors.append(f"[SEM ERROR] Variable '{nombre}' declarada sin valor")
        tipo_final = "Unknown"
    else:
        tipo_expr = get_tipo(expr)
        tipo_final = tipo_expr

        if tipo_anot:
            struct = tipo_anot[1]
          
            if isinstance(struct, tuple) and struct[0] == 'dict' and isinstance(expr, tuple) and expr[0] == 'dict':
                tkey = struct[1]
                tval = struct[2]
                allowed = [
                    ("String","Int"),
                    ("String","Any"),
                    ("Any","Any")
                ]
                if (tkey, tval) not in allowed:
                    semantic_errors.append(f"[SEM ERROR] Tipo de diccionario no permitido: [{tkey}:{tval}]")
                items = expr[1]
                for it in items:
                    k = it[1]; v = it[2]
                    tk = get_tipo(k); tv = get_tipo(v)
                    if tkey != "Any" and tk != tkey:
                        semantic_errors.append(f"[SEM ERROR] Tipo de clave incompatible: '{tk}' != '{tkey}'")
                    if tval != "Any" and tv != tval:
                        semantic_errors.append(f"[SEM ERROR] Tipo de valor incompatible: '{tv}' != '{tval}'")
                tipo_final = f"Dictionary({tkey},{tval})"
            else:
         
                tipo_final = type_to_string(struct)
    
    

    agregar_variable(nombre, tipo_final)
    p[0] = ('let_decl', nombre, tipo_final, expr)

def p_decl_stmt_incomplete_assign(p):
    "decl_stmt : LET ID ASSIGN"
    nombre = p[2]
    semantic_errors.append(f"[SEM ERROR] Declaración incompleta: 'let {nombre} =' sin expresión")
   
    agregar_variable(nombre, "Unknown")
    p[0] = ('let_incomplete', nombre)

def p_decl_stmt_onlyid(p):
    "decl_stmt : LET ID"
    nombre = p[2]
    semantic_errors.append(f"[SEM ERROR] Declaración incompleta: 'let {nombre}' sin tipo ni asignación")
    agregar_variable(nombre, "Unknown")
    p[0] = ('let_invalid', nombre)


def p_decl_type(p):
    """decl_type : COLON ID
                 | """
    if len(p)==1:
        p[0] = None
    else:
        tipo = p[2]
        if tipo not in tipos_nativos:
            semantic_errors.append(f"[SEM ERROR] Tipo desconocido '{tipo}'")
        p[0] = ('type', tipo)

# ---------------- FOR-IN ----------------
def p_for_stmt(p):
    "for_stmt : FOR ID IN expression block"
    # declaración del iterador para evitar "i usada sin declarar".
    # Lo registramos en el scope *actual* (evita falso negativo dentro del bloque).
    agregar_variable(p[2], "Int")
    p[0] = ('for', p[2], p[4], p[5])



# ---------------- BLOCK ----------------
def p_block(p):
    "block : LBRACE block_enter statements RBRACE"
    cerrar_scope()
    p[0] = ('block',p[3])

def p_block_enter(p):
    "block_enter :"
    abrir_scope()

# ---------------- EXPRESSIONS ----------------
def p_expr_stmt(p):
    """expr_stmt : expression"""
    p[0] = p[1]

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  """
    left = p[1]; right = p[3]; op = p[2]
    tipo_res = tipo_binop(op,get_tipo(left),get_tipo(right))
    p[0] = ('binop',op,left,right,tipo_res)

def p_expression_compare(p):
    """expression : expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression"""
    p[0] = ('cmp', p[1], p[2], p[3], 'Bool')

def p_expression_logic_binary(p):
    """expression : expression AND expression
                  | expression OR expression"""
    p[0] = ('logic', p[1], p[2], p[3], 'Bool')

def p_expression_range(p):
    "expression : expression DOTDOTDOT expression"
    t1 = get_tipo(p[1])
    t2 = get_tipo(p[3])
    # si ambos son números, tratamos el rango como tipo Range o Int (según prefieras)
    if t1 in tipos_numericos and t2 in tipos_numericos:
        tipo = "Range"   # marcador; puedes inferir Int si quieres
    else:
        tipo = "Unknown"
    p[0] = ('range', p[1], p[3], tipo)


def p_expression_literal(p):
    """expression : INTEGER
                  | FLOAT
                  | BOOLEAN
                  | STRING
                  | CHARACTER"""
    tipo_map = {"INTEGER":"Int","FLOAT":"Float","BOOLEAN":"Bool","STRING":"String","CHARACTER":"Character"}
    tipo = tipo_map[p.slice[1].type]
    p[0] = ('literal',tipo,tipo)

def p_expression_id(p):
    "expression : ID"
    nombre = p[1]
    tipo = buscar_variable(nombre)
    if tipo is None:
        semantic_errors.append(f"[SEM ERROR] Variable '{nombre}' usada sin declarar")
        tipo="Unknown"
    p[0]=('id',nombre,tipo)

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0]=p[2]

# ---------------- LAMBDA SIMPLE ----------------
def p_expression_lambda(p):
    "expression : ID LAMBDA_IN expression"
    param = p[1]
    abrir_scope()
    agregar_variable(param,"Unknown")
    cuerpo = p[3]
    tipo_ret = get_tipo(cuerpo)
    cerrar_scope()
    p[0] = ('lambda_simple',[param],cuerpo,tipo_ret)


# ---------------- DICTIONARIES ----------------
def p_expression_bracket(p):
    "expression : LBRACKET bracket_items RBRACKET"
    items = p[2]
    if not items:
        p[0] = ('list', [], 'List')
        return

    is_all_kv = all(it[0]=='kv' for it in items)
    is_any_kv = any(it[0]=='kv' for it in items)

    if is_all_kv:
        # infer types
        tkey = get_tipo(items[0][1])
        tval = get_tipo(items[0][2])

        # VALIDAR CON TIPOS NATIVOS
        if tkey not in tipos_nativos:
            semantic_errors.append(f"[SEM ERROR] Tipo de clave no permitido en Swift: {tkey}")
        if tval not in tipos_nativos:
            semantic_errors.append(f"[SEM ERROR] Tipo de valor no permitido en Swift: {tval}")

        # validate homogeneity (unless Any)
        for it in items:
            k = it[1]; v = it[2]
            if tkey != "Any" and get_tipo(k) != tkey:
                semantic_errors.append(f"[SEM ERROR] Clave de diccionario incompatible: {get_tipo(k)} != {tkey}")
            if tval != "Any" and get_tipo(v) != tval:
                semantic_errors.append(f"[SEM ERROR] Valor de diccionario incompatible: {get_tipo(v)} != {tval}")

        p[0] = ('dict', items, f"Dictionary({tkey},{tval})")

    elif is_any_kv:
        semantic_errors.append("[SEM ERROR] Mezcla de pares y elementos en literal de corchetes no permitida")
        p[0] = ('mixed_bracket', items, "Mixed")

    else:
        exprs = [it[1] for it in items]
        p[0] = ('list', exprs, 'List')

def p_bracket_item_kv(p):
    "bracket_item : expression COLON expression"
    p[0] = ('kv', p[1], p[3])

def p_bracket_item_expr(p):
    "bracket_item : expression"
    p[0] = ('expr', p[1])

def p_bracket_items_multiple(p):
    "bracket_items : bracket_items COMMA bracket_item"
    p[0] = p[1] + [p[3]]

def p_bracket_items_single(p):
    "bracket_items : bracket_item"
    p[0] = [p[1]]

def p_bracket_items_empty(p):
    "bracket_items : "
    p[0] = []



# ---------------- IF-ELSE ----------------
def p_expression_if(p):
    "expression : IF expression block"
    cond = p[2]
    if get_tipo(cond)!="Bool":
        semantic_errors.append(f"[SEM ERROR] Condición no booleana en IF: {get_tipo(cond)}")
    p[0] = ('if',cond,p[3])

# ---------------- ERROR ----------------
def p_error(p):
    global parse_errors
    if p:
        parse_errors.append(f"[SYN ERROR] Token inesperado '{p.value}' (tipo {p.type}) en línea {p.lineno}")
    else:
        parse_errors.append("[SYN ERROR] EOF inesperado: estructura incompleta")

parser = yacc.yacc()
#logyejecucion

def ejecutar_y_generar_log(ruta_archivo, usuario_git="AymanElS4"):
    global parse_errors, semantic_errors, tabla_simbolos
    parse_errors = []
    semantic_errors = []
    tabla_simbolos = {"scopes":[{}]}
    tabla_simbolos["scopes"][0]["print"] = "BuiltInFunction"
    tabla_simbolos["scopes"][0]["readLine"] = "BuiltInFunction"

   

    # leer código
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo,"r",encoding="utf-8") as f:
            codigo = f.read()
    else:
        raise FileNotFoundError(f"No existe archivo: {ruta_archivo}")

    # parse
    parser.parse(codigo)

    # crear carpeta logs
    carpeta_logs = os.path.join(os.getcwd(), "Proyecto-LP-Analizador", "logs")
    os.makedirs(carpeta_logs, exist_ok=True)
    fecha_hora = datetime.datetime.now().strftime("%d%m%Y-%Hh%M")
    nombre_log = f"semantico-{usuario_git}-{fecha_hora}.txt"
    ruta_log = os.path.join(carpeta_logs,nombre_log)

    with open(ruta_log,"w",encoding="utf-8") as f:
        f.write("Log semántico Swift\n")
        f.write(f"Usuario: {usuario_git}\n")
        f.write(f"Fecha/Hora: {fecha_hora}\n\n")
        if semantic_errors:
            f.write("Errores semánticos:\n")
            for e in semantic_errors:
                f.write(e+"\n")
        else:
            f.write("No se encontraron errores semánticos.\n")
        f.write("\n= Tabla de símbolos global =\n")
        for k,v in tabla_simbolos["scopes"][0].items():
            f.write(f"{k} : {v}\n")

    print(f"[OK] Log semántico generado en: {ruta_log}")
    return ruta_log


if __name__=="__main__":
    ruta_archivo = r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift"
    ejecutar_y_generar_log(ruta_archivo)
    pass

