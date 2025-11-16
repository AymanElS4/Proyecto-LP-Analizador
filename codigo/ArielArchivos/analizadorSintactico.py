from __future__ import annotations
import os
import sys
from datetime import datetime

# Importamos las herramientas de las otras capas
from analizadorLexicoArielAAT123 import analizador_lexico, errores_lexicos, tokens_reconocidos
from analizadorSemantico import analizador_sintactico, errores_sintacticos, AnalizadorSemantico

# Forzar UTF-8 para manejo de logs en la terminal
sys.stdout.reconfigure(encoding='utf-8')

# =========================================================================
# FUNCIÓN PRINCIPAL Y LOGGING
# =========================================================================

def analizar_archivo(ruta: str, usuario_git: str):
    """
    Ejecuta el análisis completo (Lex, Yacc, Semántico) y genera los logs.
    """
    
    # --- Cargar Código Fuente ---
    codigo = ""
    if not os.path.exists(ruta):
        # Usar código de prueba si el archivo no existe (útil para Canvas/pruebas rápidas)
        print(f"⚠️ Advertencia: Archivo '{ruta}' no encontrado. Ejecutando con código de prueba interno.")
        codigo = """
        // Código de Prueba para ArielAT123
        var contador: Int = 10;
        let p = (1, 2.5);
        
        while (contador > 0) {
            contador = contador - 1;
        }
        
        // Error Sintáctico intencional: Falta Punto y Coma
        var c = 1 
        
        // Ejemplo con función y clase
        func calcular(a: Int, b: Double = 10.0) -> Double {
            return Double(a) * b;
        }

        class Producto {
            var nombre: String = "Item";
        }
        """
    else:
         with open(ruta, "r", encoding="utf-8") as f:
             codigo = f.read()
    
    # --- 1. Ejecutar Análisis ---
    
    # Limpiar listas globales (aunque se limpian en lexer, mejor ser explícitos)
    errores_lexicos.clear()
    tokens_reconocidos.clear()
    errores_sintacticos.clear()
    
    lexer = analizador_lexico
    parser = analizador_sintactico
    lexer.lineno = 1
    ast = parser.parse(codigo, lexer=lexer)

    sem = AnalizadorSemantico()
    if ast: sem.verificar(ast)

    # --- 2. Generar Logs ---
    os.makedirs("logs", exist_ok=True)
    
    base_filename = os.path.basename(ruta)
    name_without_ext = os.path.splitext(base_filename)[0]
    timestamp_log = datetime.now().strftime('%Y%m%d-%Hh%M')
    
    # 2.1 Log General (Formato: [nombre_del_archivo]-[usuarioGit]-[fecha]-[hora].txt)
    archivo_log_general = f"logs/{name_without_ext}-{usuario_git}-{timestamp_log}.txt" 

    with open(archivo_log_general, "w", encoding="utf-8") as log:
        log.write("=" * 60 + "\n")
        log.write("ANÁLISIS DE COMPILADOR (ARIEL ARIAS TIPÁN) - MODULAR\n")
        log.write(f"Archivo: {ruta} | Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        log.write("=" * 60 + "\n\n")

        log.write("RESPONSABILIDADES CLAVE (ARIEL):\n")
        log.write("- Declaración de variables (var/let), Asignación de variables.\n")
        log.write("- Bucles WHILE, Condicionales IF/ELSE, Tuplas, Clases.\n")
        log.write("- Funciones con parámetros por defecto.\n")
        log.write("- SEMÁNTICO: Asignación de tipos y Operaciones permitidas.\n\n")

        log.write("✅ RESUMEN DE TOKENS RECONOCIDOS:\n")
        log.write("-" * 60 + f"\nTotal: {len(tokens_reconocidos)} tokens\n\n")

        log.write("❌ ERRORES LÉXICOS:\n")
        log.write("-" * 60 + "\n")
        if errores_lexicos: log.write('\n'.join(errores_lexicos) + '\n')
        else: log.write("No se encontraron errores léxicos.\n")
        log.write(f"\nTotal: {len(errores_lexicos)} error(es) léxico(s)\n\n")

        log.write("❌ ERRORES SINTÁCTICOS:\n")
        log.write("-" * 60 + "\n")
        if errores_sintacticos: log.write('\n'.join(errores_sintacticos) + '\n')
        else: log.write("No se encontraron errores sintácticos.\n")
        log.write(f"\nTotal: {len(errores_sintacticos)} error(es) sintáctico(s)\n\n")

        log.write("❌ ERRORES SEMÁNTICOS:\n")
        log.write("-" * 60 + "\n")
        if sem.errores: log.write('\n'.join(sem.errores) + '\n')
        else: log.write("No se encontraron errores semánticos.\n")
        log.write(f"\nTotal: {len(sem.errores)} error(es) semántico(s)\n\n")

        total_errores = len(errores_lexicos) + len(errores_sintacticos) + len(sem.errores)
        log.write("=" * 60 + "\n")
        log.write(f"RESUMEN FINAL: {total_errores} error(es) total(es).\n")
        log.write("=" * 60 + "\n")
    
    print(f"✅ Log General generado en: {archivo_log_general}")

    # 2.2 Log Específico de Errores Sintácticos (REQUERIDO)
    if errores_sintacticos:
        # Formato solicitado: sintactico-usuarioGit-fecha-hora.txt
        timestamp_sintactico = datetime.now().strftime('%d%m%Y-%Hh%M')
        archivo_log_sintactico = f"logs/sintactico-{usuario_git}-{timestamp_sintactico}.txt"
        
        with open(archivo_log_sintactico, "w", encoding="utf-8") as log_sint:
            log_sint.write("=" * 60 + "\n")
            log_sint.write(f"LOG DE ERRORES SINTÁCTICOS - {usuario_git}\n")
            log_sint.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            log_sint.write("=" * 60 + "\n\n")
            log_sint.write('\n'.join(errores_sintacticos) + '\n')
            log_sint.write(f"\nTotal de errores sintácticos: {len(errores_sintacticos)}.\n")
        
        print(f"✅ Log Sintáctico generado en: {archivo_log_sintactico}")
    
# =========================================================================
# MAIN
# =========================================================================
if __name__ == "__main__":
    ruta_archivo = "algoritmos/algoritmo_identificadores_y_operadores.swift"
    usuario_git_ariel = "ArielAT123" 
    
    analizar_archivo(ruta_archivo, usuario_git_ariel)