#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para probar cada analizador individualmente"""

import sys
import os

proyecto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'ArielArchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'Aymanarchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'JordanArchivos'))

codigo_prueba = """// Ejemplo basico de Swift

var x: Int = 10;
var y: Int = 20;
let suma: Int = x + y;

if x > 5 {
    x = x + 1;
}

var i: Int = 3;
while i > 0 {
    i = i - 1;
}
"""

print("="*80)
print("PROBANDO ARIEL")
print("="*80)
try:
    from analizadorLexicoArielAAT123 import analizador_lexico, errores_lexicos, tokens_reconocidos
    from analizadorSemantico import analizador_sintactico, errores_sintacticos, AnalizadorSemantico
    
    errores_lexicos.clear()
    tokens_reconocidos.clear()
    errores_sintacticos.clear()
    
    lexer = analizador_lexico
    parser = analizador_sintactico
    lexer.lineno = 1
    ast = parser.parse(codigo_prueba, lexer=lexer)
    
    print(f"✅ ARIEL parseó correctamente")
    print(f"   Errores léxicos: {len(errores_lexicos)}")
    print(f"   Errores sintácticos: {len(errores_sintacticos)}")
    
    if errores_sintacticos:
        for err in errores_sintacticos:
            print(f"   - {err}")
            
except Exception as e:
    print(f"❌ ARIEL falló: {e}")

print("\n" + "="*80)
print("PROBANDO AYMAN")
print("="*80)
try:
    from analizador_swift import parser as ayman_parser, lexer as ayman_lexer, parse_errors
    
    parse_errors.clear()
    result = ayman_parser.parse(codigo_prueba, lexer=ayman_lexer)
    
    print(f"✅ AYMAN parseó correctamente")
    print(f"   Errores sintácticos: {len(parse_errors)}")
    
    if parse_errors:
        print("   Errores detectados:")
        for err in parse_errors[:10]:  # Solo los primeros 10
            print(f"   - {err}")
            
except Exception as e:
    print(f"❌ AYMAN falló: {e}")

print("\n" + "="*80)
print("PROBANDO JORDAN")
print("="*80)
try:
    from sintactico_jordan import parser as jordan_parser, lexer as jordan_lexer, syntax_errors
    
    syntax_errors.clear()
    jordan_lexer.lineno = 1
    result = jordan_parser.parse(codigo_prueba, lexer=jordan_lexer)
    
    print(f"✅ JORDAN parseó correctamente")
    print(f"   Errores sintácticos: {len(syntax_errors)}")
    
    if syntax_errors:
        print("   Errores detectados:")
        for err in syntax_errors[:10]:  # Solo los primeros 10
            print(f"   - {err}")
            
except Exception as e:
    print(f"❌ JORDAN falló: {e}")

print("\n" + "="*80)
print("RESUMEN")
print("="*80)
