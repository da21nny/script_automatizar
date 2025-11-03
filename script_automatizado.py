import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import threading
import traceback


# === REGLAS DE ORGANIZACIÓN ===
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

#Funcion calcular (reemplaza o añade)
def calcular_md5(ruta, bloque_size=65536):
    """
    MD5 robusto: lee en bloques grandes y devuelve (hash_hex, error_text).
    Si no hay error, error_text es None.
    """
    try:
        h = hashlib.md5()
        with open(ruta, "rb") as f:
            for bloque in iter(lambda: f.read(bloque_size), b""):
                h.update(bloque)
        return h.hexdigest(), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    
def buscar_duplicados_dialog(carpeta, parent_widget=None, show_every_n=100):
    # Escanea la carpeta por duplicados exactos:
    # 1) Indexa archivos por tamaño.
    # 2) Solo hashea los tamaños con más de 1 archivo (candidatos).
    # 3) Devuelve dict {hash: [ruta1, ruta2, ...]} con >1 rutas.
    # parent_widget (opcional): widget Text/Listbox que tenga método .insert para debug.

    # 1) indexar por tamaño para filtrar candidatos
    size_index = {}
    cant_escaneados = 0
    errores_lectura = []

    for root, dirs, files in os.walk(carpeta):
        for fname in files:
            ruta = os.path.join(root, fname)
            try:
                sz = os.path.getsize(ruta)
            except Exception as e:
                errores_lectura.append((ruta, f"size_error: {e}"))
                continue
            size_index.setdefault(sz, []).append(ruta)
            cant_escaneados += 1
            if parent_widget and cant_escaneados % show_every_n == 0:
                try:
                    parent_widget.insert(tk.END, f"Escaneados: {cant_escaneados} archivos...\n")
                    parent_widget.see(tk.END)
                except Exception:
                    pass

    # 2) hashear solo los candidatos
    hash_index = {}
    cant_hash = 0
    for sz, rutas in size_index.items():
        if len(rutas) < 2:
            continue  # no pueden ser duplicados exactos si el tamaño difiere
        for ruta in rutas:
            h, err = calcular_md5(ruta)
            if err:
                errores_lectura.append((ruta, err))
                continue
            hash_index.setdefault(h, []).append(ruta)
            cant_hash += 1
            if parent_widget and cant_hash % show_every_n == 0:
                try:
                    parent_widget.insert(tk.END, f"Hasheados: {cant_hash} archivos...\n")
                    parent_widget.see(tk.END)
                except Exception:
                    pass

    # 3) filtrar solo hashes con >1 ruta
    duplicados = {h: rutas for h, rutas in hash_index.items() if len(rutas) > 1}

    # 4) reporte a parent_widget si se pasó
    if parent_widget:
        parent_widget.insert(tk.END, f"Escaneo finalizado. Archivos escaneados: {cant_escaneados}\n")
        parent_widget.insert(tk.END, f"Archivos hasheados (candidatos): {cant_hash}\n")
        parent_widget.insert(tk.END, f"Archivos con errores de lectura: {len(errores_lectura)}\n")
        if errores_lectura:
            parent_widget.insert(tk.END, "Ejemplos de errores (ruta -> error):\n")
            for r, e in errores_lectura[:10]:
                parent_widget.insert(tk.END, f" - {r} -> {e}\n")
        if duplicados:
            parent_widget.insert(tk.END, f"Sets duplicados encontrados: {len(duplicados)}\n")
        else:
            parent_widget.insert(tk.END, "No se encontraron duplicados exactos (bit-a-bit).\n")
        parent_widget.see(tk.END)

    return duplicados


# === FUNCIÓN PRINCIPAL ===
def organizar_archivos():
    """Organiza los archivos de una carpeta según su extensión"""
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta a organizar") 

    if not carpeta:
        return None # El usuario canceló la selección

    total = 0
    otros = 0

    # Recorremos los archivos en la carpeta seleccionada (solo nivel superior)
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo) # Ruta completa del archivo
        if os.path.isfile(ruta): # Si es un archivo
            nombre, ext = os.path.splitext(archivo)
            if ext:
                ext = ext.lstrip(".").lower()
            else:
                ext = ""  # sin extensión
            if ext in reglas: # Si la extensión está en las reglas
                destino_rel = reglas[ext]
            else: # Si no está en las reglas, va a "Otros"
                destino_rel = "Otros"
                otros += 1

            destino = os.path.normpath(os.path.join(carpeta, destino_rel))
            os.makedirs(destino, exist_ok=True) # Crear la carpeta si no existe
            try:
                shutil.move(ruta, os.path.join(destino, archivo)) # Mover el archivo
                total += 1
            except Exception as e:
                # No interrumpir todo por un archivo; podría loguearse o mostrarse
                print(f"Error moviendo {ruta} -> {destino}: {e}")

    messagebox.showinfo(
        "Organización completada",
        f"✅ Se organizaron {total} archivos.\n📂 {otros} fueron enviados a la carpeta 'Otros'."
    ) # Mostrar mensaje de éxito

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
    boton2 = crear_boton_con_zoom(frame_sup_der, "🔍 Buscar Duplicados", "#2196F3", comando=lambda: buscar_duplicados_ui(root))
    boton2.pack(pady=10)

    # Botón 3 - Esquina Inferior Izquierda
    frame_inf_izq = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_izq.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_izq, text="Copia de Seguridad (Backup)", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_izq, text="Crea copias de seguridad\nde las carpetas seleccionadas", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton3 = crear_boton_con_zoom(frame_inf_izq, "⚙️ Copia de Seguridad", "#FF9800", comando=lambda: messagebox.showinfo("Backup", "Funcionalidad en desarrollo"))
    boton3.pack(pady=10)

    # Botón 4 - Esquina Inferior Derecha
    frame_inf_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_der.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_der, text="Gestor de almacenamiento", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_der, text="Busca archivos grandes (mayores a 1Gb)\ny elija que hacer (eliminar o mantener.)", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton4 = crear_boton_con_zoom(frame_inf_der, "🔧 Gestionar Espacio", "#9C27B0", comando=lambda: messagebox.showinfo("Gestionar Espacio", "Funcionalidad en desarrollo"))
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

def buscar_duplicados_ui(root):
    """UI que lanza la búsqueda de duplicados en segundo plano y muestra resultados en un Toplevel."""
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta para buscar duplicados")
    if not carpeta:
        return

    top = tk.Toplevel(root)
    top.title("🔍 Buscar Duplicados")
    top.geometry("800x500")
    text = tk.Text(top, wrap="none")
    text.pack(expand=True, fill="both", padx=8, pady=8)

    text.insert(tk.END, f"Comenzando escaneo en: {carpeta}\n\n")
    text.see(tk.END)

    def worker():
        # Llamamos a la función de escaneo sin pasar parent_widget (evita escritura directa desde el hilo)
        duplicados = buscar_duplicados_dialog(carpeta, parent_widget=None)
        def mostrar_resultados():
            if not duplicados:
                text.insert(tk.END, "No se encontraron duplicados.\n")
            else:
                text.insert(tk.END, f"Sets duplicados encontrados: {len(duplicados)}\n\n")
                for h, rutas in duplicados.items():
                    text.insert(tk.END, f"Hash: {h}\n")
                    for r in rutas:
                        text.insert(tk.END, f" - {r}\n")
                    text.insert(tk.END, "\n")
            text.see(tk.END)
        # Actualizar GUI desde el hilo principal
        root.after(0, mostrar_resultados)

    threading.Thread(target=worker, daemon=True).start()

# === EJECUCIÓN ===
if __name__ == "__main__":
    crear_interfaz()