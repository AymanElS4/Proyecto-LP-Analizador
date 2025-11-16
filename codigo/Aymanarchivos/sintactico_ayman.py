import ply.yacc as yacc
from primitivos_y_limitadores import tokens
import ply.lex as lex
import datetime

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
    p[0] = ('let_decl', p[2], p[4])

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
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_not(p):
    "expression : NOT expression"
    p[0] = ('not', p[2])

def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = ('uminus', p[2])

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
    p[0] = ('literal', p[1])

def p_expression_id(p):
    "expression : ID"
    p[0] = ('id', p[1])



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


def test_parser_from_file(filepath, usuario_git="default"):

    lexer = lex.lex()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {filepath}")
        return

    fecha_hora = datetime.datetime.now().strftime("%d-%m-%Y-%Hh%M")
    log_name = f"Proyecto-LP-Analizador/logs/sintactico-{usuario_git}-{fecha_hora}.txt"

    with open(log_name, "w", encoding="utf-8") as log:
        log.write(f"===== LOG DE PARSER ({fecha_hora}) =====\n")

        try:
            result = parser.parse(input_text, lexer=lexer)
            log.write("Parser completado, no hay errores\n")
            log.write(f"Árbol sintáctico:\n{result}\n")
        except Exception as e:
            log.write("Error durante parseo:\n")
            log.write(str(e) + "\n")

    print(f"\nAnálisis sintáctico completado. Log guardado en: {log_name}")




