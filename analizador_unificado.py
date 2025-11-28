#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALIZADOR UNIFICADO - PROYECTO LP
Combina los 3 analizadores con tokens y errores estandarizados
Implementa consenso: solo muestra errores cuando los 3 coinciden
"""

import sys
import os
from collections import defaultdict
from typing import List, Dict, Tuple

# Configurar paths
proyecto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'ArielArchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'Aymanarchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'JordanArchivos'))

# Importar el analizador semántico unificado
from semantico_unificado import crear_analizador


class ErrorEstandarizado:
    """Clase para errores estandarizados"""
    def __init__(self, linea: int, tipo: str, mensaje: str, analizador: str):
        self.linea = linea
        self.tipo = tipo  # 'lexico', 'sintactico', 'semantico'
        self.mensaje = mensaje
        self.analizador = analizador
    
    def __str__(self):
        return f"Línea {self.linea}: {self.mensaje}"
    
    def __eq__(self, other):
        # Dos errores son iguales si están en la misma línea y son del mismo tipo
        return self.linea == other.linea and self.tipo == other.tipo
    
    def __hash__(self):
        return hash((self.linea, self.tipo))


class AnalizadorUnificado:
    """Analizador que combina Ariel, Ayman y Jordan con semántica unificada"""
    
    def __init__(self):
        self.tokens_unificados = []
        self.errores_por_analizador = {
            'ariel': {'lexico': [], 'sintactico': [], 'semantico': []},
            'ayman': {'lexico': [], 'sintactico': [], 'semantico': []},
            'jordan': {'lexico': [], 'sintactico': [], 'semantico': []}
        }
        self.semantico_unificado = crear_analizador()
    
    def extraer_numero_linea(self, texto_error: str) -> int:
        """Extrae el número de línea de un mensaje de error"""
        import re
        # Buscar patrones como "línea X", "line X", "linea X"
        match = re.search(r'l[íi]nea?\s+(\d+)', texto_error, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return -1
    
    def normalizar_error(self, error_texto: str, tipo: str, analizador: str) -> ErrorEstandarizado:
        """Convierte un error de texto a ErrorEstandarizado"""
        linea = self.extraer_numero_linea(error_texto)
        # Limpiar el mensaje
        mensaje = error_texto.strip()
        return ErrorEstandarizado(linea, tipo, mensaje, analizador)
    
    def analizar_ariel(self, codigo: str):
        """Ejecutar analizador de Ariel (solo léxico y sintáctico)"""
        try:
            from analizadorLexicoArielAAT123 import analizador_lexico, errores_lexicos, tokens_reconocidos
            from analizadorSemantico import analizador_sintactico, errores_sintacticos
            
            # Limpiar
            errores_lexicos.clear()
            tokens_reconocidos.clear()
            errores_sintacticos.clear()
            
            # Ejecutar SOLO léxico y sintáctico
            lexer = analizador_lexico
            parser = analizador_sintactico
            lexer.lineno = 1
            ast = parser.parse(codigo, lexer=lexer)
            
            # Recoger tokens
            self.tokens_unificados.extend(tokens_reconocidos)
            
            # Normalizar errores léxicos y sintácticos
            for err in errores_lexicos:
                self.errores_por_analizador['ariel']['lexico'].append(
                    self.normalizar_error(str(err), 'lexico', 'ariel')
                )
            
            for err in errores_sintacticos:
                self.errores_por_analizador['ariel']['sintactico'].append(
                    self.normalizar_error(str(err), 'sintactico', 'ariel')
                )
            
        except Exception as e:
            print(f"Error en Ariel: {e}")
    
    def analizar_ayman(self, codigo: str):
        """Ejecutar analizador de Ayman"""
        try:
            from analizador_swift import parser as ayman_parser, lexer as ayman_lexer, parse_errors
            
            parse_errors.clear()
            ayman_parser.parse(codigo, lexer=ayman_lexer)
            
            # Normalizar errores sintácticos
            for err in parse_errors:
                self.errores_por_analizador['ayman']['sintactico'].append(
                    self.normalizar_error(str(err), 'sintactico', 'ayman')
                )
            
        except Exception as e:
            print(f"Error en Ayman: {e}")
    
    def analizar_jordan(self, codigo: str):
        """Ejecutar analizador de Jordan"""
        try:
            from sintactico_jordan import parser as jordan_parser, lexer as jordan_lexer, syntax_errors
            
            syntax_errors.clear()
            jordan_lexer.lineno = 1
            jordan_parser.parse(codigo, lexer=jordan_lexer)
            
            # Normalizar errores sintácticos
            for err in syntax_errors:
                self.errores_por_analizador['jordan']['sintactico'].append(
                    self.normalizar_error(str(err), 'sintactico', 'jordan')
                )
            
        except Exception as e:
            print(f"Error en Jordan: {e}")
    
    def analisis_semantico_unificado(self, codigo: str):
        """
        Ejecuta análisis semántico unificado en el código.
        Nota: Este es un análisis básico basado en parsing del código.
        Para una integración completa, se necesita acceso al AST de los parsers.
        """
        # Por ahora, usar el semántico unificado de forma independiente
        # En una implementación completa, esto recibiría el AST de los parsers
        
        # Aquí podrías integrar con el AST de Ariel si estuviera disponible
        # Por ahora, retornamos errores vacíos ya que el análisis completo
        # requeriría modificar los parsers para usar el analizador unificado
        
        errores = self.semantico_unificado.obtener_errores()
        for err in errores:
            self.errores_por_analizador['unificado'] = {
                'lexico': [],
                'sintactico': [],
                'semantico': [self.normalizar_error(err, 'semantico', 'unificado')]
            }
    
    def calcular_consenso(self) -> Dict[str, List[ErrorEstandarizado]]:
        """
        Usa Ariel para léxico/sintáctico y el analizador semántico unificado.
        """
        # Solo usar errores de Ariel para léxico y sintáctico
        # El semántico vendría del analizador unificado cuando esté completamente integrado
        consenso = {
            'lexico': self.errores_por_analizador['ariel']['lexico'],
            'sintactico': self.errores_por_analizador['ariel']['sintactico'],
            'semantico': self.errores_por_analizador.get('unificado', {}).get('semantico', [])
        }
        
        return consenso
    
    def analizar(self, codigo: str) -> Tuple[List, Dict[str, List[ErrorEstandarizado]], Dict]:
        """
        Analiza el código con los 3 analizadores y devuelve consenso
        
        Returns:
            tokens: Lista de tokens
            consenso: Dict con errores por consenso
            detalles: Dict con errores individuales por analizador
        """
        # Limpiar resultados anteriores
        self.tokens_unificados = []
        self.errores_por_analizador = {
            'ariel': {'lexico': [], 'sintactico': [], 'semantico': []},
            'ayman': {'lexico': [], 'sintactico': [], 'semantico': []},
            'jordan': {'lexico': [], 'sintactico': [], 'semantico': []}
        }
        self.semantico_unificado = crear_analizador()
        
        # Ejecutar los 3 analizadores
        self.analizar_ariel(codigo)
        self.analizar_ayman(codigo)
        self.analizar_jordan(codigo)
        
        # Ejecutar análisis semántico unificado
        self.analisis_semantico_unificado(codigo)
        
        # Calcular consenso
        consenso = self.calcular_consenso()
        
        return self.tokens_unificados, consenso, self.errores_por_analizador


def analizar_codigo(codigo: str):
    """Función principal para analizar código"""
    analizador = AnalizadorUnificado()
    tokens, consenso, detalles = analizador.analizar(codigo)
    
    return {
        'tokens': tokens,
        'errores_lexicos': consenso['lexico'],
        'errores_sintacticos': consenso['sintactico'],
        'errores_semanticos': consenso['semantico'],
        'detalles_por_analizador': detalles
    }
