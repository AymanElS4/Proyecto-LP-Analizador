# 🚀 GUÍA RÁPIDA DE INICIO - ANALIZADOR UNIFICADO

## Instalación en 3 Pasos

### 1️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2️⃣ Ejecutar la Interfaz Gráfica Unificada
```bash
python interfaz_grafica.py
```

### 3️⃣ Analizar Código
1. El código de ejemplo ya está cargado
2. Click en "▶️ ANALIZAR (Consenso de 3 Analizadores)"
3. Revisa los resultados en las pestañas:
   - **Resumen**: Errores confirmados por los 3
   - **Errores Detectados**: Solo errores con consenso
   - **Tokens**: Tokens reconocidos
   - **Detalles**: Vista individual de cada analizador

---

## 🎯 ¿Cómo Funciona el Consenso?

El analizador ejecuta **simultáneamente** los 3 analizadores (Ariel, Ayman, Jordan) y:

✅ **MUESTRA el error** → Si los 3 analizadores lo detectaron  
❌ **NO MUESTRA** → Si al menos 1 analizador NO lo detectó

**Principio**: Si al menos un integrante implementó bien esa parte, el código puede ejecutarse.

---

## ⚡ Acceso Rápido a Funcionalidades

### Análisis Rápido con Interfaz Gráfica
```bash
python interfaz_grafica.py
```

### Crear .zip para Entrega
```bash
python crear_zip.py
```

### Ejecutar Analizadores Individuales

**Léxico (Palabras Reservadas):**
```bash
python codigo/palabras_reservadas_comentarios.py
```

**Léxico (Primitivos):**
```bash
python codigo/primitivos_y_limitadores.py
```

**Completo (Léxico + Sintáctico + Semántico):**
```bash
python codigo/ArielArchivos/analizadorSintactico.py
```

---

## 🎯 Características Principales

- ✅ **Analizador Léxico**: Reconoce todos los tokens de Swift
- ✅ **Analizador Sintáctico**: Valida la gramática del código
- ✅ **Analizador Semántico**: Verifica tipos y reglas semánticas
- ✅ **Interfaz Gráfica**: Moderna y fácil de usar
- ✅ **Generación de Logs**: Automática en cada análisis
- ✅ **Algoritmos de Prueba**: Listos para demostración

---

## 📝 Estructura de Archivos Clave

```
📁 Proyecto-LP-Analizador/
  ├── 🎨 interfaz_grafica.py          ← ARCHIVO PRINCIPAL
  ├── 📖 README.md                     ← Documentación completa
  ├── 📦 requirements.txt              ← Dependencias
  ├── 🗜️ crear_zip.py                  ← Crear .zip para entrega
  │
  ├── 📁 codigo/                       ← Analizadores
  │   ├── palabras_reservadas_comentarios.py
  │   ├── primitivos_y_limitadores.py
  │   └── 📁 ArielArchivos/           ← Analizador completo
  │       ├── analizadorLexicoArielAAT123.py
  │       ├── analizadorSintactico.py
  │       └── analizadorSemantico.py
  │
  ├── 📁 algoritmos/                   ← Ejemplos de prueba
  │   ├── algoritmo_comentarios_y_palabrasReservadas.swift
  │   ├── algoritmo_identificadores_y_operadores.swift
  │   └── algoritmosprimitivos.swift
  │
  └── 📁 logs/                         ← Logs generados
```

---

## 🎓 Para Sustentación

### Ejemplos Recomendados por Integrante

**Ariel (ArielAT123):**
- Archivo: `algoritmo_identificadores_y_operadores.swift`
- Demuestra: Variables, funciones, while, tuplas

**Ayman (AymanElS4):**
- Archivo: `algoritmosprimitivos.swift`
- Demuestra: Tipos primitivos, delimitadores

**Jorge (jorssanc):**
- Archivo: `algoritmo_comentarios_y_palabrasReservadas.swift`
- Demuestra: Palabras reservadas, comentarios

### Ejemplos de Errores a Mostrar

**Error Léxico:**
```swift
var x = @123;  // Carácter ilegal '@'
```

**Error Sintáctico:**
```swift
var x = 5  // Falta punto y coma
```

**Error Semántico:**
```swift
let x = 5;
x = 10;  // Error: 'x' es inmutable (let)
```

---

## ❓ Solución Rápida de Problemas

### "No se encuentra el módulo ply"
```bash
pip install ply
```

### "No se encuentra tkinter"
**Windows:** Ya incluido  
**Linux:** `sudo apt-get install python3-tk`  
**macOS:** Ya incluido

### La interfaz no abre
```bash
# Verifica tu versión de Python
python --version

# Debe ser 3.7 o superior
```

### Errores de importación
```bash
# Asegúrate de estar en la carpeta del proyecto
cd "Proyecto-LP-Analizador"
python interfaz_grafica.py
```

---

## 📞 Soporte

Para problemas o preguntas:
- Ariel Arias Tipán (ArielAT123)
- Ayman El Salous (AymanElS4)
- Jorge Sánchez (jorssanc)

---

**¡Proyecto Listo para Entregar y Sustentar!** 🎉
