import tkinter as tk
from tkinter import ttk
import time, threading, sys, os

#variables de configuración
DURATION = 20
BSOD_TIME = 7
BSOD_IMAGE = "bsod.gif"

# Variables globales
_on_close_callback = None
_analysis_running = False
_analysis_thread = None

def resource_path(relative_path):
    """Obtiene la ruta correcta tanto en desarrollo como en ejecutable"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def close_bsod_and_return(bsod_window):
    """Cierra el BSOD y vuelve al menú principal"""
    global _analysis_running
    _analysis_running = False
    bsod_window.destroy()
    if _on_close_callback:
        _on_close_callback()

def show_bsod():
    global _analysis_running
    try:
        image_path = resource_path(BSOD_IMAGE)
        bsod = tk.Toplevel()
        bsod.attributes('-fullscreen', True)
        bsod.configure(bg='blue')

        if os.path.exists(image_path):
            # Obtener dimensiones de la pantalla
            screen_width = bsod.winfo_screenwidth()
            screen_height = bsod.winfo_screenheight()
            
            # Cargar imagen GIF
            photo = tk.PhotoImage(file=image_path)
            
            # Calcular factor de escala para ajustar a pantalla
            img_width = photo.width()
            img_height = photo.height()
            
            scale_w = screen_width / img_width
            scale_h = screen_height / img_height
            scale = max(scale_w, scale_h)
            
            # Redimensionar usando subsample o zoom
            if scale < 1:
                # Si necesitamos reducir, usamos subsample
                subsample_factor = int(1 / scale)
                photo = photo.subsample(subsample_factor, subsample_factor)
            elif scale > 1:
                # Si necesitamos ampliar, usamos zoom
                zoom_factor = int(scale)
                photo = photo.zoom(zoom_factor, zoom_factor)
            
            # Crear canvas para centrar la imagen
            canvas = tk.Canvas(bsod, width=screen_width, height=screen_height, 
                             bg='blue', highlightthickness=0)
            canvas.pack(fill='both', expand=True)
            canvas.create_image(screen_width//2, screen_height//2, 
                              image=photo, anchor='center')
            canvas.image = photo  # Mantener referencia
        else:
            tk.Label(bsod, text="BLUE SCREEN OF DEATH", 
                    font=("Arial", 30), fg="white", bg="blue").pack(expand=True)

        # ESC cierra BSOD y detiene análisis
        bsod.bind('<Escape>', lambda e: close_bsod_and_return(bsod))
        bsod.focus_force()

    except Exception as e:
        print(f"Error al cargar imagen: {e}")
        _analysis_running = False

def start_analysis(progress, root):
    """Función de análisis con control de detención"""
    global _analysis_running
    _analysis_running = True
    
    for i in range(DURATION + 1):
        if not _analysis_running:
            break
            
        time.sleep(1)
        
        # Verificar si el widget progress aún existe
        try:
            progress['value'] = (i / DURATION) * 100
            root.update_idletasks()
        except tk.TclError:
            # El widget fue destruido, salir del bucle
            break
            
        if i == BSOD_TIME and _analysis_running:
            show_bsod()

def crear_frame_sorpresa(parent, on_close=None):
    """Crea el frame de sorpresa dentro del contenedor padre"""
    global _on_close_callback, _analysis_running
    _on_close_callback = on_close
    
    frame = tk.Frame(parent, bg="#f4f4f4")
    
    # Botón de volver
    if on_close:
        def volver_seguro():
            global _analysis_running
            _analysis_running = False
            on_close()
            
        btn_volver = tk.Button(frame, text="← Volver", command=volver_seguro, 
                              font=("Arial", 10), bg="#607D8B", fg="white")
        btn_volver.pack(anchor="nw", padx=10, pady=10)
    
    label = tk.Label(frame, text="Analizando componentes de la PC...", 
                    font=("Arial", 14), bg="#f4f4f4")
    label.pack(pady=50)
    
    progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=20)
    
    # Iniciar el análisis en un hilo separado
    analysis_thread = threading.Thread(target=start_analysis, args=(progress, frame), daemon=True)
    analysis_thread.start()
    
    return frame

def main(container=None):
    """Mantiene compatibilidad si se ejecuta standalone"""
    if container:
        return crear_frame_sorpresa(container)
    else:
        root = tk.Tk()
        root.title("Analizando componentes de la PC")
        root.geometry("640x480")
        crear_frame_sorpresa(root)
        root.mainloop()

# Ejecutar el módulo standalone
if __name__ == "__main__":
    main()