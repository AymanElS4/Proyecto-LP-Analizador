import os
import datetime

#ya que no podia cambiar la ubicacion del parser.out, se hizo esta funcion para crear el log correspondiente

#para leer el parser.out y de ahí generar un log con los conflictos, reglas y estados
def generar_log_desde_parser_out(ruta_parser_out="parser.out", usuario_git="AymanElS4"):
    
    if not os.path.exists(ruta_parser_out):
        print(f"[ERROR] No se encontró '{ruta_parser_out}'")
        return
    
    # Leer contenido completo
    with open(ruta_parser_out, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Crear carpeta logs si no existe
    os.makedirs("logs", exist_ok=True)

    # Crear nombre del log
    fecha_hora = datetime.datetime.now().strftime("%d-%m-%Y-%Hh%M")
    archivo_log = f"Proyecto-LP-Analizador\logs\sintaxis-{usuario_git}-{fecha_hora}.txt"
   


    conflictos = []
    reglas = []
    estados = []

    lineas = contenido.splitlines()

    modo_reglas = False
    modo_estados = False

    for linea in lineas:
        # Conflictos típicos
        if "shift/reduce conflict" in linea or "reduce/reduce conflict" in linea:
            conflictos.append(linea.strip())

        # Detectar lista de reglas
        if linea.strip().startswith("Rules:"):
            modo_reglas = True
            modo_estados = False
            continue

        # Detectar tabla de estados
        if linea.strip().startswith("state 0"):
            modo_estados = True
            modo_reglas = False

        # Guardar reglas
        if modo_reglas and linea.strip() and not linea.startswith("state"):
            reglas.append(linea.rstrip())

        # Guardar estados
        if modo_estados:
            estados.append(linea.rstrip())

    #Escribir log
    with open(archivo_log, "w", encoding="utf-8") as log:
        log.write("="*60 + "\n")
        log.write(f"   RESUMEN DE PARSER.OUT – Usuario: {usuario_git}\n")
        log.write(f"   Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        log.write("="*60 + "\n\n")

        # Conflictos
        log.write("CONFLICTOS ENCONTRADOS\n")
        log.write("-"*60 + "\n")
        if conflictos:
            for c in conflictos:
                log.write(c + "\n")
        else:
            log.write("No se encontraron conflictos.\n")
        log.write("\n")

        # Reglas
        log.write("REGLAS DETECTADAS\n")
        log.write("-"*60 + "\n")
        if reglas:
            for r in reglas:
                log.write(r + "\n")
        else:
            log.write("No se pudieron detectar reglas.\n")
        log.write("\n")

        # Estados
        log.write("ESTADOS DEL PARSER\n")
        log.write("-"*60 + "\n")
        if estados:
            for e in estados:
                log.write(e + "\n")
        else:
            log.write("No se pudieron detectar estados.\n")

    print(f"Log generado exitosamente en: {archivo_log}")

generar_log_desde_parser_out(ruta_parser_out="Proyecto-LP-Analizador\codigo\Aymanarchivos\parser.out", usuario_git="AymanElS4")
