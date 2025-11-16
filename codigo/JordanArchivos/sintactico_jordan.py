import ply.yacc as yacc
import ply.lex as lex
from datetime import datetime
import os

reserved = {
    'class': 'CLASS', 'deinit': 'DEINIT', 'enum': 'ENUM', 'extension': 'EXTENSION',
    'func': 'FUNC', 'import': 'IMPORT', 'init': 'INIT', 'inout': 'INOUT',
    'let': 'LET', 'operator': 'OPERATOR', 'protocol': 'PROTOCOL', 'struct': 'STRUCT',
    'subscript': 'SUBSCRIPT', 'typealias': 'TYPEALIAS', 'var': 'VAR', 'break': 'BREAK',
    'case': 'CASE', 'continue': 'CONTINUE', 'default': 'DEFAULT', 'defer': 'DEFER',
    'do': 'DO', 'else': 'ELSE', 'fallthrough': 'FALLTHROUGH', 'for': 'FOR',
    'guard': 'GUARD', 'if': 'IF', 'in': 'IN', 'repeat': 'REPEAT', 'return': 'RETURN',
    'switch': 'SWITCH', 'where': 'WHERE', 'while': 'WHILE', 'as': 'AS', 'Any': 'ANY',
    'catch': 'CATCH', 'false': 'FALSE', 'is': 'IS', 'nil': 'NIL', 'rethrows': 'RETHROWS',
    'super': 'SUPER', 'self': 'SELF', 'Self': 'SELF_TYPE', 'throw': 'THROW',
    'throws': 'THROWS', 'true': 'TRUE', 'try': 'TRY', '__COLUMN__': 'COLUMN',
    '__FILE__': 'FILE', '__FUNCTION__': 'FUNCTION', '__LINE__': 'LINE'
}

tokens_list = [
    'ID', 'NUMBER', 'STRING', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET', 'COMMA', 'SEMICOLON', 'COLON', 'ARROW', 'ASSIGN',
    'EQUAL', 'NOT_EQUAL', 'LT', 'GT', 'LTE', 'GTE', 'PLUS', 'MINUS',
    'MULTIPLY', 'DIVIDE', 'AND', 'OR', 'NOT', 'DOT', 'QUESTION', 'MODULO',
    'PLUSASSIGN', 'MINUSASSIGN', 'MULTASSIGN', 'DIVASSIGN', 'RANGE', 'CLOSEDRANGE'
]

tokens = tokens_list + list(reserved.values())

t_ignore = ' \t'

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_ARROW = r'->'
t_DOT = r'\.'
t_QUESTION = r'\?'
t_ASSIGN = r'='
t_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_LTE = r'<='
t_GTE = r'>='
t_LT = r'<'
t_GT = r'>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_CLOSEDRANGE = r'\.\.\.'
t_RANGE = r'\.\.<'
t_PLUSASSIGN = r'\+='
t_MINUSASSIGN = r'-='
t_MULTASSIGN = r'\*='
t_DIVASSIGN = r'/='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

def t_COMMENT_SINGLE(t):
    r'//.*'
    pass

def t_COMMENT_MULTI(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_NUMBER(t):
    r'(\d+\.\d+|\d+)'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

syntax_errors = []

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUAL', 'NOT_EQUAL'),
    ('left', 'LT', 'LTE', 'GT', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
)

def p_program(p):
    """program : statements"""
    p[0] = ('program', p[1])

def p_statements_list(p):
    """statements : statements statement"""
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    """statements : statement"""
    p[0] = [p[1]]

def p_statement(p):
    """statement : if_statement
                 | function_declaration
                 | var_declaration
                 | expression_statement
                 | return_statement
                 | SEMICOLON"""
    if p[1] == ';':
        p[0] = ('empty',)
    else:
        p[0] = p[1]

def p_if_statement_simple(p):
    """if_statement : IF LPAREN expression RPAREN block"""
    p[0] = ('if', p[3], p[5])

def p_if_statement_else(p):
    """if_statement : IF LPAREN expression RPAREN block ELSE block"""
    p[0] = ('if_else', p[3], p[5], p[7])

def p_if_statement_else_if(p):
    """if_statement : IF LPAREN expression RPAREN block ELSE if_statement"""
    p[0] = ('if_else_if', p[3], p[5], p[7])

def p_block(p):
    """block : LBRACE statements RBRACE
             | LBRACE RBRACE"""
    if len(p) == 4:
        p[0] = ('block', p[2])
    else:
        p[0] = ('block', [])

def p_array_literal(p):
    """array_literal : LBRACKET RBRACKET
                    | LBRACKET array_elements RBRACKET"""
    if len(p) == 3:
        p[0] = ('array', [])
    else:
        p[0] = ('array', p[2])

def p_array_elements_list(p):
    """array_elements : array_elements COMMA expression"""
    p[0] = p[1] + [p[3]]

def p_array_elements_single(p):
    """array_elements : expression"""
    p[0] = [p[1]]

def p_array_access(p):
    """array_access : ID LBRACKET expression RBRACKET
                    | array_access LBRACKET expression RBRACKET"""
    if isinstance(p[1], str):
        p[0] = ('array_access', p[1], p[3])
    else:
        p[0] = ('array_access_nested', p[1], p[3])

def p_property_access(p):
    """property_access : ID DOT ID
                      | property_access DOT ID"""
    if isinstance(p[1], str):
        p[0] = ('property', p[1], p[3])
    else:
        p[0] = ('property_nested', p[1], p[3])

def p_function_declaration(p):
    """function_declaration : FUNC ID LPAREN parameters RPAREN ARROW type_annotation block
                           | FUNC ID LPAREN RPAREN ARROW type_annotation block"""
    if len(p) == 9:
        p[0] = ('function', p[2], p[4], p[6], p[8])
    else:
        p[0] = ('function', p[2], [], p[5], p[7])

def p_function_declaration_no_return(p):
    """function_declaration : FUNC ID LPAREN parameters RPAREN block
                           | FUNC ID LPAREN RPAREN block"""
    if len(p) == 7:
        p[0] = ('function_void', p[2], p[4], p[6])
    else:
        p[0] = ('function_void', p[2], [], p[5])

def p_parameters_list(p):
    """parameters : parameters COMMA parameter
                  | parameter"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_parameter(p):
    """parameter : ID COLON type_annotation"""
    p[0] = ('param', p[1], p[3])

def p_type_annotation(p):
    """type_annotation : ID
                      | ID QUESTION
                      | ID DOT ID
                      | LBRACKET type_annotation RBRACKET
                      | LBRACKET type_annotation COLON type_annotation RBRACKET"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = (p[1], 'optional')
    elif len(p) == 4 and p[2] == '[':
        p[0] = ('array_type', p[2])
    elif len(p) == 6:
        p[0] = ('dict_type', p[2], p[4])
    else:
        p[0] = (p[1], p[3])

def p_return_statement_value(p):
    """return_statement : RETURN expression SEMICOLON
                       | RETURN expression"""
    p[0] = ('return', p[2])

def p_return_statement_void(p):
    """return_statement : RETURN SEMICOLON
                       | RETURN"""
    p[0] = ('return', None)

def p_var_declaration(p):
    """var_declaration : VAR ID ASSIGN expression SEMICOLON
                      | VAR ID COLON type_annotation ASSIGN expression SEMICOLON
                      | LET ID ASSIGN expression SEMICOLON
                      | LET ID COLON type_annotation ASSIGN expression SEMICOLON"""
    if len(p) == 6:
        p[0] = ('var_decl', p[2], None, p[4])
    elif len(p) == 8 and p[1] == 'var':
        p[0] = ('var_decl', p[2], p[4], p[6])
    elif len(p) == 6 and p[1] == 'let':
        p[0] = ('let_decl', p[2], None, p[4])
    else:
        p[0] = ('let_decl', p[2], p[4], p[6])

def p_expression_statement(p):
    """expression_statement : expression SEMICOLON
                          | expression"""
    p[0] = ('expr_stmt', p[1])

def p_expression_assignment(p):
    """expression : ID ASSIGN expression
                  | ID PLUSASSIGN expression
                  | ID MINUSASSIGN expression
                  | ID MULTASSIGN expression
                  | ID DIVASSIGN expression"""
    p[0] = ('assign', p[1], p[2], p[3])

def p_expression_property_assignment(p):
    """expression : property_access ASSIGN expression"""
    p[0] = ('assign_property', p[1], p[3])

def p_expression_array_assignment(p):
    """expression : array_access ASSIGN expression"""
    p[0] = ('assign_array', p[1], p[3])

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression
                  | expression MODULO expression
                  | expression EQUAL expression
                  | expression NOT_EQUAL expression
                  | expression LT expression
                  | expression LTE expression
                  | expression GT expression
                  | expression GTE expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_unary(p):
    """expression : NOT expression
                  | MINUS expression"""
    p[0] = ('unary', p[1], p[2])

def p_expression_ternary(p):
    """expression : expression QUESTION expression COLON expression"""
    p[0] = ('ternary', p[1], p[3], p[5])

def p_expression_range(p):
    """expression : expression RANGE expression
                  | expression CLOSEDRANGE expression"""
    p[0] = ('range', p[2], p[1], p[3])

def p_expression_function_call(p):
    """expression : ID LPAREN argument_list RPAREN
                  | ID LPAREN RPAREN"""
    if len(p) == 5:
        p[0] = ('call', p[1], p[3])
    else:
        p[0] = ('call', p[1], [])

def p_argument_list(p):
    """argument_list : argument_list COMMA expression
                    | expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expression_array(p):
    """expression : array_literal"""
    p[0] = p[1]

def p_expression_array_access(p):
    """expression : array_access"""
    p[0] = p[1]

def p_expression_property_access(p):
    """expression : property_access"""
    p[0] = p[1]

def p_expression_paren(p):
    """expression : LPAREN expression RPAREN
                  | LPAREN tuple_elements RPAREN"""
    if isinstance(p[2], tuple) and p[2][0] == 'tuple':
        p[0] = p[2]
    else:
        p[0] = p[2]

def p_tuple_elements(p):
    """tuple_elements : expression COMMA expression
                     | tuple_elements COMMA expression"""
    if p[1][0] == 'tuple':
        p[0] = ('tuple', p[1][1] + [p[3]])
    else:
        p[0] = ('tuple', [p[1], p[3]])

def p_expression_primary(p):
    """expression : ID
                  | NUMBER
                  | STRING
                  | TRUE
                  | FALSE
                  | NIL"""
    p[0] = ('literal', p[1])

def p_error(p):
    global syntax_errors
    if p:
        error_msg = "Linea {}: token '{}' inesperado (tipo: {})".format(p.lineno, p.value, p.type)
        syntax_errors.append(error_msg)
        parser.errok()
    else:
        error_msg = "Linea desconocida: fin de archivo inesperado"
        syntax_errors.append(error_msg)

parser = yacc.yacc(debug=False, write_tables=False)

def analizar_archivo(nombre_archivo, usuario_git="jorssanc"):
    global syntax_errors
    syntax_errors = []

    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print("[ERROR] No se encontro el archivo '{}'".format(nombre_archivo))
        return

    lexer.lineno = 1

    print("[*] Analizando '{}'".format(nombre_archivo))
    ast = parser.parse(codigo, lexer=lexer)

    if not os.path.exists("logs"):
        os.makedirs("logs")

    fecha_hora = datetime.now().strftime("%d%m%Y-%Hh%M")
    log_filename = f"logs/sintactico-{usuario_git}-{fecha_hora}.txt"

    with open(log_filename, 'w', encoding='utf-8') as log:
        log.write("ANALIZADOR SINTACTICO - JORDAN\n")
        log.write("Usuario: {}\n".format(usuario_git))
        log.write("Archivo: {}\n".format(nombre_archivo))
        log.write("Fecha: {}\n".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        log.write("\n")
        log.write("\n")
        
        if syntax_errors:
            log.write("ERRORES ENCONTRADOS:\n")
            log.write("-" * 50 + "\n")
            for error in syntax_errors:
                log.write("{}\n".format(error))
            log.write("\nTotal errores: {}\n".format(len(syntax_errors)))
        else:
            log.write("Resultado: SIN ERRORES\n")

    print("[+] Log guardado: {}".format(log_filename))
    if syntax_errors:
        print("[!] {} error(es) sintactico(s) encontrado(s)".format(len(syntax_errors)))
        for error in syntax_errors:
            print("    {}".format(error))

if __name__ == "__main__":
    archivo_prueba = "algoritmos/algoritmo_if_arrays_funcion.swift"
    analizar_archivo(archivo_prueba, usuario_git="jorssanc")
