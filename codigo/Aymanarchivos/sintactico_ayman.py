import ply.yacc as yacc
import primitivos_y_limitadores as lexmod
from primitivos_y_limitadores import tokens
import ply.lex as lex
import datetime
import os

tabla_simbolos = {
    "scopes": [
        {}  # scope global
    ]
}
#agregar nuevo scope
def agregar_variable(nombre, tipo):
    
    scope = tabla_simbolos["scopes"][-1]
    if nombre in scope:
        semantic_errors.append(
            f"[SEM ERROR] Variable '{nombre}' ya declarada en este ámbito"
        )
    else:
        scope[nombre] = tipo
# Buscar variable en scopes desde el más interno al más externo
def buscar_variable(nombre):
    
    for scope in reversed(tabla_simbolos["scopes"]):
        if nombre in scope:
            return scope[nombre]
    return None  # no existe

def get_tipo(expr):
    if isinstance(expr, tuple):
        return expr[-1]   # último elemento siempre es tipo
    return "Unknown"

#tipos
tipos_numericos = {"Int", "Float", "Double"}
tipos_booleanos = {"Bool"}
tipos_textuales = {"String", "Character"}

def tipo_binop(op, tipo1, tipo2):
    if tipo1 == "Unknown" or tipo2 == "Unknown":
        return "Unknown"

    # comparaciones
    if op in ("<", "<=", ">", ">=", "==", "!="):
        return "Bool"

    # lógicas
    if op in ("&&", "||"):
        if tipo1 == tipo2 == "Bool":
            return "Bool"
        semantic_errors.append(f"[SEM ERROR] Operación lógica inválida: {tipo1} {op} {tipo2}")
        return "Unknown"

    # numéricas
    if op in ("+", "-", "*", "/"):
        if tipo1 in tipos_numericos and tipo2 in tipos_numericos:
            if "Double" in (tipo1, tipo2):
                return "Double"
            if "Float" in (tipo1, tipo2):
                return "Float"
            return "Int"

        if op == "+" and tipo1 == tipo2 == "String":
            return "String"

    semantic_errors.append(f"[SEM ERROR] Tipos incompatibles: {tipo1} {op} {tipo2}")
    return "Unknown"


precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
)
# lista para recolectar errores sintácticos durante el parseo
parse_errors = []
semantic_errors = []


def p_program(p): #expresion general del programa
    """program : statements"""
    p[0] = ('program', p[1])

def p_statements_multiple(p): #varias expresiones/statements
    """statements : statements statement"""
    p[0] = p[1] + [p[2]]

def p_statements_single(p): #una sola expresión/statement
    """statements : statement"""
    p[0] = [p[1]]

def p_statement(p): #expresion cualquiera, 
    """statement : decl_stmt
                 | expr_stmt
                 | for_stmt
                 | block
                 | SEMICOLON"""
    if p[1] == ';':
        p[0] = ('empty',)
    else:
        p[0] = p[1]

# declaración let: let id = expression [;]
def p_decl_stmt(p):
    """decl_stmt : LET ID ASSIGN expression optional_semicolon"""
    nombre = p[2]
    expr = p[4]
    tipo_expr = expr[1]
    agregar_variable(nombre, tipo_expr)
    p[0] = ("let_decl", nombre, expr)

def p_decl_stmt_incompleto(p):
    """decl_stmt : LET ID ASSIGN"""
    semantic_errors.append("[SEM ERROR] Declaración incompleta: falta expresión en let")
    p[0] = ("let_incompleto", p[2])

def p_decl_stmt_faltatipo(p):
    """decl_stmt : LET ID"""
    semantic_errors.append("[SEM ERROR] Falta tipo o valor en declaración")
    p[0] = ("let_invalido", p[2])

def p_optional_semicolon(p):
    """optional_semicolon : SEMICOLON
                          | """
    pass

# bloque { statements }
def p_block(p):
    """block : LBRACE statements RBRACE"""
    tabla_simbolos["scopes"].append({})
    
    contenido = p[2]
    tabla_simbolos["scopes"].pop()
    p[0] = ("block", contenido)

# for-in: for ID in expression block
def p_for_stmt(p):
    """for_stmt : FOR ID IN expression block"""
    tabla_simbolos["scopes"].append({})
    agregar_variable(p[2], "Int")
    contenido = p[5]
    tabla_simbolos["scopes"].pop()
    p[0] = ("for", p[2], p[4], contenido)

  

# print(...) or input(...)
def p_expr_stmt_print(p):
    """expr_stmt : ID LPAREN arg_list RPAREN optional_semicolon"""
    func = p[1]

    if func == "print":
        p[0] = ("print", p[3])

    elif func == "readLine":
        p[0] = ("readLine", "String")  # readLine() → String

    else:
        p[0] = ("call", func, p[3])

#args de funciones: expression (, expression)*
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

# expresiones: lambdas, diccionarios, operaciones, paréntesis, literales, ids


def p_expression_lambda(p):
    """expression : LPAREN params RPAREN LAMBDA_IN expression"""
    params = p[2]            # lista de IDs
    cuerpo = p[5]           # expresión del cuerpo
    tipo_retorno = cuerpo[1] if isinstance(cuerpo, tuple) else "Unknown"
    lambda_type = f"Lambda({tipo_retorno})"
    p[0] = ("lambda", params, cuerpo, lambda_type)

def p_expression_lambda_simple(p):
    """expression : ID LAMBDA_IN expression"""
    param = p[1]
    cuerpo = p[3]
    tipo_retorno = cuerpo[1] if isinstance(cuerpo, tuple) else "Unknown"
    lambda_type = f"Lambda({tipo_retorno})"
    p[0] = ("lambda_simple", [param], cuerpo, lambda_type)

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

# diccionario: [ (expression : expression) ( , expr:expr )* ]
def p_expression_dict(p):
    """expression : LBRACKET dict_items RBRACKET"""
    items = p[2]
    if len(items) == 0:
        p[0] = ("dict", [], "Dictionary(Empty)")
        return

    tkey = items[0][1][1]
    tval = items[0][2][1]

    for (_, k, v) in items:
        if k[1] != tkey:
            semantic_errors.append(f"[SEM ERROR] Clave de diccionario incompatible: {k[1]} != {tkey}")
        if v[1] != tval:
            semantic_errors.append(f"[SEM ERROR] Valor de diccionario incompatible: {v[1]} != {tval}")

    p[0] = ("dict", items, f"Dictionary({tkey},{tval})")

def p_dict_items_multiple(p):
    """dict_items : dict_items COMMA dict_item"""
    p[0] = p[1] + [p[3]]

def p_dict_items_single(p):
    """dict_items : dict_item
                  | """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]]

def p_dict_item(p):
    """dict_item : expression COLON expression"""
    p[0] = ('kv', p[1], p[3])

# operaciones binarias y literales
#poner los tokens de igual-mayor, menor igual, etc confunde demasiado la verdad
def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression"""
    tipo_res = tipo_binop(p[2], get_tipo(p[1]), get_tipo(p[3]))
    p[0] = ("binop", p[2], p[1], p[3], tipo_res)

    


def p_expression_not(p):
    "expression : NOT expression"
    if p[2][1] != "Bool":
        semantic_errors.append(f"[SEM ERROR] '!' solo aplica a Bool, no a {p[2][1]}")
    p[0] = ('not', p[2], "Bool")

def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"
    if p[2][1] not in tipos_numericos:
        semantic_errors.append(f"[SEM ERROR] '-' unario solo aplica a números")
    p[0] = ('uminus', p[2], p[2][1])

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
        "INTEGER": "Int",
        "FLOAT": "Float",
        "DOUBLE": "Double",
        "BOOLEAN": "Bool",
        "STRING": "String",
        "CHARACTER": "Character"
    }

    tipo = tipo_map[p.slice[1].type]
    p[0] = ('literal', tipo, tipo)

def p_expression_id(p):
    "expression : ID"
    tipo = buscar_variable(p[1])
    if tipo is None:
        semantic_errors.append(f"[SEM ERROR] Variable '{p[1]}' usada sin declarar")
        p[0] = ("id", p[1], "Unknown")
    else:
        p[0] = ("id", p[1], tipo)


# manejo de errores sintácticos


def p_error(p):
    global parse_errors
    if p:
        parse_errors.append(f"[SYN ERROR] Token inesperado '{p.value}' en línea {p.lineno}")
        parser.errok()
    else:
        parse_errors.append("[SYN ERROR] EOF inesperado: estructura incompleta")

parser = yacc.yacc()

def ejecutar_y_generalog(codigo_fuente: str, parser_obj=parser, usuario_git="AymanElS4", carpeta_base="Proyecto-LP-Analizador"):
    global parse_errors, semantic_errors
    parse_errors = []
    semantic_errors = []

    lexer = lex.lex(module=lexmod)

    try:
        # parsea; forzar que use el lexer/tokenizador cargado en primitivos_y_limitadores
        parser_obj.parse(codigo_fuente)
    except Exception as e:
        parse_errors.append(f"[SYN ERROR] Excepción durante el parseo: {str(e)}")

    # crear carpeta logs
    carpeta_logs = os.path.join(carpeta_base, "logs")
    os.makedirs(carpeta_logs, exist_ok=True)

    fecha_hora = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
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

        # opcional: resumen de tabla de símbolos (scope global)
        f.write("= Tabla de símbolos (scope global) =\n")
        for k, v in tabla_simbolos["scopes"][0].items():
            f.write(f"{k} : {v}\n")

    print(f"[OK] Log generado en: {ruta_log}")
    return ruta_log

with open(r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift","r",encoding="utf-8") as f:
   swiftcod = f.read()
ruta = ejecutar_y_generalog(codigo_fuente=swiftcod, parser_obj=parser, usuario_git="AymanElS4")
print("Ruta log:", ruta)




