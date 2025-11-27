#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para empaquetar el proyecto en un archivo .zip
Incluye todos los archivos necesarios para la entrega final
"""

import os
import zipfile
from datetime import datetime

def crear_zip_proyecto():
    """Crear archivo .zip con todos los componentes del proyecto"""
    
    # Nombre del archivo zip con fecha
    fecha = datetime.now().strftime('%Y%m%d')
    nombre_zip = f'Proyecto-LP-Analizador-Swift_{fecha}.zip'
    
    # Archivos y carpetas a incluir
    archivos_incluir = [
        'README.md',
        'requirements.txt',
        'interfaz_grafica.py',
        'codigo/',
        'algoritmos/',
        'logs/'
    ]
    
    # Archivos a excluir
    patrones_excluir = [
        '__pycache__',
        '.pyc',
        '.git',
        'parsetab.py',
        '.DS_Store'
    ]
    
    print("="*60)
    print("EMPAQUETANDO PROYECTO - ANALIZADOR DE SWIFT")
    print("="*60)
    print(f"Creando archivo: {nombre_zip}\n")
    
    try:
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            archivos_agregados = 0
            
            # Agregar archivos individuales
            for item in archivos_incluir:
                if os.path.isfile(item):
                    zipf.write(item)
                    print(f"✓ Agregado: {item}")
                    archivos_agregados += 1
                    
                elif os.path.isdir(item):
                    # Agregar directorio y su contenido
                    for root, dirs, files in os.walk(item):
                        # Filtrar directorios a excluir
                        dirs[:] = [d for d in dirs if not any(excl in d for excl in patrones_excluir)]
                        
                        for file in files:
                            # Filtrar archivos a excluir
                            if not any(excl in file for excl in patrones_excluir):
                                ruta_completa = os.path.join(root, file)
                                zipf.write(ruta_completa)
                                print(f"✓ Agregado: {ruta_completa}")
                                archivos_agregados += 1
        
        # Información final
        tamaño = os.path.getsize(nombre_zip) / 1024  # KB
        print(f"\n{'='*60}")
        print(f"✅ ARCHIVO CREADO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Nombre: {nombre_zip}")
        print(f"Tamaño: {tamaño:.2f} KB")
        print(f"Archivos incluidos: {archivos_agregados}")
        print(f"\n📦 El archivo .zip está listo para entregar!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR al crear el archivo .zip: {str(e)}\n")
        return False
    
    return True

if __name__ == "__main__":
    crear_zip_proyecto()
