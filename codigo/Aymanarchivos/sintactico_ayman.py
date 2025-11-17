import ply.yacc as yacc
from primitivos_y_limitadores import tokens
import ply.lex as lex
import datetime
import os

tabla_simbolos = {
    "variables": {}
}
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

def p_program(p):
    """program : statements"""
    p[0] = ('program', p[1])

def p_statements_multiple(p):
    """statements : statements statement"""
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    """statements : statement"""
    p[0] = [p[1]]

def p_statement(p):
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
    tipo_expr = p[4][1]  # el tipo viene como ('expr', tipo)

    # ---- SEMÁNTICA ----
    if nombre in tabla_simbolos["variables"]:
        semantic_errors.append(
            f"[SEM ERROR] La variable '{nombre}' ya está declarada"
        )
    else:
        tabla_simbolos["variables"][nombre] = tipo_expr

    p[0] = ('let_decl', nombre, p[4])

def p_optional_semicolon(p):
    """optional_semicolon : SEMICOLON
                          | """
    pass

# bloque { statements }
def p_block(p):
    """block : LBRACE statements RBRACE"""
    p[0] = ('block', p[2])

# for-in: for ID in expression block
def p_for_stmt(p):
    """for_stmt : FOR ID IN expression block"""
    p[0] = ('for_in', p[2], p[4], p[5])

# print(...) or input(...)
def p_expr_stmt_print(p):
    """expr_stmt : ID LPAREN arg_list RPAREN optional_semicolon"""
    # si p[1]=='print' manejamos impresión, si 'input' ingreso
    if p[1] == 'print':
        p[0] = ('print', p[3])
    elif p[1] == 'input':
        p[0] = ('input', None)
    else:
        p[0] = ('call', p[1], p[3])

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
    p[0] = ('lambda', p[2], p[5])

def p_expression_lambda_simple(p):
    """expression : ID LAMBDA_IN expression"""
    # forma simplificada: x -> expr
    p[0] = ('lambda_simple', p[1], p[3])

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
    p[0] = ('dict', p[2])

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
    tipo1 = p[1][1]
    tipo2 = p[3][1]

    #tipos supersimples
    if tipo1 != tipo2:
        semantic_errors.append(
            f"[SEM ERROR] Tipos incompatibles: {tipo1} {p[2]} {tipo2}"
        )

    p[0] = ('binop', p[2], p[1], p[3], tipo1)


def p_expression_not(p):
    "expression : NOT expression"
    p[0] = ('not', p[2],"Bool" )

def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"
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
    nombre = p[1]

    if nombre not in tabla_simbolos["variables"]:
        semantic_errors.append(
            f"[SEM ERROR] Variable '{nombre}' usada sin declarar"
        )
        p[0] = ('id', nombre, "Unknown")
    else:
        p[0] = ('id', nombre, tabla_simbolos["variables"][nombre])





# manejo de errores sintácticos



def p_error(p):
    global parse_errors
    if p:
        msg = f"[SYN ERROR] Token inesperado '{p.value}' (tipo {p.type}) en línea {p.lineno}"
        parse_errors.append(msg)
        # intentar recuperar: saltar token
        parser.errok()
    else:
        msg = "[SYN ERROR] Fin de archivo inesperado (EOF) - posible estructura incompleta"
        parse_errors.append(msg)

parser = yacc.yacc()

def ejecutar_y_generalog(codigo_fuente, parser, usuario_git="AymanElS4"):
    global parse_errors, semantic_errors

    parse_errors.clear()
    semantic_errors.clear()

    try:
        parser.parse(codigo_fuente)
    except Exception as e:
        parse_errors.append(f"[SYN ERROR] Excepción durante el parseo: {str(e)}")

    carpeta_logs = os.path.join("Proyecto-LP-Analizador", "logs")
    fecha_hora = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    nombre_archivo = f"sintactico-{usuario_git}-{fecha_hora}.txt"
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

        if semantic_errors:
            f.write("Errores semánticos:\n")
            for err in semantic_errors:
                f.write(err + "\n")
            f.write("\n")

        if not parse_errors and not semantic_errors:
            f.write("No se encontraron errores.\n")

    print(f"[OK] Log generado en: {ruta_log}")
    return ruta_log

with open(r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift", "r", encoding="utf-8") as f:
    swiftcod = f.read()

ejecutar_y_generalog(
    codigo_fuente=swiftcod,
    parser=parser,
    usuario_git="AymanElS4"
)




