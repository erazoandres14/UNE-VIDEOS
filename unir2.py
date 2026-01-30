#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import subprocess
import os
import sys
from typing import Tuple


def get_ff_bins() -> Tuple[str, str]:
    """Devuelve las rutas a los ejecutables ffmpeg y ffprobe sin inicializar la GUI.

    Busca en la carpeta `ffmpeg_local/bin` relativa al script (o a sys._MEIPASS cuando
    está empaquetado con PyInstaller). Si no se encuentran, devuelve 'ffmpeg' y
    'ffprobe' para usar los binarios del PATH del sistema.
    """
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    ffmpeg_candidate = os.path.join(base_dir, 'ffmpeg_local', 'bin', 'ffmpeg')
    ffprobe_candidate = os.path.join(base_dir, 'ffmpeg_local', 'bin', 'ffprobe')

    if os.name == 'nt':
        if not os.path.exists(ffmpeg_candidate) and os.path.exists(ffmpeg_candidate + '.exe'):
            ffmpeg_candidate += '.exe'
        if not os.path.exists(ffprobe_candidate) and os.path.exists(ffprobe_candidate + '.exe'):
            ffprobe_candidate += '.exe'

    ffmpeg_bin = ffmpeg_candidate if os.path.exists(ffmpeg_candidate) else 'ffmpeg'
    ffprobe_bin = ffprobe_candidate if os.path.exists(ffprobe_candidate) else 'ffprobe'
    return ffmpeg_bin, ffprobe_bin
from PIL import Image, ImageTk
import threading

class VideoUnifier:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Unificador de Videos - Moderno")
        self.root.geometry("700x600")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Obtener rutas a ffmpeg/ffprobe (sin inicializar la GUI)
        self.ffmpeg_bin, self.ffprobe_bin = get_ff_bins()
        
        # Variables para almacenar los videos
        self.videos = [None, None, None]
        self.video_labels = []
        
        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🎬 UNIFICADOR DE VIDEOS",
            font=('Segoe UI', 24, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Une hasta 3 videos de forma rápida y eficiente",
            font=('Segoe UI', 12),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=5)
        
        # Frame principal para los slots de video
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        # Crear 3 slots para videos
        for i in range(3):
            self.create_video_slot(main_frame, i)
            
        # Frame para botones
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=30)
        
        # Botón para unir videos
        self.unir_button = tk.Button(
            button_frame,
            text="🚀 UNIR VIDEOS",
            font=('Segoe UI', 14, 'bold'),
            bg='#27ae60',
            fg='white', 
            relief='flat',
            padx=30,
            pady=10,
            command=self.unir_videos,
            cursor='hand2'
        )
        self.unir_button.pack()
        
        # Botón para limpiar
        clear_button = tk.Button(
            button_frame,
            text="🧹 LIMPIAR TODO",
            font=('Segoe UI', 12),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            command=self.limpiar_todo,
            cursor='hand2'
        )
        clear_button.pack(pady=10)
        
        # Frame para la barra de progreso
        progress_frame = tk.Frame(self.root, bg='#2c3e50')
        progress_frame.pack(pady=10)
        
        # Label para el progreso
        progress_label = tk.Label(
            progress_frame,
            text="Progreso:",
            font=('Segoe UI', 10, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        progress_label.pack(pady=5)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400,
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(pady=5)
        
        # Configurar estilo personalizado para la barra de progreso
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Custom.Horizontal.TProgressbar',
            troughcolor='#34495e',
            background='#27ae60',
            bordercolor='#2c3e50',
            lightcolor='#27ae60',
            darkcolor='#27ae60'
        )
        
        # Label de estado
        self.status_label = tk.Label(
            self.root,
            text="Listo para unir videos",
            font=('Segoe UI', 10),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        self.status_label.pack(pady=5)
        
        # Label de porcentaje
        self.percentage_label = tk.Label(
            self.root,
            text="0%",
            font=('Segoe UI', 12, 'bold'),
            fg='#27ae60',
            bg='#2c3e50'
        )
        self.percentage_label.pack(pady=5)
        
    def create_video_slot(self, parent, index):
        """Crea un slot para un video"""
        slot_frame = tk.Frame(parent, bg='#34495e', relief='raised', bd=2)
        slot_frame.pack(pady=10, fill='x', padx=10)
        
        # Header del slot
        header_frame = tk.Frame(slot_frame, bg='#34495e')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        slot_label = tk.Label(
            header_frame,
            text=f"Video {index + 1}",
            font=('Segoe UI', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        )
        slot_label.pack(side='left')
        
        # Botones del slot
        button_frame = tk.Frame(header_frame, bg='#34495e')
        button_frame.pack(side='right')
        
        add_button = tk.Button(
            button_frame,
            text="📁 Agregar",
            font=('Segoe UI', 9),
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=15,
            pady=5,
            command=lambda: self.agregar_video(index),
            cursor='hand2'
        )
        add_button.pack(side='left', padx=2)
        
        remove_button = tk.Button(
            button_frame,
            text="❌ Quitar",
            font=('Segoe UI', 9),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=15,
            pady=5,
            command=lambda: self.quitar_video(index),
            cursor='hand2'
        )
        remove_button.pack(side='left', padx=2)
        
        # Label para mostrar el video
        video_label = tk.Label(
            slot_frame,
            text="Ningún video seleccionado",
            font=('Segoe UI', 10),
            fg='#95a5a6',
            bg='#34495e',
            wraplength=500,
            justify='left'
        )
        video_label.pack(padx=10, pady=10, anchor='w')
        
        self.video_labels.append(video_label)
        
    def agregar_video(self, index):
        """Agrega un video al slot especificado"""
        archivo = filedialog.askopenfilename(
            title=f"Selecciona el video {index + 1}",
            filetypes=[
                ("Videos MP4", "*.mp4"),
                ("Videos AVI", "*.avi"),
                ("Videos MOV", "*.mov"),
                ("Todos los videos", "*.*")
            ]
        )
        
        if archivo:
            self.videos[index] = archivo
            nombre_archivo = os.path.basename(archivo)
            self.video_labels[index].config(
                text=f"✅ {nombre_archivo}",
                fg='#27ae60'
            )
            
    def quitar_video(self, index):
        """Quita un video del slot especificado"""
        self.videos[index] = None
        self.video_labels[index].config(
            text="Ningún video seleccionado",
            fg='#95a5a6'
        )
        
    def limpiar_todo(self):
        """Limpia todos los slots de video"""
        for i in range(3):
            self.videos[i] = None
            self.video_labels[i].config(
                text="Ningún video seleccionado",
                fg='#95a5a6'
            )
        self.status_label.config(text="Listo para unir videos")
        
    def unir_videos(self):
        """Une los videos seleccionados"""
        # Filtrar videos no nulos
        videos_validos = [v for v in self.videos if v is not None]
        
        if len(videos_validos) < 2:
            messagebox.showerror(
                "Error",
                "Debes seleccionar al menos 2 videos para unir"
            )
            return
            
        # Preguntar nombre de salida
        nombre = tk.simpledialog.askstring(
            "Nombre de salida",
            "Escribe el nombre del video final (sin extensión):"
        )
        
        if not nombre:
            return
            
        salida = nombre + ".mp4"
        
        # Verificar si el archivo ya existe
        if os.path.exists(salida):
            if not messagebox.askyesno(
                "Archivo existente",
                f"El archivo {salida} ya existe. ¿Deseas sobrescribirlo?"
            ):
                return
                
        # Iniciar proceso en hilo separado
        self.unir_button.config(state='disabled')
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.status_label.config(text="Iniciando proceso de unificación...")
        
        thread = threading.Thread(
            target=self.procesar_unificacion,
            args=(videos_validos, salida)
        )
        thread.daemon = True
        thread.start()
        
    def procesar_unificacion(self, videos, salida):
        """Procesa la unificación de videos en hilo separado"""
        try:
            # Crear archivo temporal con la lista
            concat_file = "concat_list.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                for v in videos:
                    f.write(f"file '{os.path.abspath(v)}'\n")
            
            # Comando ffmpeg con progreso
            cmd = [
                self.ffmpeg_bin,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-progress", "pipe:1",
                "-y",  # Sobrescribir sin preguntar
                salida
            ]
            
            # Ejecutar ffmpeg con captura de progreso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitorear el progreso
            self.monitorear_progreso(process, concat_file, salida)
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists("concat_list.txt"):
                os.remove("concat_list.txt")
            self.root.after(0, self.unificacion_completada, False, str(e))
            
    def monitorear_progreso(self, process, concat_file, salida):
        """Monitorea el progreso de ffmpeg en tiempo real"""
        try:
            # Obtener duración total de los videos
            duracion_total = self.obtener_duracion_total()
            
            # Iniciar progreso simulado en hilo separado si no se puede obtener duración
            if not duracion_total:
                self.root.after(0, self.actualizar_progreso_indeterminado)
                # Iniciar progreso simulado
                thread_progreso = threading.Thread(target=self.simular_progreso)
                thread_progreso.daemon = True
                thread_progreso.start()
            
            progreso_encontrado = False
            for line in process.stdout:
                if "out_time_ms=" in line:
                    progreso_encontrado = True
                    # Extraer tiempo actual
                    tiempo_actual = self.extraer_tiempo_ms(line)
                    if tiempo_actual and duracion_total:
                        progreso = min((tiempo_actual / duracion_total) * 100, 100)
                        self.root.after(0, self.actualizar_progreso, progreso, tiempo_actual, duracion_total)
                    elif tiempo_actual:
                        # Si no tenemos duración total, mostrar tiempo transcurrido
                        self.root.after(0, self.actualizar_progreso_tiempo, tiempo_actual)
            
            # Si no se encontró progreso, usar simulado
            if not progreso_encontrado and not duracion_total:
                self.root.after(0, self.actualizar_progreso_indeterminado)
                        
            # Esperar a que termine el proceso
            process.wait()
            
            # Limpiar archivo temporal
            if os.path.exists(concat_file):
                os.remove(concat_file)
                
            # Verificar si fue exitoso
            if process.returncode == 0:
                self.root.after(0, self.unificacion_completada, True, salida)
            else:
                self.root.after(0, self.unificacion_completada, False, "Error en el proceso de ffmpeg")
                
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(concat_file):
                os.remove(concat_file)
            self.root.after(0, self.unificacion_completada, False, str(e))
            
    def obtener_duracion_total(self):
        """Obtiene la duración total de todos los videos en milisegundos"""
        duracion_total = 0
        try:
            for video in self.videos:
                if video:
                    duracion = self.obtener_duracion_video(video)
                    if duracion:
                        duracion_total += duracion
        except:
            pass
        return duracion_total
        
    def obtener_duracion_video(self, video_path):
        """Obtiene la duración de un video en milisegundos"""
        try:
            cmd = [
                self.ffprobe_bin,
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duracion_segundos = float(result.stdout.strip())
            return int(duracion_segundos * 1000)  # Convertir a milisegundos
            
        except:
            return None
            
    def extraer_tiempo_ms(self, linea):
        """Extrae el tiempo en milisegundos de una línea de ffmpeg"""
        try:
            if "out_time_ms=" in linea:
                tiempo_str = linea.split("=")[1].strip()
                if tiempo_str != "N/A":
                    return int(tiempo_str)
        except:
            pass
        return None
        
    def actualizar_progreso(self, progreso, tiempo_actual, duracion_total):
        """Actualiza la barra de progreso y el estado"""
        self.progress['value'] = progreso
        
        # Actualizar label de porcentaje
        self.percentage_label.config(text=f"{progreso:.1f}%")
        
        # Convertir tiempos a formato legible
        tiempo_actual_str = self.formatear_tiempo(tiempo_actual)
        duracion_total_str = self.formatear_tiempo(duracion_total)
        
        self.status_label.config(
            text=f"Procesando... {progreso:.1f}% ({tiempo_actual_str} / {duracion_total_str})"
        )
        
        # Actualizar la interfaz
        self.root.update_idletasks()
        
    def formatear_tiempo(self, ms):
        """Convierte milisegundos a formato MM:SS"""
        if not ms:
            return "00:00"
        segundos = ms // 1000
        minutos = segundos // 60
        segundos = segundos % 60
        return f"{minutos:02d}:{segundos:02d}"
        
    def actualizar_progreso_indeterminado(self):
        """Actualiza el progreso cuando no se puede determinar el porcentaje"""
        self.progress['mode'] = 'indeterminate'
        self.progress.start()
        self.status_label.config(text="Procesando videos... (progreso indeterminado)")
        
    def actualizar_progreso_tiempo(self, tiempo_actual):
        """Actualiza el progreso mostrando solo el tiempo transcurrido"""
        tiempo_str = self.formatear_tiempo(tiempo_actual)
        self.status_label.config(text=f"Procesando... Tiempo transcurrido: {tiempo_str}")
        
    def simular_progreso(self):
        """Simula progreso cuando ffmpeg no reporta progreso"""
        import time
        progreso = 0
        while progreso < 100:
            time.sleep(0.5)  # Actualizar cada medio segundo
            progreso += 2
            if progreso > 100:
                progreso = 100
            self.root.after(0, self.actualizar_progreso_simulado, progreso)
            
    def actualizar_progreso_simulado(self, progreso):
        """Actualiza el progreso simulado"""
        self.progress['value'] = progreso
        self.percentage_label.config(text=f"{progreso:.1f}%")
        self.status_label.config(text=f"Procesando... {progreso:.1f}%")
        self.root.update_idletasks()
            
    def unificacion_completada(self, exitoso, mensaje):
        """Actualiza la UI cuando se completa la unificación"""
        # Detener la barra de progreso
        if self.progress['mode'] == 'indeterminate':
            self.progress.stop()
        else:
            self.progress['value'] = 100 if exitoso else 0
            
        # Restaurar modo determinante
        self.progress['mode'] = 'determinate'
        
        # Actualizar label de porcentaje
        if exitoso:
            self.percentage_label.config(text="100%")
        else:
            self.percentage_label.config(text="0%")
        
        self.unir_button.config(state='normal')
        
        if exitoso:
            self.status_label.config(text=f"✅ Video unido exitosamente: {mensaje}")
            messagebox.showinfo(
                "Éxito",
                f"Los videos se han unido correctamente como:\n{mensaje}"
            )
        else:
            self.status_label.config(text=f"❌ Error: {mensaje}")
            messagebox.showerror(
                "Error",
                f"No se pudo unir los videos:\n{mensaje}"
            )
            
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    # Soporte de línea de comandos para evitar abrir la GUI automáticamente.
    # --print-bins  : imprime las rutas de ffmpeg/ffprobe detectadas y sale (sin GUI)
    # Sin flags      : arranca la aplicación GUI normalmente.
    if '--print-bins' in sys.argv:
        ffmpeg_bin, ffprobe_bin = get_ff_bins()
        print(ffmpeg_bin)
        print(ffprobe_bin)
    else:
        app = VideoUnifier()
        app.run()