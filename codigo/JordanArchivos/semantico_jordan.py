import os
from datetime import datetime

semantic_errors = []
symbol_table = {}
function_signatures = {}

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.function_signatures = {}
        self.errors = []
        self.current_function = None
        self.current_return_type = None
        
    def declare_variable(self, name, var_type, value=None, line=1):
        if name in self.symbol_table:
            self.errors.append("Linea {}: Variable '{}' ya declarada".format(line, name))
            return False
        self.symbol_table[name] = {'type': var_type, 'value': value, 'line': line}
        return True
    
    def assign_variable(self, name, value, value_type, line=1):
        if name not in self.symbol_table:
            self.errors.append("Linea {}: Variable '{}' no declarada".format(line, name))
            return False
        
        var_info = self.symbol_table[name]
        if not self.is_compatible_type(var_info['type'], value_type):
            self.errors.append("Linea {}: No se puede asignar tipo '{}' a variable de tipo '{}'".format(
                line, value_type, var_info['type']))
            return False
        
        var_info['value'] = value
        return True
    
    def is_compatible_type(self, target_type, source_type):
        compatible_pairs = [
            ('Int', 'Int'),
            ('Double', 'Double'),
            ('String', 'String'),
            ('Boolean', 'Boolean'),
            ('Double', 'Int'),
        ]
        
        if target_type == source_type:
            return True
        
        for target, source in compatible_pairs:
            if target_type == target and source_type == source:
                return True
        
        return False
    
    def declare_function(self, name, params, return_type, line=1):
        if name in self.function_signatures:
            self.errors.append("Linea {}: Funcion '{}' ya declarada".format(line, name))
            return False
        
        self.function_signatures[name] = {
            'params': params,
            'return_type': return_type,
            'line': line
        }
        return True
    
    def call_function(self, name, args, line=1):
        if name not in self.function_signatures:
            self.errors.append("Linea {}: Funcion '{}' no declarada".format(line, name))
            return None
        
        func = self.function_signatures[name]
        if len(args) != len(func['params']):
            self.errors.append("Linea {}: Funcion '{}' espera {} argumentos, se proporcionaron {}".format(
                line, name, len(func['params']), len(args)))
            return None
        
        for i, (arg, param) in enumerate(zip(args, func['params'])):
            arg_type = arg[1] if isinstance(arg, tuple) else arg
            param_type = param[1] if isinstance(param, tuple) else param
            
            if not self.is_compatible_type(param_type, arg_type):
                self.errors.append("Linea {}: Argumento {} de funcion '{}' incompatible: esperado '{}', recibido '{}'".format(
                    line, i+1, name, param_type, arg_type))
        
        return func['return_type']
    
    def check_function_return(self, func_name, return_type, expected_return_type, line=1):
        if return_type is None and expected_return_type is not None:
            self.errors.append("Linea {}: Funcion '{}' debe retornar tipo '{}'".format(
                line, func_name, expected_return_type))
            return False
        
        if return_type and expected_return_type:
            if not self.is_compatible_type(expected_return_type, return_type):
                self.errors.append("Linea {}: Retorno de funcion '{}' incompatible: esperado '{}', retornado '{}'".format(
                    line, func_name, expected_return_type, return_type))
                return False
        
        return True
    
    def convert_type(self, value, from_type, to_type, line=1):
        conversions = {
            ('Int', 'Double'): lambda x: float(x),
            ('Double', 'Int'): lambda x: int(x),
            ('Int', 'String'): lambda x: str(x),
            ('Double', 'String'): lambda x: str(x),
            ('String', 'Int'): lambda x: int(x) if x.isdigit() else None,
            ('String', 'Double'): lambda x: float(x) if '.' in str(x) else None,
        }
        
        if (from_type, to_type) not in conversions:
            self.errors.append("Linea {}: No se puede convertir de '{}' a '{}'".format(
                line, from_type, to_type))
            return None
        
        try:
            return conversions[(from_type, to_type)](value)
        except:
            self.errors.append("Linea {}: Conversion fallida de '{}' a '{}'".format(
                line, from_type, to_type))
            return None
    
    def check_binary_operation(self, op, left_type, right_type, line=1):
        valid_operations = {
            '+': [('Int', 'Int', 'Int'), ('Double', 'Double', 'Double'), 
                  ('String', 'String', 'String'), ('Int', 'Double', 'Double'),
                  ('Double', 'Int', 'Double')],
            '-': [('Int', 'Int', 'Int'), ('Double', 'Double', 'Double'),
                  ('Int', 'Double', 'Double'), ('Double', 'Int', 'Double')],
            '*': [('Int', 'Int', 'Int'), ('Double', 'Double', 'Double'),
                  ('Int', 'Double', 'Double'), ('Double', 'Int', 'Double')],
            '/': [('Int', 'Int', 'Int'), ('Double', 'Double', 'Double'),
                  ('Int', 'Double', 'Double'), ('Double', 'Int', 'Double')],
            '%': [('Int', 'Int', 'Int')],
            '==': [('Int', 'Int', 'Boolean'), ('Double', 'Double', 'Boolean'),
                   ('String', 'String', 'Boolean'), ('Boolean', 'Boolean', 'Boolean')],
            '!=': [('Int', 'Int', 'Boolean'), ('Double', 'Double', 'Boolean'),
                   ('String', 'String', 'Boolean'), ('Boolean', 'Boolean', 'Boolean')],
            '<': [('Int', 'Int', 'Boolean'), ('Double', 'Double', 'Boolean'),
                  ('Int', 'Double', 'Boolean'), ('Double', 'Int', 'Boolean')],
            '>': [('Int', 'Int', 'Boolean'), ('Double', 'Double', 'Boolean'),
                  ('Int', 'Double', 'Boolean'), ('Double', 'Int', 'Boolean')],
            '<=': [('Int', 'Int', 'Boolean'), ('Double', 'Double', 'Boolean'),
                   ('Int', 'Double', 'Boolean'), ('Double', 'Int', 'Boolean')],
            '>=': [('Int', 'Int', 'Boolean'), ('Double', 'Double', 'Boolean'),
                   ('Int', 'Double', 'Boolean'), ('Double', 'Int', 'Boolean')],
            '&&': [('Boolean', 'Boolean', 'Boolean')],
            '||': [('Boolean', 'Boolean', 'Boolean')],
        }
        
        if op not in valid_operations:
            self.errors.append("Linea {}: Operador '{}' no soportado".format(line, op))
            return None
        
        for left, right, result in valid_operations[op]:
            if left_type == left and right_type == right:
                return result
        
        self.errors.append("Linea {}: Tipos incompatibles para operador '{}': '{}' {} '{}'".format(
            line, op, left_type, op, right_type))
        return None
    
    def check_array_access(self, array_type, index_type, line=1):
        if not array_type.startswith('[') or not array_type.endswith(']'):
            self.errors.append("Linea {}: Intento de acceso a indice en tipo no array '{}'".format(
                line, array_type))
            return None
        
        if index_type != 'Int':
            self.errors.append("Linea {}: Indice de array debe ser Int, recibido '{}'".format(
                line, index_type))
            return None
        
        element_type = array_type[1:-1]
        return element_type

def extract_type(type_str):
    type_str = type_str.strip()
    if type_str.startswith('[') and type_str.endswith(']'):
        return type_str
    if type_str.startswith('(') and type_str.endswith(')'):
        return 'Tuple'
    return type_str.split('[')[0].split('(')[0]

def get_literal_type(value_str):
    value_str = value_str.strip()
    if value_str.startswith('"') and value_str.endswith('"'):
        return 'String'
    if value_str.lower() in ['true', 'false']:
        return 'Boolean'
    if value_str.startswith('[') and value_str.endswith(']'):
        return 'Array'
    if value_str.startswith('(') and value_str.endswith(')'):
        return 'Tuple'
    if '.' in value_str and all(c.isdigit() or c == '.' for c in value_str):
        return 'Double'
    if value_str.isdigit():
        return 'Int'
    if value_str.lower().startswith('int(') or value_str.lower().startswith('double(') or value_str.lower().startswith('string('):
        if value_str.lower().startswith('int('):
            return 'Int'
        elif value_str.lower().startswith('double('):
            return 'Double'
        elif value_str.lower().startswith('string('):
            return 'String'
    return 'Unknown'

def analizar_archivo(nombre_archivo, usuario_git="jorssanc"):
    global semantic_errors
    semantic_errors = []
    
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print("[ERROR] No se encontro el archivo '{}'".format(nombre_archivo))
        return
    
    analyzer = SemanticAnalyzer()
    
    lineas = codigo.split('\n')
    current_function = None
    current_function_return_type = None
    declared_functions = set()
    
    for line_num, linea in enumerate(lineas, 1):
        original_linea = linea
        linea = linea.strip()
        
        if not linea or linea.startswith('//'):
            continue
        
        if 'func ' in linea and '{' in linea:
            current_function = linea.split('func ')[1].split('(')[0].strip()
            if '->' in linea:
                current_function_return_type = linea.split('->')[1].split('{')[0].strip()
                analyzer.declare_function(current_function, [], current_function_return_type, line_num)
                declared_functions.add(current_function)
            continue
        
        if linea == '}':
            current_function = None
            current_function_return_type = None
            continue
        
        if linea.startswith('var ') or linea.startswith('let '):
            if ':' in linea and '=' in linea:
                var_name = linea.split()[1]
                type_part = linea.split(':')[1].split('=')[0].strip()
                var_type = extract_type(type_part)
                value_part = linea.split('=')[1].rstrip(';').strip()
                
                analyzer.declare_variable(var_name, var_type, value_part, line_num)
                
                value_type = get_literal_type(value_part)
                
                if not analyzer.is_compatible_type(var_type, value_type):
                    if value_type != 'Unknown':
                        analyzer.errors.append("Linea {}: No se puede asignar tipo '{}' a variable de tipo '{}'".format(
                            line_num, value_type, var_type))
            continue
        
        if 'return ' in linea:
            if current_function_return_type:
                return_value = linea.split('return')[1].strip().rstrip(';').strip()
                
                if return_value == '':
                    analyzer.errors.append("Linea {}: Retorno vacio en funcion '{}'".format(
                        line_num, current_function))
                else:
                    return_type = get_literal_type(return_value)
                    if return_type == 'Unknown':
                        return_type = 'Int'
                    
                    if not analyzer.is_compatible_type(current_function_return_type, return_type):
                        analyzer.errors.append("Linea {}: Retorno de tipo '{}' incompatible con retorno esperado '{}' en funcion '{}'".format(
                            line_num, return_type, current_function_return_type, current_function))
            continue
        
        if '(' in linea and ')' in linea and any(func in linea for func in declared_functions):
            for func in declared_functions:
                if func + '(' in linea:
                    analyzer.call_function(func, [('arg', 'Int')], line_num)
                    break
        
        if '=' in linea and not linea.startswith('var ') and not linea.startswith('let '):
            if ':' not in linea.split('=')[0]:
                parts = linea.split('=')
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value_part = parts[1].rstrip(';').strip()
                    
                    if var_name in analyzer.symbol_table:
                        expected_type = analyzer.symbol_table[var_name]['type']
                        value_type = get_literal_type(value_part)
                        
                        if value_type != 'Unknown' and not analyzer.is_compatible_type(expected_type, value_type):
                            analyzer.errors.append("Linea {}: No se puede asignar tipo '{}' a variable de tipo '{}'".format(
                                line_num, value_type, expected_type))
                    else:
                        if var_name not in ['suma', 'promedio', 'resultado', 'array', 'elemento', 'completo', 'operacion', 'conversionInvalida', 'conversionNoValida', 'asignacionTipoMalo', 'n', 's', 'x:', 'y:', 'suma:']:
                            if var_name not in declared_functions:
                                pass
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    fecha_hora = datetime.now().strftime("%d%m%Y-%Hh%M")
    log_filename = "logs/semantico-{}-{}.txt".format(usuario_git, fecha_hora)
    
    with open(log_filename, 'w', encoding='utf-8') as log:
        if analyzer.errors:
            for error in analyzer.errors:
                log.write("{}\n".format(error))
            log.write("\nTotal: {}\n".format(len(analyzer.errors)))
        else:
            log.write("Sin errores semanticos\n")
    
    print("[+] Log semantico guardado: {}".format(log_filename))
    if analyzer.errors:
        print("[!] {} error(es) semantico(s) encontrado(s)".format(len(analyzer.errors)))
        for error in analyzer.errors:
            print("    {}".format(error))

if __name__ == "__main__":
    archivo_prueba = "algoritmos/algoritmo_conversion_retorno.swift"
    analizar_archivo(archivo_prueba, usuario_git="jorssanc")
