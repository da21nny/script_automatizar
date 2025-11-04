import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time, threading, sys, os

#variables de configuración
DURATION = 20
BSOD_TIME = 10
BSOD_IMAGE = "bsod.png"

# Variable global para almacenar la función de cierre
_on_close_callback = None

#función para cerrar el BSOD y volver al menú principal
def close_bsod_and_return(bsod_window):
    """Cierra el BSOD y vuelve al menú principal"""
    bsod_window.destroy()
    if _on_close_callback:
        _on_close_callback()

def show_bsod():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, BSOD_IMAGE)
        bsod = tk.Toplevel()
        bsod.attributes('-fullscreen', True)
        bsod.configure(bg='blue')

        if os.path.exists(image_path):
            img = Image.open(image_path)
            screen_width = bsod.winfo_screenwidth()
            screen_height = bsod.winfo_screenheight()
            img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(bsod, image=photo)
            label.image = photo
            label.pack(fill='both', expand=True)
        else:
            tk.Label(bsod, text="BLUE SCREEN OF DEATH", font=("Arial", 30), fg="white", bg="blue").pack(expand=True)

        # Al presionar ESC, cierra BSOD y vuelve al main
        bsod.bind('<Escape>', lambda e: close_bsod_and_return(bsod))
        bsod.focus_force()

    # Manejo de errores al cargar la imagen
    except Exception as e:
        print(f"Error al cargar imagen: {e}")

#función para simular el análisis con barra de progreso
def start_analysis(progress, root):
    for i in range(DURATION + 1):
        time.sleep(1)
        progress['value'] = (i / DURATION) * 100
        root.update_idletasks()
        if i == BSOD_TIME:
            show_bsod()

#función para crear el frame de sorpresa
def crear_frame_sorpresa(parent, on_close=None):
    """Crea el frame de sorpresa dentro del contenedor padre"""
    global _on_close_callback
    _on_close_callback = on_close
    
    frame = tk.Frame(parent, bg="#f4f4f4")
    
    # Botón de volver
    if on_close:
        btn_volver = tk.Button(frame, text="← Volver", command=on_close, 
                              font=("Arial", 10), bg="#607D8B", fg="white")
        btn_volver.pack(anchor="nw", padx=10, pady=10)
    
    label = tk.Label(frame, text="Analizando componentes de la PC...", 
                    font=("Arial", 14), bg="#f4f4f4")
    label.pack(pady=50)
    
    progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=20)
    
    # Iniciar el análisis en un hilo separado
    threading.Thread(target=start_analysis, args=(progress, frame), daemon=True).start()
    
    return frame

#función principal para ejecutar el módulo standalone
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