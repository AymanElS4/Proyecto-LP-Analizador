import ply.yacc as yacc
from primitivos_y_limitadores import tokens
import os
import datetime

errores_sintacticos = []
#precendencia de operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)



#programa
def p_program(p):
    '''program : program statement
              | statement'''
    pass

#print
def p_statement(p):
    '''statement : let_decl
                 | for_loop
                 | print_stmt
                 | input_stmt
                 | expr
                 | condition'''
    pass

#print
def p_print_stmt(p):
    "print_stmt : print LPAREN expr RPAREN"
    pass


#ingreso de datos
def p_input_stmt(p):
    "input_stmt : ID ASSIGN READLINE LPAREN RPAREN"
    pass

#declaracion let 
def p_let_decl(p):
    "statement : LET ID ASSIGN expr"
    pass


#expresiones aritméticas
def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr MOD expr'''
    pass


def p_expr_group(p):
    "expr : LPAREN expr RPAREN"
    pass


def p_expr_number(p):
    '''expr : NUMBER
            | FLOAT
            | STRING
            | CHARACTER
            | ID'''
    pass

#diccionarios

def p_dict(p):
    "expr : LBRACKET dict_items RBRACKET"
    pass


def p_dict_items(p):
    '''dict_items : dict_items COMMA dict_item
                  | dict_item'''
    pass


def p_dict_item(p):
    "dict_item : STRING COLON expr"
    pass


#bucles for

def p_for_loop(p):
    '''statement : FOR ID IN expr RANGE expr LBRACE program RBRACE
                 | FOR ID IN expr RANGE expr LBRACE RBRACE
                 | FOR ID IN LBRACKET dict_items RBRACKET LBRACE program RBRACE
                 | FOR ID IN LBRACKET dict_items RBRACKET LBRACE RBRACE'''
    pass



#lambda
def p_param_list(p):
    '''param_list : param_list COMMA ID
                  | ID'''
    pass


def p_lambda_params(p):
    '''lambda_params : LPAREN param_list RPAREN
                     | LPAREN RPAREN'''
    pass

def p_lambda(p):
    "expr : LBRACE lambda_params ARROW ID IN expr RBRACE"
    pass




#condiociones lógicas
def p_condition_logic(p):
    '''condition : condition AND condition
                 | condition OR condition'''
    pass


def p_condition_comparison(p):
    '''condition : expr GT expr
                 | expr GE expr
                 | expr LT expr
                 | expr LE expr
                 | expr EQ expr
                 | expr NE expr'''
    pass


def p_condition_group(p):
    "condition : LPAREN condition RPAREN"
    pass

# empty rule
def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        msg = f"[SYN ERROR] Token inesperado '{p.value}' (tipo {p.type}) en línea {p.lineno}"
        print(msg)
        errores_sintacticos.append(msg)
    else:
        msg = "[SYN ERROR] Fin de archivo inesperado"
        print(msg)
        errores_sintacticos.append(msg)




parser = yacc.yacc(debug=True)

def ejecutar_test_sintactico(codigo_fuente, parser, usuario_git="AymanElS4"):
    

    # Limpiar errores previos
    errores_sintacticos.clear()

    # Ejecutar el parser
    parser.parse(codigo_fuente)

    # Crear carpeta logs si no existe
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Obtener fecha y hora actuales
    ahora = datetime.datetime.now()
    fecha = ahora.strftime("%d%m%Y")
    hora = ahora.strftime("%Hh%M")  # 23h32

    # Construir nombre del archivo
    nombre_archivo = f"sintactico-{usuario_git}-{fecha}-{hora}.txt"
    ruta_archivo = os.path.join("logs", nombre_archivo)

    # Escribir los errores en el archivo
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        if errores_sintacticos:
            f.write("Errores Sintácticos Detectados:\n")
            f.write("---------------------------------\n")
            for err in errores_sintacticos:
                f.write(err + "\n")
        else:
            f.write("Sin errores sintácticos.\n")

    return ruta_archivo  

with open(r"Proyecto-LP-Analizador\algoritmos\algoritmosprimitivos.swift", "r", encoding="utf-8") as f:
    swiftcod = f.read()

ejecutar_test_sintactico(
    codigo_fuente=swiftcod,
    parser=parser,
    usuario_git="AymanElS4"
)




