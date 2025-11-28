#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALIZADOR SEMÁNTICO UNIFICADO
Combina las capacidades semánticas de Ariel, Ayman y Jordan
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


# ============================================================================
# TIPOS DE DATOS
# ============================================================================

@dataclass
class TipoSwift:
    """Representa un tipo en Swift"""
    nombre: str  # 'Int', 'String', 'Array', 'Dictionary'
    parametros: List['TipoSwift'] = None  # Para tipos genéricos como [Int] o [String:Int]
    
    def __str__(self):
        if self.nombre in ['Int', 'Double', 'String', 'Bool', 'Character']:
            return self.nombre
        elif self.nombre == 'Array':
            elem = self.parametros[0] if self.parametros else 'Any'
            return f"[{elem}]"
        elif self.nombre == 'Dictionary':
            key = self.parametros[0] if self.parametros and len(self.parametros) > 0 else 'Any'
            val = self.parametros[1] if self.parametros and len(self.parametros) > 1 else 'Any'
            return f"[{key}:{val}]"
        else:
            return self.nombre
    
    def es_compatible_con(self, otro: 'TipoSwift') -> bool:
        """Verifica si este tipo es compatible con otro"""
        if self.nombre == 'Desconocido' or otro.nombre == 'Desconocido':
            return True
        
        # Tipos numéricos son compatibles entre sí
        if self.nombre in ['Int', 'Double'] and otro.nombre in ['Int', 'Double']:
            return True
        
        # Mismo tipo base
        if self.nombre != otro.nombre:
            return False
        
        # Para arrays y diccionarios, verificar parámetros
        if self.nombre == 'Array' and self.parametros and otro.parametros:
            return self.parametros[0].es_compatible_con(otro.parametros[0])
        
        if self.nombre == 'Dictionary' and self.parametros and otro.parametros:
            return (self.parametros[0].es_compatible_con(otro.parametros[0]) and
                    self.parametros[1].es_compatible_con(otro.parametros[1]))
        
        return True


@dataclass
class Simbolo:
    """Representa un símbolo en la tabla"""
    nombre: str
    tipo: TipoSwift
    mutable: bool  # True para var, False para let
    linea: int
    valor: Any = None  # Valor inicial si existe


# ============================================================================
# TABLA DE SÍMBOLOS UNIFICADA
# ============================================================================

class TablaSimbolosUnificada:
    """Tabla de símbolos compartida por todos los analizadores"""
    
    def __init__(self):
        self.scopes: List[Dict[str, Simbolo]] = [{}]
        self.errores: List[str] = []
        
        # Pre-cargar funciones built-in
        self.scopes[0]['print'] = Simbolo('print', TipoSwift('Function'), False, 0)
        self.scopes[0]['readLine'] = Simbolo('readLine', TipoSwift('Function'), False, 0)
    
    def nuevo_scope(self):
        """Abre un nuevo ámbito"""
        self.scopes.append({})
    
    def cerrar_scope(self):
        """Cierra el ámbito actual"""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def declarar(self, nombre: str, tipo: TipoSwift, mutable: bool, linea: int, valor: Any = None):
        """Declara una variable en el scope actual"""
        scope_actual = self.scopes[-1]
        
        if nombre in scope_actual:
            self.errores.append(
                f"❌ Línea {linea}: Variable '{nombre}' ya declarada en este ámbito"
            )
        else:
            scope_actual[nombre] = Simbolo(nombre, tipo, mutable, linea, valor)
    
    def buscar(self, nombre: str) -> Optional[Simbolo]:
        """Busca un símbolo en todos los scopes (de adentro hacia afuera)"""
        for scope in reversed(self.scopes):
            if nombre in scope:
                return scope[nombre]
        return None
    
    def validar_uso(self, nombre: str, linea: int) -> Optional[TipoSwift]:
        """Valida que una variable exista y retorna su tipo"""
        simbolo = self.buscar(nombre)
        if simbolo is None:
            self.errores.append(
                f"❌ Línea {linea}: Variable '{nombre}' no declarada"
            )
            return TipoSwift('Desconocido')
        return simbolo.tipo
    
    def validar_asignacion(self, nombre: str, tipo_valor: TipoSwift, linea: int):
        """Valida que una variable pueda ser reasignada"""
        simbolo = self.buscar(nombre)
        
        if simbolo is None:
            self.errores.append(
                f"❌ Línea {linea}: Variable '{nombre}' no declarada"
            )
            return
        
        if not simbolo.mutable:
            self.errores.append(
                f"❌ Línea {linea}: Variable '{nombre}' es inmutable (let) y no puede ser reasignada"
            )
            return
        
        if not simbolo.tipo.es_compatible_con(tipo_valor):
            self.errores.append(
                f"❌ Línea {linea}: Tipo incompatible. Variable '{nombre}' es {simbolo.tipo}, se intentó asignar {tipo_valor}"
            )


# ============================================================================
# ANALIZADOR SEMÁNTICO UNIFICADO
# ============================================================================

class AnalizadorSemanticoUnificado:
    """
    Analizador semántico que combina:
    - Variables var/let con mutabilidad (Ariel)
    - Arrays y diccionarios (Ayman)
    - Funciones y clases (Ariel)
    """
    
    def __init__(self):
        self.tabla = TablaSimbolosUnificada()
    
    def obtener_errores(self) -> List[str]:
        """Retorna todos los errores semánticos detectados"""
        return self.tabla.errores
    
    def nuevo_scope(self):
        """Abre un nuevo ámbito"""
        self.tabla.nuevo_scope()
    
    def cerrar_scope(self):
        """Cierra el ámbito actual"""
        self.tabla.cerrar_scope()
    
    # ========================================================================
    # DECLARACIONES
    # ========================================================================
    
    def declarar_variable(self, nombre: str, tipo: Optional[TipoSwift], 
                         valor_tipo: Optional[TipoSwift], mutable: bool, linea: int):
        """
        Declara una variable (var o let)
        - Si tiene tipo explícito, usa ese
        - Si no, infiere del valor
        - Valida compatibilidad si tiene ambos
        """
        # Determinar tipo final
        if tipo and valor_tipo:
            # Tiene tipo y valor: validar compatibilidad
            if not tipo.es_compatible_con(valor_tipo):
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Tipo incompatible. Variable '{nombre}' declarada como {tipo}, pero se inicializa con {valor_tipo}"
                )
            tipo_final = tipo
        elif tipo:
            # Solo tipo, sin valor
            tipo_final = tipo
        elif valor_tipo:
            # Solo valor, inferir tipo
            tipo_final = valor_tipo
        else:
            # Ni tipo ni valor
            self.tabla.errores.append(
                f"❌ Línea {linea}: Variable '{nombre}' declarada sin tipo ni valor"
            )
            tipo_final = TipoSwift('Desconocido')
        
        # Declarar en la tabla
        self.tabla.declarar(nombre, tipo_final, mutable, linea)
    
    def validar_asignacion(self, nombre: str, tipo_valor: TipoSwift, linea: int):
        """Valida reasignación de variable"""
        self.tabla.validar_asignacion(nombre, tipo_valor, linea)
    
    def validar_uso_variable(self, nombre: str, linea: int) -> TipoSwift:
        """Valida uso de variable y retorna su tipo"""
        return self.tabla.validar_uso(nombre, linea)
    
    # ========================================================================
    # TIPOS
    # ========================================================================
    
    def crear_tipo_simple(self, nombre: str) -> TipoSwift:
        """Crea un tipo simple (Int, String, etc.)"""
        return TipoSwift(nombre)
    
    def crear_tipo_array(self, tipo_elemento: TipoSwift) -> TipoSwift:
        """Crea un tipo array [T]"""
        return TipoSwift('Array', [tipo_elemento])
    
    def crear_tipo_diccionario(self, tipo_clave: TipoSwift, tipo_valor: TipoSwift) -> TipoSwift:
        """Crea un tipo diccionario [K:V]"""
        return TipoSwift('Dictionary', [tipo_clave, tipo_valor])
    
    def inferir_tipo_literal(self, valor: Any) -> TipoSwift:
        """Infiere el tipo de un literal"""
        if isinstance(valor, bool):
            return TipoSwift('Bool')
        elif isinstance(valor, int):
            return TipoSwift('Int')
        elif isinstance(valor, float):
            return TipoSwift('Double')
        elif isinstance(valor, str):
            return TipoSwift('String')
        else:
            return TipoSwift('Desconocido')
    
    def inferir_tipo_array(self, elementos: List[TipoSwift], linea: int) -> TipoSwift:
        """Infiere el tipo de un array literal"""
        if not elementos:
            return TipoSwift('Array', [TipoSwift('Any')])
        
        # Todos los elementos deben ser del mismo tipo
        tipo_base = elementos[0]
        for elem in elementos[1:]:
            if not tipo_base.es_compatible_con(elem):
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Array con tipos mixtos: {tipo_base} y {elem}"
                )
                return TipoSwift('Array', [TipoSwift('Any')])
        
        return TipoSwift('Array', [tipo_base])
    
    def inferir_tipo_diccionario(self, pares: List[tuple], linea: int) -> TipoSwift:
        """Infiere el tipo de un diccionario literal"""
        if not pares:
            return TipoSwift('Dictionary', [TipoSwift('Any'), TipoSwift('Any')])
        
        # Todos los pares deben tener claves y valores del mismo tipo
        tipo_clave = pares[0][0]
        tipo_valor = pares[0][1]
        
        for clave_tipo, valor_tipo in pares[1:]:
            if not tipo_clave.es_compatible_con(clave_tipo):
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Diccionario con claves de tipos mixtos: {tipo_clave} y {clave_tipo}"
                )
            if not tipo_valor.es_compatible_con(valor_tipo):
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Diccionario con valores de tipos mixtos: {tipo_valor} y {valor_tipo}"
                )
        
        return TipoSwift('Dictionary', [tipo_clave, tipo_valor])
    
    # ========================================================================
    # OPERACIONES
    # ========================================================================
    
    def validar_operacion_binaria(self, operador: str, tipo_izq: TipoSwift, 
                                  tipo_der: TipoSwift, linea: int) -> TipoSwift:
        """Valida operación binaria y retorna tipo resultado"""
        # Operadores aritméticos
        if operador in ['+', '-', '*', '/', '%']:
            if tipo_izq.nombre in ['Int', 'Double'] and tipo_der.nombre in ['Int', 'Double']:
                # Si alguno es Double, resultado es Double
                if tipo_izq.nombre == 'Double' or tipo_der.nombre == 'Double':
                    return TipoSwift('Double')
                return TipoSwift('Int')
            
            # Concatenación de strings
            if operador == '+' and tipo_izq.nombre == 'String' and tipo_der.nombre == 'String':
                return TipoSwift('String')
            
            self.tabla.errores.append(
                f"❌ Línea {linea}: Operador '{operador}' no aplicable a {tipo_izq} y {tipo_der}"
            )
            return TipoSwift('Desconocido')
        
        # Operadores de comparación
        if operador in ['==', '!=', '<', '>', '<=', '>=']:
            return TipoSwift('Bool')
        
        # Operadores lógicos
        if operador in ['&&', '||']:
            if tipo_izq.nombre != 'Bool' or tipo_der.nombre != 'Bool':
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Operador '{operador}' requiere operandos Bool, recibido {tipo_izq} y {tipo_der}"
                )
            return TipoSwift('Bool')
        
        return TipoSwift('Desconocido')
    
    def validar_operacion_unaria(self, operador: str, tipo: TipoSwift, linea: int) -> TipoSwift:
        """Valida operación unaria y retorna tipo resultado"""
        if operador == '!':
            if tipo.nombre != 'Bool':
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Operador '!' requiere tipo Bool, recibido {tipo}"
                )
            return TipoSwift('Bool')
        
        if operador == '-':
            if tipo.nombre not in ['Int', 'Double']:
                self.tabla.errores.append(
                    f"❌ Línea {linea}: Operador '-' requiere tipo numérico, recibido {tipo}"
                )
            return tipo
        
        return TipoSwift('Desconocido')
    
    # ========================================================================
    # CONTROL DE FLUJO
    # ========================================================================
    
    def validar_condicion(self, tipo: TipoSwift, contexto: str, linea: int):
        """Valida que una condición sea booleana"""
        if tipo.nombre not in ['Bool', 'Desconocido']:
            self.tabla.errores.append(
                f"❌ Línea {linea}: Condición de {contexto} debe ser Bool, recibido {tipo}"
            )


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def crear_analizador() -> AnalizadorSemanticoUnificado:
    """Crea y retorna una instancia del analizador unificado"""
    return AnalizadorSemanticoUnificado()
