# Analizador Unificado de Swift - Proyecto de Lenguajes de Programación

## 📋 Descripción del Proyecto

Este proyecto implementa un **analizador unificado** para el lenguaje Swift que combina el trabajo de 3 integrantes:

### 🎯 Enfoque de Consenso
El analizador ejecuta **simultáneamente** los 3 analizadores del equipo y:
- ✅ **Solo muestra errores** cuando **LOS 3 analizadores coinciden** en detectar un problema en la misma línea
- ✅ **Si al menos 1 analizador NO detecta el error**, significa que ese integrante implementó correctamente esa parte
- ✅ El resultado es un análisis **robusto** que solo reporta errores reales confirmados por consenso

### Componentes:
- **Analizador Léxico**: Reconoce tokens, palabras reservadas, identificadores y operadores
- **Analizador Sintáctico**: Valida la estructura gramatical del código  
- **Analizador Semántico**: Verifica reglas semánticas de tipos y alcance
- **Interfaz Gráfica Unificada**: Muestra resultados consolidados con errores confirmados

## 👥 Integrantes del Equipo

| Integrante | Usuario Git | Responsabilidades |
|------------|-------------|-------------------|
| **Ariel Arias Tipán** | ArielAT123 | Analizador completo (léxico + sintáctico + semántico), Variables, Clases, Funciones, While |
| **Ayman El Salous** | AymanElS4 | Tipos primitivos, Arrays, Diccionarios, For-in, Lambdas |
| **Jordan Sánchez** | jorssanc | If-else, Arrays, Funciones con retorno, Palabras reservadas |

## 🚀 Instalación

### Requisitos Previos
- **Python 3.7 o superior**
- **tkinter** (incluido con Python en Windows y macOS)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install ply
```

**Para Linux (Ubuntu/Debian)**, si tkinter no está instalado:
```bash
sudo apt-get install python3-tk
```

## 📁 Estructura del Proyecto

```
Proyecto-LP-Analizador/
│
├── interfaz_grafica.py              # ⭐ ARCHIVO PRINCIPAL - Interfaz gráfica
│
├── codigo/                           # Analizadores por integrante
│   ├── ArielArchivos/               # Analizador completo (Ariel)
│   │   ├── analizadorLexicoArielAAT123.py
│   │   ├── analizadorSintactico.py
│   │   └── analizadorSemantico.py
│   │
│   ├── Aymanarchivos/               # Analizador semántico (Ayman)
│   │   ├── analizador_swift.py
│   │   └── primitivos_y_limitadores.py
│   │
│   └── JordanArchivos/              # Analizador sintáctico (Jordan)
│       ├── sintactico_jordan.py
│       ├── semantico_jordan.py
│       └── palabras_reservadas_comentarios.py
│
├── algoritmos/                       # Algoritmos de prueba
│   ├── algoritmo_comentarios_y_palabrasReservadas.swift
│   ├── algoritmo_identificadores_y_operadores.swift
│   ├── algoritmo_if_arrays_funcion.swift
│   ├── algoritmo_conversion_retorno.swift
│   └── algoritmosprimitivos.swift
│
├── logs/                            # Logs generados automáticamente
│   └── (archivos .txt generados por el análisis)
│
├── README.md                        # Este archivo
├── GUIA_RAPIDA.md                   # Guía de inicio rápido
├── requirements.txt                 # Dependencias
└── crear_zip.py                     # Script para crear .zip de entrega
```

## 🎯 Uso del Programa

### Interfaz Gráfica Unificada (RECOMENDADO) ⭐

Ejecute la interfaz gráfica principal:

```bash
python interfaz_grafica.py
```

#### 🎯 Cómo Funciona el Consenso:

1. **Ejecución Simultánea**: Al hacer click en "ANALIZAR", se ejecutan los 3 analizadores automáticamente
2. **Detección de Consenso**: El sistema compara los errores línea por línea
3. **Reporte Inteligente**:
   - ✅ **Se muestra el error** → Si los 3 analizadores lo detectaron
   - ❌ **NO se muestra** → Si al menos 1 analizador NO lo detectó (significa que ese integrante lo implementó bien)

#### 📊 Pestañas de Resultados:

1. **📋 Resumen**: Estadísticas generales y errores confirmados por consenso
2. **❌ Errores Detectados**: Solo errores donde LOS 3 coinciden
3. **🔤 Tokens**: Lista completa de tokens reconocidos
4. **📝 Detalles por Analizador**: Vista individual de cada analizador

#### 📂 Funciones Disponibles:
- **Abrir**: Cargar archivos `.swift` desde `algoritmos/`
- **Guardar**: Guardar el código actual
- **Nuevo**: Limpiar el editor
- **Ejemplo**: Cargar código de ejemplo
- **Usuario**: Personalizar nombre para los logs

#### 📝 Generación de Logs:
- Los logs se guardan automáticamente en `logs/`
- Formato: `analisis_unificado-[usuario]-[fecha].txt`
- Incluyen solo errores confirmados por los 3 analizadores

### Ejecución Individual de Analizadores (Opcional)

#### Analizador Completo (Ariel)
```bash
python codigo/ArielArchivos/analizadorSintactico.py
```

#### Analizador de Ayman
```bash
python codigo/Aymanarchivos/analizador_swift.py
```

#### Analizador de Jordan
```bash
python codigo/JordanArchivos/sintactico_jordan.py
```

## 📝 Análisis Implementado

### 1️⃣ Analizador Léxico

**Tokens Reconocidos:**
- **Palabras reservadas**: `var`, `let`, `func`, `if`, `else`, `while`, `for`, `in`, `class`, `return`, `import`, etc.
- **Identificadores**: nombres de variables, funciones y clases
- **Literales**:
  - Enteros: `42`, `100`
  - Decimales: `3.14`, `2.718`
  - Cadenas: `"Hola"`, `"Swift"`
  - Caracteres: `'A'`, `'Z'`
  - Booleanos: `true`, `false`
- **Operadores**:
  - Aritméticos: `+`, `-`, `*`, `/`, `%`
  - Lógicos: `&&`, `||`, `!`
  - Relacionales: `==`, `!=`, `<`, `>`, `<=`, `>=`
  - Asignación: `=`, `+=`, `-=`, `*=`, `/=`
- **Delimitadores**: `(`, `)`, `{`, `}`, `[`, `]`, `,`, `;`, `:`
- **Especiales**: `->` (flecha), `...` (rango cerrado), `..<` (rango abierto)
- **Comentarios**: `//` (línea) y `/* */` (multilínea)

**Errores Detectados:**
- Caracteres no reconocidos
- Símbolos inválidos

### 2️⃣ Analizador Sintáctico

**Estructuras Reconocidas por Integrante:**

#### Ariel:
- Declaración de variables (`var`, `let`)
- Asignaciones y reasignaciones
- Bucles `while`
- Condicionales (`if`, `if-else`)
- Funciones con parámetros y valores por defecto
- Clases con propiedades y métodos
- Tuplas
- Expresiones aritméticas y lógicas

#### Ayman:
- Tipos primitivos (Int, Float, Double, Bool, String, Character)
- Arrays y acceso a elementos
- Diccionarios `[Key:Value]`
- Bucles `for-in`
- Lambdas simples (`x -> expresion`)
- Rangos (`...`, `..<`)

#### Jordan:
- Condicionales `if-else` anidados
- Declaración de funciones con retorno
- Arrays literales y acceso
- Expresiones con operadores
- Tuplas
- Asignaciones compuestas (`+=`, `-=`, `*=`, `/=`)

**Tipos de Errores Detectados:**
1. **Token inesperado**: símbolo fuera de contexto
2. **EOF inesperado**: fin de archivo prematuro
3. **Estructura incompleta**: falta de delimitadores

### 3️⃣ Analizador Semántico

**Reglas Semánticas Implementadas:**

#### Ariel (2 reglas):
1. **Inmutabilidad de `let`**: Variables declaradas con `let` no pueden ser reasignadas
   ```swift
   let x = 5
   x = 10  // ❌ Error: 'x' es inmutable
   ```

2. **Compatibilidad de Tipos**: Los tipos deben ser compatibles en asignaciones y operaciones
   ```swift
   var x: Int = "texto"  // ❌ Error: tipo incompatible
   ```

#### Ayman (2 reglas):
3. **Validación de Tipos Primitivos**: Literales deben corresponder a tipos válidos
   ```swift
   let x: Int = 3.14  // ❌ Error: Double no es Int
   ```

4. **Tipos de Diccionarios**: Las claves y valores deben ser de tipos permitidos
   ```swift
   let datos: [String:Int] = ["edad": true]  // ❌ Error: tipo de valor incorrecto
   ```

#### Jordan (2 reglas):
5. **Condiciones Booleanas**: Las condiciones de `if` y `while` deben ser booleanas
   ```swift
   if 5 {  // ❌ Error: condición no booleana
       print("test")
   }
   ```

6. **Variables Declaradas**: No se pueden usar variables sin declarar
   ```swift
   print(x)  // ❌ Error: 'x' no declarada
   ```

**Errores Semánticos Detectados:**
- Variable no declarada antes de uso
- Reasignación de variable inmutable
- Incompatibilidad de tipos
- Operaciones inválidas entre tipos
- Condiciones no booleanas
- Redeclaración de variables en el mismo ámbito

## 🧪 Algoritmos de Prueba

Cada integrante tiene algoritmos de prueba específicos:

### 1. `algoritmo_comentarios_y_palabrasReservadas.swift` (Jordan)
Prueba:
- Palabras reservadas de Swift
- Comentarios de línea `//`
- Comentarios multilínea `/* */`

### 2. `algoritmosprimitivos.swift` (Ayman)
Prueba:
- Tipos primitivos: Int, Float, Double, Bool, String, Character
- Arrays y diccionarios
- Delimitadores

### 3. `algoritmo_identificadores_y_operadores.swift` (Ariel)
Prueba:
- Identificadores y variables
- Operadores aritméticos y lógicos
- Funciones con parámetros por defecto
- Tuplas
- Bucles `while`

### 4. `algoritmo_if_arrays_funcion.swift` (Jordan)
Prueba:
- Condicionales `if-else` anidados
- Arrays y acceso a elementos
- Funciones con retorno

### 5. `algoritmo_conversion_retorno.swift`
Prueba:
- Conversión de tipos
- Funciones con diferentes tipos de retorno

## 📊 Logs Generados

Los logs se generan automáticamente en la carpeta `logs/` con el siguiente formato:

```
analisis_[analizador]-[usuario]-[YYYYMMDD]-[HHhMM].txt
```

**Ejemplos:**
- `analisis_completo-ArielAT123-20251127-16h30.txt`
- `analisis_ayman-AymanElS4-20251127-16h35.txt`
- `sintactico_jordan-jorssanc-20251127-16h40.txt`

**Contenido del Log:**
- Fecha y hora del análisis
- Usuario que ejecutó el análisis
- Estadísticas de tokens (si aplica)
- Lista de errores léxicos
- Lista de errores sintácticos
- Lista de errores semánticos
- Tabla de símbolos (si aplica)
- Resumen final

## 🎨 Características de la Interfaz Gráfica

- ✅ **Tema Oscuro Profesional**: Diseño moderno inspirado en VS Code
- ✅ **Editor con Números de Línea**: Mejor visualización del código
- ✅ **Pestañas Organizadas**: Resultados separados por categoría
- ✅ **Selector de Analizador**: Elegir entre 3 analizadores diferentes
- ✅ **Barra de Estado**: Información en tiempo real
- ✅ **Guardado/Apertura**: Manejo completo de archivos
- ✅ **Logs Automáticos**: Guardado tras cada análisis
- ✅ **Código de Ejemplo**: Carga rápida de ejemplo funcional
- ✅ **Contador de Líneas/Caracteres**: Estadísticas del código

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'ply'"
**Solución**: 
```bash
pip install ply
```

### Error: "ImportError: No module named '_tkinter'"
**Solución**:
- **Windows**: Reinstalar Python con tkinter
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: Ya incluido con Python

### La interfaz no muestra resultados
**Solución**: 
1. Verifique que todos los archivos estén en las carpetas correctas:
   - `codigo/ArielArchivos/`
   - `codigo/Aymanarchivos/`
   - `codigo/JordanArchivos/`
2. Reinstale las dependencias: `pip install -r requirements.txt`

### Errores al importar módulos
**Solución**:
```bash
# Asegúrese de estar en la carpeta del proyecto
cd "Proyecto-LP-Analizador"
python interfaz_grafica.py
```

### Archivo parsetab.py genera errores
**Solución**: Elimine todos los archivos `parsetab.py` y `parser.out`, se regenerarán automáticamente

## 📦 Crear .ZIP para Entrega

Para crear el archivo .zip del proyecto completo:

```bash
python crear_zip.py
```

Esto generará: `Proyecto-LP-Analizador-Swift_[FECHA].zip`

El archivo .zip incluirá:
- ✅ Código fuente completo
- ✅ Interfaz gráfica
- ✅ Algoritmos de prueba
- ✅ Logs existentes
- ✅ README.md y documentación
- ✅ requirements.txt

## 📞 Integrantes

- **Ariel Arias Tipán** (ArielAT123)
- **Ayman El Salous** (AymanElS4)
- **Jordan Sánchez** (jorssanc)

---

**Proyecto de Lenguajes de Programación**  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
