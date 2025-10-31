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

    titulo = tk.Label(root, text="Organizador de Archivos", font=("Arial", 14, "bold"), bg="#f4f4f4", fg="#333")
    titulo.pack(pady=20)

    descripcion = tk.Label(
        root,
        text="Selecciona una carpeta y organiza automáticamente tus archivos\npor tipo y extensión.",
        font=("Arial", 10),
        bg="#f4f4f4",
        fg="#555"
    )
    descripcion.pack(pady=5)

    boton = tk.Button(
        root,
        text="📁 Seleccionar carpeta y organizar",
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=10,
        pady=10,
        command=organizar_archivos
    )
    boton.pack(pady=25)

    titulo = tk.Label(root, text="Archivos Duplicados", font=("Arial", 14, "bold"), bg="#f4f4f4", fg="#333")
    titulo.pack(pady=20)

    descripcion = tk.Label(
        root,
        text="Examina la Carpeta y busca archivos duplicados.",
        font=("Arial", 10),
        bg="#f4f4f4",
        fg="#555"
    )
    descripcion.pack(pady=5)

    boton = tk.Button(
        root,
        text="📁 Seleccionar carpeta y organizar",
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=10,
        pady=10,
        command=organizar_archivos
    )
    boton.pack(pady=25)


    creditos = tk.Label(root, text="Desarrollado por Los Penguin 1 💻", font=("Arial", 9), bg="#f4f4f4", fg="#888")
    creditos.pack(side="bottom", pady=10)

    root.mainloop()

# === EJECUCIÓN ===
if __name__ == "__main__":
    crear_interfaz()
