#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERFAZ GRÁFICA DEL ANALIZADOR LÉXICO, SINTÁCTICO Y SEMÁNTICO
Proyecto de Lenguajes de Programación - Swift Analyzer
Integra los analizadores de: Ariel, Ayman y Jordan
EJECUTA TODOS LOS ANALIZADORES SIMULTÁNEAMENTE
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
from datetime import datetime

# Configurar paths para importar los módulos
proyecto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'ArielArchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'Aymanarchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'JordanArchivos'))


class AnalizadorGUI:
    """Interfaz gráfica principal del analizador"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Swift - Proyecto LP")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Configurar estilo
        self.setup_styles()
        
        # Variables
        self.current_file = None
        self.usuario_git = tk.StringVar(value="usuario")
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar ejemplo al inicio
        self.load_example()
        
    def setup_styles(self):
        """Configurar estilos visuales de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos para los frames
        style.configure('TFrame', background='#2b2b2b')
        style.configure('Header.TFrame', background='#1e1e1e')
        
        # Estilos para labels
        style.configure('Title.TLabel', 
                       background='#1e1e1e', 
                       foreground='#61dafb',
                       font=('Segoe UI', 18, 'bold'))
        style.configure('Subtitle.TLabel',
                       background='#1e1e1e',
                       foreground='#a0a0a0',
                       font=('Segoe UI', 10))
        style.configure('TLabel', 
                       background='#2b2b2b', 
                       foreground='#ffffff',
                       font=('Segoe UI', 10))
        
        # Estilos para botones
        style.configure('Primary.TButton',
                       background='#61dafb',
                       foreground='#000000',
                       font=('Segoe UI', 11, 'bold'),
                       padding=12)
        style.map('Primary.TButton',
                 background=[('active', '#4fa8c5')])
        
        style.configure('TButton',
                       background='#3c3c3c',
                       foreground='#ffffff',
                       font=('Segoe UI', 10),
                       padding=8)
        style.map('TButton',
                 background=[('active', '#505050')])
        
        # Estilos para el notebook (pestañas)
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#3c3c3c',
                       foreground='#ffffff',
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', '#61dafb')],
                 foreground=[('selected', '#000000')])
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame de encabezado
        header_frame = ttk.Frame(self.root, style='Header.TFrame', padding=20)
        header_frame.pack(fill='x')
        
        title_label = ttk.Label(header_frame, 
                               text="🔍 Analizador de Swift - Proyecto de LP",
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                   text="Análisis Completo con los 3 Analizadores | Ariel + Ayman + Jordan",
                                   style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Frame principal con dos columnas
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # ==================== COLUMNA IZQUIERDA - EDITOR ====================
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Toolbar con opciones
        toolbar_frame = ttk.Frame(left_frame)
        toolbar_frame.pack(fill='x', pady=5)
        
        ttk.Button(toolbar_frame, text="📂 Abrir", 
                  command=self.open_file).pack(side='left', padx=3)
        ttk.Button(toolbar_frame, text="💾 Guardar", 
                  command=self.save_file).pack(side='left', padx=3)
        ttk.Button(toolbar_frame, text="🆕 Nuevo", 
                  command=self.new_file).pack(side='left', padx=3)
        ttk.Button(toolbar_frame, text="📝 Ejemplo", 
                  command=self.load_example).pack(side='left', padx=3)
        
        # Usuario Git
        user_frame = ttk.Frame(toolbar_frame)
        user_frame.pack(side='right', padx=5)
        ttk.Label(user_frame, text="Usuario:").pack(side='left', padx=3)
        user_entry = ttk.Entry(user_frame, textvariable=self.usuario_git, width=15)
        user_entry.pack(side='left')
        
        # Editor de código
        editor_label = ttk.Label(left_frame, text="💻 Editor de Código Swift")
        editor_label.pack(anchor='w', pady=5)
        
        # Frame para el editor con números de línea
        editor_container = ttk.Frame(left_frame)
        editor_container.pack(fill='both', expand=True)
        
        # Números de línea
        self.line_numbers = tk.Text(
            editor_container,
            width=4,
            font=('Consolas', 11),
            bg='#1a1a1a',
            fg='#858585',
            relief='flat',
            state='disabled',
            takefocus=0
        )
        self.line_numbers.pack(side='left', fill='y')
        
        # Editor principal
        self.code_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white',
            selectbackground='#264f78',
            relief='flat',
            padx=10,
            pady=10,
            undo=True,
            maxundo=-1
        )
        self.code_editor.pack(side='left', fill='both', expand=True)
        
        # Bind para actualizar números de línea
        self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.update_line_numbers)
        
        # Botón de análisis grande
        analyze_btn = ttk.Button(left_frame, 
                                text="▶️ ANALIZAR CON LOS 3 ANALIZADORES",
                                style='Primary.TButton',
                                command=self.analyze_code)
        analyze_btn.pack(fill='x', pady=10)
        
        # ==================== COLUMNA DERECHA - RESULTADOS ====================
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        results_label = ttk.Label(right_frame, text="📊 Resultados del Análisis Completo")
        results_label.pack(anchor='w', pady=5)
        
        # Notebook para pestañas de resultados
        self.results_notebook = ttk.Notebook(right_frame)
        self.results_notebook.pack(fill='both', expand=True)
        
        # Pestaña: Resumen General
        self.summary_text = self.create_result_tab("📋 Resumen General")
        
        # Pestaña: Ariel 
        self.ariel_text = self.create_result_tab("👤 Ariel ")
        
        # Pestaña: Ayman
        self.ayman_text = self.create_result_tab("👤 Ayman")
        
        # Pestaña: Jordan
        self.jordan_text = self.create_result_tab("👤 Jordan")
        
        # Pestaña: Todos los Tokens
        self.tokens_text = self.create_result_tab("🔤 Todos los Tokens")
        
        # Pestaña: AST
        self.ast_text = self.create_result_tab("🌳 AST")
        
        # Barra de estado
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_bar = ttk.Label(status_frame, 
                                    text="✅ Listo - Ejecutará los 3 analizadores simultáneamente",
                                    relief='sunken',
                                    anchor='w',
                                    padding=5)
        self.status_bar.pack(side='left', fill='x', expand=True)
        
        self.status_info = ttk.Label(status_frame,
                                     text="Líneas: 0 | Caracteres: 0",
                                     relief='sunken',
                                     anchor='e',
                                     padding=5)
        self.status_info.pack(side='right')
        
    def create_result_tab(self, title):
        """Crear una pestaña con un área de texto para resultados"""
        frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(frame, text=title)
        
        text_area = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            relief='flat',
            padx=15,
            pady=15,
            state='normal'
        )
        text_area.pack(fill='both', expand=True)
        
        # Tags para colores
        text_area.tag_config('success', foreground='#4ec9b0')
        text_area.tag_config('error', foreground='#f48771')
        text_area.tag_config('warning', foreground='#dcdcaa')
        text_area.tag_config('info', foreground='#9cdcfe')
        text_area.tag_config('header', foreground='#61dafb', font=('Consolas', 11, 'bold'))
        text_area.tag_config('title', foreground='#c586c0', font=('Consolas', 12, 'bold'))
        
        return text_area
    
    def update_line_numbers(self, event=None):
        """Actualizar números de línea"""
        lines = self.code_editor.get('1.0', 'end').count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        
        # Actualizar info
        content = self.code_editor.get('1.0', 'end-1c')
        lines_count = content.count('\n') + 1 if content else 0
        chars_count = len(content)
        self.status_info.config(text=f"Líneas: {lines_count} | Caracteres: {chars_count}")
    
    def load_example(self):
        """Cargar un ejemplo de código Swift"""
        example_code = """// Ejemplo de código Swift para análisis completo
import Foundation

// Variables y constantes
var numero: Int = 42
let mensaje: String = "Hola Swift"
var resultado: Double = 3.14159

// Función con parámetros
func sumar(a: Int, b: Int) -> Int {
    return a + b
}

// Condicionales
if numero > 0 {
    print("Número positivo")
} else {
    print("Número negativo")
}

// Bucles
var contador = 5
while contador > 0 {
    print(contador)
    contador = contador - 1
}

// Arrays
let numeros: [Int] = [1, 2, 3, 4, 5]
for item in 0...4 {
    print(numeros)
}

// Diccionarios
let datos: [String:Int] = ["edad": 25, "año": 2025]

// Clase
class Persona {
    var nombre: String = "Juan"
    var edad: Int = 25
}

let persona = Persona()
print(persona.nombre)
"""
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', example_code)
        self.update_line_numbers()
        self.status_bar.config(text="📝 Código de ejemplo cargado")
    
    def open_file(self):
        """Abrir un archivo Swift"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Swift",
            filetypes=[("Swift files", "*.swift"), ("All files", "*.*")],
            initialdir=os.path.join(proyecto_dir, "algoritmos")
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.code_editor.delete(1.0, tk.END)
                    self.code_editor.insert(1.0, content)
                    self.current_file = file_path
                    self.update_line_numbers()
                    self.status_bar.config(text=f"📂 Cargado: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir:\n{str(e)}")
    
    def save_file(self):
        """Guardar el código actual"""
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                title="Guardar archivo",
                defaultextension=".swift",
                filetypes=[("Swift files", "*.swift"), ("All files", "*.*")]
            )
        
        if self.current_file:
            try:
                content = self.code_editor.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.config(text=f"💾 Guardado: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    def new_file(self):
        """Crear un nuevo archivo"""
        if messagebox.askyesno("Nuevo archivo", "¿Limpiar el editor?"):
            self.code_editor.delete(1.0, tk.END)
            self.current_file = None
            self.update_line_numbers()
            self.clear_results()
            self.status_bar.config(text="🆕 Nuevo archivo")
    
    def clear_results(self):
        """Limpiar todas las pestañas de resultados"""
        for text_widget in [self.summary_text, self.ariel_text, self.ayman_text,
                           self.jordan_text, self.tokens_text, self.ast_text]:
            text_widget.delete(1.0, tk.END)
    
    def analyze_code(self):
        """Analizar el código con LOS 3 ANALIZADORES"""
        codigo = self.code_editor.get(1.0, tk.END).strip()
        
        if not codigo:
            messagebox.showwarning("Sin código", "No hay código para analizar")
            return
        
        # Limpiar resultados anteriores
        self.clear_results()
        
        self.status_bar.config(text="⏳ Analizando con los 3 analizadores...")
        self.root.update()
        
        # Resultados de cada analizador
        results = {
            'ariel': {'success': False, 'tokens': [], 'lex_errors': [], 'syn_errors': [], 'sem_errors': [], 'ast': None},
            'ayman': {'success': False, 'parse_errors': [], 'sem_errors': [], 'ast': None, 'tabla': None},
            'jordan': {'success': False, 'syn_errors': [], 'ast': None}
        }
        
        # ============ ANALIZAR CON ARIEL ============
        try:
            from analizadorLexicoArielAAT123 import (
                analizador_lexico, errores_lexicos, tokens_reconocidos
            )
            from analizadorSemantico import (
                analizador_sintactico, errores_sintacticos, AnalizadorSemantico
            )
            
            errores_lexicos.clear()
            tokens_reconocidos.clear()
            errores_sintacticos.clear()
            
            lexer = analizador_lexico
            parser = analizador_sintactico
            lexer.lineno = 1
            ast = parser.parse(codigo, lexer=lexer)
            
            sem = AnalizadorSemantico()
            if ast:
                sem.verificar(ast)
            
            results['ariel'] = {
                'success': True,
                'tokens': list(tokens_reconocidos),
                'lex_errors': list(errores_lexicos),
                'syn_errors': list(errores_sintacticos),
                'sem_errors': list(sem.errores),
                'ast': ast
            }
        except Exception as e:
            results['ariel']['error'] = str(e)
        
        # ============ ANALIZAR CON AYMAN ============
        try:
            from analizador_swift import (
                parser as ayman_parser, lexer as ayman_lexer,
                semantic_errors, parse_errors, tabla_simbolos
            )
            
            semantic_errors.clear()
            parse_errors.clear()
            tabla_simbolos["scopes"] = [{}]
            tabla_simbolos["scopes"][0]["print"] = "BuiltInFunction"
            tabla_simbolos["scopes"][0]["readLine"] = "BuiltInFunction"
            
            ast_ayman = ayman_parser.parse(codigo, lexer=ayman_lexer)
            
            results['ayman'] = {
                'success': True,
                'parse_errors': list(parse_errors),
                'sem_errors': list(semantic_errors),
                'ast': ast_ayman,
                'tabla': dict(tabla_simbolos)
            }
        except Exception as e:
            results['ayman']['error'] = str(e)
        
        # ============ ANALIZAR CON JORDAN ============
        try:
            from sintactico_jordan import (
                parser as jordan_parser, lexer as jordan_lexer, syntax_errors
            )
            
            syntax_errors.clear()
            jordan_lexer.lineno = 1
            
            ast_jordan = jordan_parser.parse(codigo, lexer=jordan_lexer)
            
            results['jordan'] = {
                'success': True,
                'syn_errors': list(syntax_errors),
                'ast': ast_jordan
            }
        except Exception as e:
            results['jordan']['error'] = str(e)
        
        # ============ MOSTRAR RESULTADOS ============
        self.display_all_results(results)
        self.generate_combined_log(results)
        
        self.status_bar.config(text="✅ Análisis completado con los 3 analizadores")
    
    def display_all_results(self, results):
        """Mostrar resultados de los 3 analizadores"""
        
        # ============ RESUMEN GENERAL ============
        summary = f"""{'='*80}
RESUMEN GENERAL - ANÁLISIS CON LOS 3 ANALIZADORES
{'='*80}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Usuario: {self.usuario_git.get()}

"""
        
        # Estadísticas de Ariel
        if results['ariel']['success']:
            ariel_total = (len(results['ariel']['lex_errors']) + 
                          len(results['ariel']['syn_errors']) + 
                          len(results['ariel']['sem_errors']))
            summary += f"""┌─ ANALIZADOR DE ARIEL (Completo) ─────────────────────────────────┐
│ • Tokens reconocidos: {len(results['ariel']['tokens'])}
│ • Errores léxicos: {len(results['ariel']['lex_errors'])}
│ • Errores sintácticos: {len(results['ariel']['syn_errors'])}
│ • Errores semánticos: {len(results['ariel']['sem_errors'])}
│ • TOTAL DE ERRORES: {ariel_total}
└───────────────────────────────────────────────────────────────────┘

"""
        else:
            summary += f"""┌─ ANALIZADOR DE ARIEL ─────────────────────────────────────────────┐
│ ❌ Error al ejecutar: {results['ariel'].get('error', 'Desconocido')}
└───────────────────────────────────────────────────────────────────┘

"""
        
        # Estadísticas de Ayman
        if results['ayman']['success']:
            ayman_total = len(results['ayman']['parse_errors']) + len(results['ayman']['sem_errors'])
            summary += f"""┌─ ANALIZADOR DE AYMAN ─────────────────────────────────────────────┐
│ • Errores sintácticos (parser): {len(results['ayman']['parse_errors'])}
│ • Errores semánticos: {len(results['ayman']['sem_errors'])}
│ • TOTAL DE ERRORES: {ayman_total}
└───────────────────────────────────────────────────────────────────┘

"""
        else:
            summary += f"""┌─ ANALIZADOR DE AYMAN ─────────────────────────────────────────────┐
│ ❌ Error al ejecutar: {results['ayman'].get('error', 'Desconocido')}
└───────────────────────────────────────────────────────────────────┘

"""
        
        # Estadísticas de Jordan
        if results['jordan']['success']:
            jordan_total = len(results['jordan']['syn_errors'])
            summary += f"""┌─ ANALIZADOR DE JORDAN ────────────────────────────────────────────┐
│ • Errores sintácticos: {len(results['jordan']['syn_errors'])}
│ • TOTAL DE ERRORES: {jordan_total}
└───────────────────────────────────────────────────────────────────┘

"""
        else:
            summary += f"""┌─ ANALIZADOR DE JORDAN ────────────────────────────────────────────┐
│ ❌ Error al ejecutar: {results['jordan'].get('error', 'Desconocido')}
└───────────────────────────────────────────────────────────────────┘

"""
        
        # Total general
        total_general = 0
        if results['ariel']['success']:
            total_general += (len(results['ariel']['lex_errors']) + 
                            len(results['ariel']['syn_errors']) + 
                            len(results['ariel']['sem_errors']))
        if results['ayman']['success']:
            total_general += len(results['ayman']['parse_errors']) + len(results['ayman']['sem_errors'])
        if results['jordan']['success']:
            total_general += len(results['jordan']['syn_errors'])
        
        summary += f"""{'='*80}
TOTAL GENERAL DE ERRORES ENCONTRADOS: {total_general}
{'='*80}
"""
        
        self.summary_text.insert('1.0', summary)
        
        # ============ PESTAÑA ARIEL ============
        if results['ariel']['success']:
            ariel_text = f"""ANÁLISIS COMPLETO - ARIEL ARIAS TIPÁN
{'='*80}

✅ TOKENS RECONOCIDOS: {len(results['ariel']['tokens'])}
{'-'*80}
"""
            if results['ariel']['tokens']:
                for i, tok in enumerate(results['ariel']['tokens'][:100], 1):  # Limitar a 100
                    ariel_text += f"{i:4d}. Línea {tok.lineno:3d}: {tok.type:18s} → {repr(tok.value)}\n"
                if len(results['ariel']['tokens']) > 100:
                    ariel_text += f"\n... y {len(results['ariel']['tokens']) - 100} tokens más\n"
            
            ariel_text += f"\n\n❌ ERRORES LÉXICOS: {len(results['ariel']['lex_errors'])}\n{'-'*80}\n"
            if results['ariel']['lex_errors']:
                ariel_text += '\n'.join(results['ariel']['lex_errors'])
            else:
                ariel_text += "✅ Sin errores léxicos"
            
            ariel_text += f"\n\n❌ ERRORES SINTÁCTICOS: {len(results['ariel']['syn_errors'])}\n{'-'*80}\n"
            if results['ariel']['syn_errors']:
                ariel_text += '\n'.join(results['ariel']['syn_errors'])
            else:
                ariel_text += "✅ Sin errores sintácticos"
            
            ariel_text += f"\n\n❌ ERRORES SEMÁNTICOS: {len(results['ariel']['sem_errors'])}\n{'-'*80}\n"
            if results['ariel']['sem_errors']:
                ariel_text += '\n'.join(results['ariel']['sem_errors'])
            else:
                ariel_text += "✅ Sin errores semánticos"
            
            self.ariel_text.insert('1.0', ariel_text)
        else:
            self.ariel_text.insert('1.0', f"❌ Error: {results['ariel'].get('error', 'Desconocido')}")
        
        # ============ PESTAÑA AYMAN ============
        if results['ayman']['success']:
            ayman_text = f"""ANÁLISIS - AYMAN EL SALOUS
{'='*80}

❌ ERRORES SINTÁCTICOS (PARSER): {len(results['ayman']['parse_errors'])}
{'-'*80}
"""
            if results['ayman']['parse_errors']:
                ayman_text += '\n'.join(results['ayman']['parse_errors'])
            else:
                ayman_text += "✅ Sin errores sintácticos"
            
            ayman_text += f"\n\n❌ ERRORES SEMÁNTICOS: {len(results['ayman']['sem_errors'])}\n{'-'*80}\n"
            if results['ayman']['sem_errors']:
                ayman_text += '\n'.join(results['ayman']['sem_errors'])
            else:
                ayman_text += "✅ Sin errores semánticos"
            
            ayman_text += f"\n\n📋 TABLA DE SÍMBOLOS:\n{'-'*80}\n"
            if results['ayman']['tabla']:
                for k, v in results['ayman']['tabla']['scopes'][0].items():
                    ayman_text += f"  {k:25s} : {v}\n"
            
            self.ayman_text.insert('1.0', ayman_text)
        else:
            self.ayman_text.insert('1.0', f"❌ Error: {results['ayman'].get('error', 'Desconocido')}")
        
        # ============ PESTAÑA JORDAN ============
        if results['jordan']['success']:
            jordan_text = f"""ANÁLISIS SINTÁCTICO - JORDAN SÁNCHEZ
{'='*80}

❌ ERRORES SINTÁCTICOS: {len(results['jordan']['syn_errors'])}
{'-'*80}
"""
            if results['jordan']['syn_errors']:
                jordan_text += '\n'.join(results['jordan']['syn_errors'])
            else:
                jordan_text += "✅ Sin errores sintácticos"
            
            self.jordan_text.insert('1.0', jordan_text)
        else:
            self.jordan_text.insert('1.0', f"❌ Error: {results['jordan'].get('error', 'Desconocido')}")
        
        # ============ TODOS LOS TOKENS ============
        if results['ariel']['success'] and results['ariel']['tokens']:
            tokens_text = f"TODOS LOS TOKENS RECONOCIDOS (Ariel)\nTotal: {len(results['ariel']['tokens'])}\n{'='*80}\n\n"
            for i, tok in enumerate(results['ariel']['tokens'], 1):
                tokens_text += f"{i:4d}. Línea {tok.lineno:3d}: {tok.type:18s} → {repr(tok.value)}\n"
            self.tokens_text.insert('1.0', tokens_text)
        else:
            self.tokens_text.insert('1.0', "No hay tokens disponibles")
        
        # ============ AST ============
        ast_text = "ÁRBOLES DE SINTAXIS ABSTRACTA\n" + "="*80 + "\n\n"
        if results['ariel']['success'] and results['ariel']['ast']:
            ast_text += f"AST DE ARIEL:\n{'-'*80}\n{repr(results['ariel']['ast'])[:2000]}\n\n"
        if results['ayman']['success'] and results['ayman']['ast']:
            ast_text += f"AST DE AYMAN:\n{'-'*80}\n{repr(results['ayman']['ast'])[:2000]}\n\n"
        if results['jordan']['success'] and results['jordan']['ast']:
            ast_text += f"AST DE JORDAN:\n{'-'*80}\n{repr(results['jordan']['ast'])[:2000]}\n\n"
        
        self.ast_text.insert('1.0', ast_text)
        
        # Seleccionar pestaña de resumen
        self.results_notebook.select(0)
    
    def generate_combined_log(self, results):
        """Generar log combinado de los 3 analizadores"""
        try:
            os.makedirs("logs", exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d-%Hh%M')
            usuario = self.usuario_git.get()
            log_file = f"logs/analisis_completo_3_analizadores-{usuario}-{timestamp}.txt"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("ANÁLISIS COMPLETO CON LOS 3 ANALIZADORES\n")
                f.write("="*80 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Usuario: {usuario}\n")
                f.write("="*80 + "\n\n")
                
                # Ariel
                if results['ariel']['success']:
                    f.write("┌─ ANALIZADOR DE ARIEL ─────────────────────────────────┐\n")
                    f.write(f"│ Tokens: {len(results['ariel']['tokens'])}\n")
                    f.write(f"│ Errores léxicos: {len(results['ariel']['lex_errors'])}\n")
                    f.write(f"│ Errores sintácticos: {len(results['ariel']['syn_errors'])}\n")
                    f.write(f"│ Errores semánticos: {len(results['ariel']['sem_errors'])}\n")
                    f.write("└───────────────────────────────────────────────────────┘\n\n")
                    
                    if results['ariel']['lex_errors']:
                        f.write("ERRORES LÉXICOS:\n" + "-"*80 + "\n")
                        f.write('\n'.join(results['ariel']['lex_errors']) + "\n\n")
                    if results['ariel']['syn_errors']:
                        f.write("ERRORES SINTÁCTICOS:\n" + "-"*80 + "\n")
                        f.write('\n'.join(results['ariel']['syn_errors']) + "\n\n")
                    if results['ariel']['sem_errors']:
                        f.write("ERRORES SEMÁNTICOS:\n" + "-"*80 + "\n")
                        f.write('\n'.join(results['ariel']['sem_errors']) + "\n\n")
                
                # Ayman
                if results['ayman']['success']:
                    f.write("┌─ ANALIZADOR DE AYMAN ─────────────────────────────────┐\n")
                    f.write(f"│ Errores sintácticos: {len(results['ayman']['parse_errors'])}\n")
                    f.write(f"│ Errores semánticos: {len(results['ayman']['sem_errors'])}\n")
                    f.write("└───────────────────────────────────────────────────────┘\n\n")
                    
                    if results['ayman']['parse_errors']:
                        f.write("ERRORES SINTÁCTICOS:\n" + "-"*80 + "\n")
                        f.write('\n'.join(results['ayman']['parse_errors']) + "\n\n")
                    if results['ayman']['sem_errors']:
                        f.write("ERRORES SEMÁNTICOS:\n" + "-"*80 + "\n")
                        f.write('\n'.join(results['ayman']['sem_errors']) + "\n\n")
                
                # Jordan
                if results['jordan']['success']:
                    f.write("┌─ ANALIZADOR DE JORDAN ────────────────────────────────┐\n")
                    f.write(f"│ Errores sintácticos: {len(results['jordan']['syn_errors'])}\n")
                    f.write("└───────────────────────────────────────────────────────┘\n\n")
                    
                    if results['jordan']['syn_errors']:
                        f.write("ERRORES SINTÁCTICOS:\n" + "-"*80 + "\n")
                        f.write('\n'.join(results['jordan']['syn_errors']) + "\n\n")
            
            print(f"✅ Log generado: {log_file}")
        except Exception as e:
            print(f"Error generando log: {e}")


def main():
    """Función principal"""
    root = tk.Tk()
    app = AnalizadorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
