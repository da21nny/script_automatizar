import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

reglas = {
    # Documentos
    "pdf": "Documentos/PDF",
    "docx": "Documentos/Word",
    "doc": "Documentos/Word",
    "xlsx": "Documentos/Excel",
    "xls": "Documentos/Excel",
    "pptx": "Documentos/PowerPoint",
    "ppt": "Documentos/PowerPoint",
    "txt": "Documentos/TXT",
    "csv": "Documentos/Planillas",
    "odt": "Documentos/OpenOffice",
    # Imágenes
    "jpg": "Imagenes",
    "jpeg": "Imagenes",
    "png": "Imagenes",
    "gif": "Imagenes",
    "bmp": "Imagenes",
    "svg": "Imagenes",
    # Música
    "mp3": "Musica",
    "wav": "Musica",
    "ogg": "Musica",
    "flac": "Musica",
    # Videos
    "mp4": "Videos",
    "avi": "Videos",
    "mkv": "Videos",
    "mov": "Videos",
    # Comprimidos
    "zip": "Comprimidos",
    "rar": "Comprimidos",
    "7z": "Comprimidos",
    "tar": "Comprimidos",
    "gz": "Comprimidos",
    # Programas y Scripts
    "exe": "Programas",
    "msi": "Programas",
    "bat": "Scripts",
    "py": "Scripts",
    "js": "Scripts",
    "html": "Web",
    "css": "Web",
    "json": "Web",
    "xml": "Web"
    }

# === FUNCIÓN PRINCIPAL ===
def organizar_archivos():
    """Organiza los archivos de una carpeta según su extensión"""
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta a organizar")

    if not carpeta:
        messagebox.showwarning("Atención", "No seleccionaste ninguna carpeta.")
        return

    total = 0
    otros = 0

    # Recorremos los archivos en la carpeta seleccionada
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta):
            ext = archivo.split(".")[-1].lower()
            if ext in reglas:
                destino = os.path.join(carpeta, reglas[ext])
            else:
                destino = os.path.join(carpeta, "Otros")
                otros += 1
            os.makedirs(destino, exist_ok=True)
            shutil.move(ruta, os.path.join(destino, archivo))
            total += 1

    messagebox.showinfo(
        "Organización completada",
        f"✅ Se organizaron {total} archivos.\n📂 {otros} fueron enviados a la carpeta 'Otros'."
    )

# === INTERFAZ GRÁFICA ===
def crear_interfaz():
    root = tk.Tk()
    root.title("🗂️ Asistente de Archivos - Versión GUI")
    root.geometry("640x480")
    root.resizable(False, False)
    root.configure(bg="#f4f4f4")

    # Crear un frame principal para contener los botones
    frame_principal = tk.Frame(root, bg="#f4f4f4")
    frame_principal.pack(expand=True, fill="both", padx=20, pady=20)

    # Configurar el grid para tener 2 columnas y 2 filas
    frame_principal.grid_columnconfigure(0, weight=1)
    frame_principal.grid_columnconfigure(1, weight=1)
    frame_principal.grid_rowconfigure(0, weight=1)
    frame_principal.grid_rowconfigure(1, weight=1)

    # Botón 1 - Esquina Superior Izquierda
    frame_sup_izq = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_sup_izq.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_sup_izq, text="Organizador de Archivos", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_sup_izq, text="Organiza tus archivos\npor tipo y extensión", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton1 = crear_boton_con_zoom(frame_sup_izq, "📁 Organizar Archivos", "#4CAF50", organizar_archivos)
    boton1.pack(pady=10)

    # Botón 2 - Esquina Superior Derecha
    frame_sup_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_sup_der.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_sup_der, text="Archivos Duplicados", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_sup_der, text="Encuentra y gestiona\narchivos duplicados", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton2 = crear_boton_con_zoom(frame_sup_der, "🔍 Buscar Duplicados", "#2196F3")
    boton2.pack(pady=10)

    # Botón 3 - Esquina Inferior Izquierda
    frame_inf_izq = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_izq.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_izq, text="Opción 3", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_izq, text="Descripción de\nla opción 3", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton3 = crear_boton_con_zoom(frame_inf_izq, "⚙️ Opción 3", "#FF9800")
    boton3.pack(pady=10)

    # Botón 4 - Esquina Inferior Derecha
    frame_inf_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_der.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_der, text="Opción 4", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_der, text="Descripción de\nla opción 4", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton4 = crear_boton_con_zoom(frame_inf_der, "🔧 Opción 4", "#9C27B0")
    boton4.pack(pady=10)

    # Créditos en la parte inferior
    creditos = tk.Label(root, text="Desarrollado por Los Penguin 1 💻", font=("Arial", 9), bg="#f4f4f4", fg="#888")
    creditos.pack(side="bottom", pady=10)

    root.mainloop()

# === FUNCIÓN DE CREACIÓN DE BOTONES CON ZOOM ===
def crear_boton_con_zoom(frame, texto, color, comando=None):
    """Crea un botón con efecto de zoom al pasar el cursor"""
    boton = tk.Button(frame, text=texto, font=("Arial", 12), bg=color, fg="white", command=comando)
    
    def on_enter(e):
        # Aumenta el tamaño del botón cuando el cursor entra
        boton.config(font=("Arial", 13, "bold"))
        
    def on_leave(e):
        # Restaura el tamaño original cuando el cursor sale
        boton.config(font=("Arial", 12))
    
    boton.bind("<Enter>", on_enter)
    boton.bind("<Leave>", on_leave)
    
    return boton

# === EJECUCIÓN ===
if __name__ == "__main__":
    crear_interfaz()
