import os
import shutil
from tkinter import filedialog, messagebox

# Reglas de organización
reglas = {
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
    "jpg": "Imagenes",
    "jpeg": "Imagenes",
    "png": "Imagenes",
    "gif": "Imagenes",
    "bmp": "Imagenes",
    "svg": "Imagenes",
    "mp3": "Musica",
    "wav": "Musica",
    "ogg": "Musica",
    "flac": "Musica",
    "mp4": "Videos",
    "avi": "Videos",
    "mkv": "Videos",
    "mov": "Videos",
    "zip": "Comprimidos",
    "rar": "Comprimidos",
    "7z": "Comprimidos",
    "tar": "Comprimidos",
    "gz": "Comprimidos",
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

def organizar_archivos():
    """Organiza los archivos de una carpeta según su extensión"""
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta a organizar")
    if not carpeta:
        return None

    total = 0
    otros = 0

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