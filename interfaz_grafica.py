#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALIZADOR DE SWIFT - PROYECTO LP
Analizador completo desarrollado por el equipo
Combina las implementaciones de Ariel, Ayman y Jordan
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
from datetime import datetime

# Configurar paths
proyecto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'ArielArchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'Aymanarchivos'))
sys.path.insert(0, os.path.join(proyecto_dir, 'codigo', 'JordanArchivos'))


class AnalizadorSwift:
    """Analizador completo de Swift del equipo"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Swift - Proyecto LP")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        self.setup_styles()
        self.current_file = None
        self.usuario_git = tk.StringVar(value="equipo")
        
        self.create_widgets()
        self.load_example()
        
    def setup_styles(self):
        """Configurar estilos visuales"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#2b2b2b')
        style.configure('Header.TFrame', background='#1e1e1e')
        
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
        """Crear interfaz"""
        
        # Encabezado
        header_frame = ttk.Frame(self.root, style='Header.TFrame', padding=20)
        header_frame.pack(fill='x')
        
        ttk.Label(header_frame, 
                 text="🔍 Analizador de Swift",
                 style='Title.TLabel').pack()
        
        ttk.Label(header_frame,
                 text="Análisis Léxico, Sintáctico y Semántico | Ariel, Ayman, Jordan",
                 style='Subtitle.TLabel').pack()
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Editor
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill='x', pady=5)
        
        ttk.Button(toolbar, text="📂 Abrir", command=self.open_file).pack(side='left', padx=3)
        ttk.Button(toolbar, text="💾 Guardar", command=self.save_file).pack(side='left', padx=3)
        ttk.Button(toolbar, text="🆕 Nuevo", command=self.new_file).pack(side='left', padx=3)
        ttk.Button(toolbar, text="📝 Ejemplo", command=self.load_example).pack(side='left', padx=3)
        
        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side='right', padx=5)
        ttk.Label(user_frame, text="Usuario:").pack(side='left', padx=3)
        ttk.Entry(user_frame, textvariable=self.usuario_git, width=15).pack(side='left')
        
        ttk.Label(left_frame, text="💻 Editor de Código Swift").pack(anchor='w', pady=5)
        
        editor_container = ttk.Frame(left_frame)
        editor_container.pack(fill='both', expand=True)
        
        self.line_numbers = tk.Text(
            editor_container, width=4, font=('Consolas', 11),
            bg='#1a1a1a', fg='#858585', relief='flat',
            state='disabled', takefocus=0
        )
        self.line_numbers.pack(side='left', fill='y')
        
        self.code_editor = scrolledtext.ScrolledText(
            editor_container, wrap=tk.NONE, font=('Consolas', 11),
            bg='#1e1e1e', fg='#d4d4d4', insertbackground='white',
            selectbackground='#264f78', relief='flat',
            padx=10, pady=10, undo=True, maxundo=-1
        )
        self.code_editor.pack(side='left', fill='both', expand=True)
        
        self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.update_line_numbers)
        
        ttk.Button(left_frame, 
                  text="▶️ ANALIZAR CÓDIGO",
                  style='Primary.TButton',
                  command=self.analyze_code).pack(fill='x', pady=10)
        
        # Resultados
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        ttk.Label(right_frame, text="📊 Resultados del Análisis").pack(anchor='w', pady=5)
        
        self.results_notebook = ttk.Notebook(right_frame)
        self.results_notebook.pack(fill='both', expand=True)
        
        self.summary_text = self.create_result_tab("📋 Resumen")
        self.errors_lexical = self.create_result_tab("🔴 Errores Léxicos")
        self.errors_syntax = self.create_result_tab("🔴 Errores Sintácticos")
        self.errors_semantic = self.create_result_tab("🔴 Errores Semánticos")
        self.tokens_text = self.create_result_tab("🔤 Tokens")
        
        # Barra de estado
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_bar = ttk.Label(status_frame, 
                                    text="✅ Listo para analizar código Swift",
                                    relief='sunken', anchor='w', padding=5)
        self.status_bar.pack(side='left', fill='x', expand=True)
        
        self.status_info = ttk.Label(status_frame,
                                     text="Líneas: 0 | Caracteres: 0",
                                     relief='sunken', anchor='e', padding=5)
        self.status_info.pack(side='right')
        
    def create_result_tab(self, title):
        """Crear pestaña de resultados"""
        frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(frame, text=title)
        
        text_area = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, font=('Consolas', 10),
            bg='#1e1e1e', fg='#d4d4d4', relief='flat',
            padx=15, pady=15
        )
        text_area.pack(fill='both', expand=True)
        
        text_area.tag_config('success', foreground='#4ec9b0')
        text_area.tag_config('error', foreground='#f48771')
        text_area.tag_config('warning', foreground='#dcdcaa')
        text_area.tag_config('info', foreground='#9cdcfe')
        
        return text_area
    
    def update_line_numbers(self, event=None):
        """Actualizar números de línea"""
        lines = self.code_editor.get('1.0', 'end').count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        
        content = self.code_editor.get('1.0', 'end-1c')
        lines_count = content.count('\n') + 1 if content else 0
        chars_count = len(content)
        self.status_info.config(text=f"Líneas: {lines_count} | Caracteres: {chars_count}")
    
    def load_example(self):
        """Cargar ejemplo"""
        example = """// Ejemplo basico de Swift

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
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', example)
        self.update_line_numbers()
        self.status_bar.config(text="📝 Ejemplo cargado")
    
    def open_file(self):
        """Abrir archivo"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Swift",
            filetypes=[("Swift files", "*.swift"), ("All files", "*.*")],
            initialdir=os.path.join(proyecto_dir, "algoritmos")
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.code_editor.delete(1.0, tk.END)
                    self.code_editor.insert(1.0, f.read())
                    self.current_file = file_path
                    self.update_line_numbers()
                    self.status_bar.config(text=f"📂 {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir:\n{str(e)}")
    
    def save_file(self):
        """Guardar archivo"""
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".swift",
                filetypes=[("Swift files", "*.swift"), ("All files", "*.*")]
            )
        
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.get(1.0, tk.END))
                self.status_bar.config(text=f"💾 Guardado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    def new_file(self):
        """Nuevo archivo"""
        if messagebox.askyesno("Nuevo", "¿Limpiar editor?"):
            self.code_editor.delete(1.0, tk.END)
            self.current_file = None
            self.clear_results()
            self.update_line_numbers()
    
    def clear_results(self):
        """Limpiar resultados"""
        for text in [self.summary_text, self.errors_lexical, self.errors_syntax, 
                    self.errors_semantic, self.tokens_text]:
            text.delete(1.0, tk.END)
    
    def analyze_code(self):
        """Analizar código Swift con módulo unificado de consenso"""
        codigo = self.code_editor.get(1.0, tk.END).strip()
        
        if not codigo:
            messagebox.showwarning("Sin código", "No hay código para analizar")
            return
        
        self.clear_results()
        self.status_bar.config(text="⏳ Analizando con el analizador de Ariel...")
        self.root.update()
        
        try:
            # Usar el módulo unificado
            from analizador_unificado import analizar_codigo
            
            resultados = analizar_codigo(codigo)
            
            # Convertir errores estandarizados a strings
            lex_errors = [str(e) for e in resultados['errores_lexicos']]
            syn_errors = [str(e) for e in resultados['errores_sintacticos']]
            sem_errors = [str(e) for e in resultados['errores_semanticos']]
            tokens = resultados['tokens']
            
            # Mostrar resultados
            self.display_combined_results(lex_errors, syn_errors, sem_errors, tokens)
            self.generate_log(lex_errors, syn_errors, sem_errors, tokens)
            
            total = len(lex_errors) + len(syn_errors) + len(sem_errors)
            if total == 0:
                self.status_bar.config(text=f"✅ Sin errores - Código válido")
            else:
                self.status_bar.config(text=f"✅ Análisis completado - {total} errores detectados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis:\n{str(e)}")
            import traceback
            traceback.print_exc()
            self.status_bar.config(text="❌ Error en el análisis")
    
    def display_combined_results(self, lex_errors, syn_errors, sem_errors, tokens):
        """Mostrar resultados del análisis"""
        
        total_errors = len(lex_errors) + len(syn_errors) + len(sem_errors)
        
        # RESUMEN
        summary = f"""{'='*80}
ANÁLISIS DE CÓDIGO SWIFT
{'='*80}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Usuario: {self.usuario_git.get()}

📊 ESTADÍSTICAS:
  • Tokens reconocidos: {len(tokens)}
  • Errores léxicos: {len(lex_errors)}
  • Errores sintácticos: {len(syn_errors)}
  • Errores semánticos: {len(sem_errors)}
  
{'='*80}
TOTAL DE ERRORES: {total_errors}
{'='*80}
"""
        
        if total_errors == 0:
            summary += "\n✅ ¡CÓDIGO SIN ERRORES!\nEl análisis fue exitoso.\n"
        else:
            summary += f"\n⚠️ Se encontraron {total_errors} error(es).\nRevise las pestañas de errores.\n"
        
        self.summary_text.insert('1.0', summary)
        
        # ERRORES LÉXICOS
        if lex_errors:
            lex_text = f"ERRORES LÉXICOS DETECTADOS\nTotal: {len(lex_errors)}\n{'='*80}\n\n"
            for i, err in enumerate(lex_errors, 1):
                lex_text += f"{i}. {err}\n"
        else:
            lex_text = "✅ NO SE DETECTARON ERRORES LÉXICOS\n\nTodos los caracteres y símbolos son válidos."
        
        self.errors_lexical.insert('1.0', lex_text)
        
        # ERRORES SINTÁCTICOS
        if syn_errors:
            syn_text = f"ERRORES SINTÁCTICOS DETECTADOS\nTotal: {len(syn_errors)}\n{'='*80}\n\n"
            for i, err in enumerate(syn_errors, 1):
                syn_text += f"{i}. {err}\n"
        else:
            syn_text = "✅ NO SE DETECTARON ERRORES SINTÁCTICOS\n\nLa estructura del código es correcta."
        
        self.errors_syntax.insert('1.0', syn_text)
        
        # ERRORES SEMÁNTICOS
        if sem_errors:
            sem_text = f"ERRORES SEMÁNTICOS DETECTADOS\nTotal: {len(sem_errors)}\n{'='*80}\n\n"
            for i, err in enumerate(sem_errors, 1):
                sem_text += f"{i}. {err}\n"
        else:
            sem_text = "✅ NO SE DETECTARON ERRORES SEMÁNTICOS\n\nLos tipos y alcances son correctos."
        
        self.errors_semantic.insert('1.0', sem_text)
        
        # TOKENS
        if tokens:
            tokens_text = f"TOKENS RECONOCIDOS\nTotal: {len(tokens)}\n{'='*80}\n\n"
            for i, tok in enumerate(tokens, 1):
                tokens_text += f"{i:4d}. Línea {tok.lineno:3d}: {tok.type:18s} → {repr(tok.value)}\n"
        else:
            tokens_text = "No se reconocieron tokens."
        
        self.tokens_text.insert('1.0', tokens_text)
        
        # Mostrar la pestaña apropiada
        if total_errors > 0:
            # Ir a la primera pestaña con errores
            if lex_errors:
                self.results_notebook.select(1)  # Errores léxicos
            elif syn_errors:
                self.results_notebook.select(2)  # Errores sintácticos
            elif sem_errors:
                self.results_notebook.select(3)  # Errores semánticos
        else:
            self.results_notebook.select(0)  # Resumen
    
    def generate_log(self, lex_errors, syn_errors, sem_errors, tokens):
        """Generar log del análisis"""
        try:
            os.makedirs("logs", exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d-%Hh%M')
            usuario = self.usuario_git.get()
            log_file = f"logs/analisis_swift-{usuario}-{timestamp}.txt"
            
            total_errors = len(lex_errors) + len(syn_errors) + len(sem_errors)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("ANÁLISIS DE CÓDIGO SWIFT\n")
                f.write("="*80 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Usuario: {usuario}\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Tokens reconocidos: {len(tokens)}\n")
                f.write(f"Errores léxicos: {len(lex_errors)}\n")
                f.write(f"Errores sintácticos: {len(syn_errors)}\n")
                f.write(f"Errores semánticos: {len(sem_errors)}\n")
                f.write(f"TOTAL DE ERRORES: {total_errors}\n\n")
                
                if lex_errors:
                    f.write("ERRORES LÉXICOS:\n" + "-"*80 + "\n")
                    for err in lex_errors:
                        f.write(f"  • {err}\n")
                    f.write("\n")
                
                if syn_errors:
                    f.write("ERRORES SINTÁCTICOS:\n" + "-"*80 + "\n")
                    for err in syn_errors:
                        f.write(f"  • {err}\n")
                    f.write("\n")
                
                if sem_errors:
                    f.write("ERRORES SEMÁNTICOS:\n" + "-"*80 + "\n")
                    for err in sem_errors:
                        f.write(f"  • {err}\n")
                    f.write("\n")
                
                if total_errors == 0:
                    f.write("✅ CÓDIGO SIN ERRORES\n")
            
            print(f"✅ Log generado: {log_file}")
            
        except Exception as e:
            print(f"Error generando log: {e}")


def main():
    """Función principal"""
    root = tk.Tk()
    app = AnalizadorSwift(root)
    root.mainloop()


if __name__ == "__main__":
    main()
