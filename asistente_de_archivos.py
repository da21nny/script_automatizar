import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

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

# === FUNCIÓN PRINCIPAL ===
def organizar_archivos():
    """Organiza los archivos de una carpeta según su extensión"""
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta a organizar")

    if not carpeta:
        return None  # El usuario canceló la selección

    total = 0
    otros = 0

    # Recorremos los archivos en la carpeta seleccionada
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)  # Ruta completa del archivo
        if os.path.isfile(ruta):  # Si es un archivo
            ext = archivo.split(".")[-1].lower()  # Obtener la extensión en minúsculas
            if ext in reglas:  # Si la extensión está en las reglas
                destino = os.path.join(carpeta, reglas[ext])  # Carpeta destino según la regla
            else:  # Si no está en las reglas, va a "Otros"
                destino = os.path.join(carpeta, "Otros")
                otros += 1
            os.makedirs(destino, exist_ok=True)  # Crear la carpeta si no existe
            shutil.move(ruta, os.path.join(destino, archivo))  # Mover el archivo
            total += 1

    messagebox.showinfo(
        "Organización completada",
        f"✅ Se organizaron {total} archivos.\n📂 {otros} fueron enviados a la carpeta 'Otros'."
    )  # Mostrar mensaje de éxito

# === GESTOR EMBEBIDO (se puede insertar en un Frame existente) ===
def crear_frame_gestor(parent, on_close=None):
    """Crea un Frame con el gestor de almacenamiento dentro de `parent`.
    on_close() será llamado cuando el usuario pulse 'Volver' (o 'Salir' si no hay callback)."""
    frame = tk.Frame(parent)
    archivos_encontrados = []

    usuario = Path.home()
    carpeta_raiz = usuario

    # Frame inferior con botones
    frame_botones = tk.Frame(frame)
    frame_botones.pack(side="bottom", anchor="e", padx=10, pady=10)

    # Barra de progreso
    progreso = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=520)
    progreso.pack(pady=10)

    lbl_estado = tk.Label(frame, text="Esperando para escanear...", font=("Arial", 10))
    lbl_estado.pack()

    # Tabla de resultados
    columnas = ("Archivo", "Tamaño", "Ruta completa")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=12)
    for col in columnas:
        tree.heading(col, text=col)
    tree.column("Archivo", width=200)
    tree.column("Tamaño", width=80)
    tree.column("Ruta completa", width=340)
    tree.pack(pady=10, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    stop_event = threading.Event()
    scan_thread = None
    SIZE_LIMIT = 512 * 1024 * 1024  # 512 MB

    def buscar_archivos_grandes():
        nonlocal archivos_encontrados
        archivos_encontrados.clear()
        for item in tree.get_children():
            tree.delete(item)

        lbl_estado.config(text="Escaneando carpetas del usuario...")
        stop_event.clear()

        # Contar archivos totales
        total_archivos = 0
        for _, _, archivos in os.walk(carpeta_raiz):
            if stop_event.is_set():
                lbl_estado.config(text="Escaneo cancelado.")
                return
            total_archivos += len(archivos)

        progreso["value"] = 0
        progreso["maximum"] = max(total_archivos, 1)
        procesados = 0

        for ruta, _, archivos in os.walk(carpeta_raiz):
            if stop_event.is_set():
                lbl_estado.config(text="Escaneo cancelado.")
                return
            for archivo in archivos:
                if stop_event.is_set():
                    lbl_estado.config(text="Escaneo cancelado.")
                    return
                ruta_completa = os.path.join(ruta, archivo)
                try:
                    size = os.path.getsize(ruta_completa)
                    if size > SIZE_LIMIT:
                        archivos_encontrados.append((ruta_completa, size))
                        tree.insert("", "end", values=(archivo, f"{size/1048576:.2f} MB", ruta_completa))
                except Exception:
                    pass

                procesados += 1
                progreso["value"] = procesados
                frame.update_idletasks()

        if stop_event.is_set():
            lbl_estado.config(text="Escaneo cancelado.")
            return

        if archivos_encontrados:
            lbl_estado.config(text=f"Escaneo completado: {len(archivos_encontrados)} archivos grandes encontrados.")
            messagebox.showinfo("Completado", f"Se encontraron {len(archivos_encontrados)} archivos mayores a 512 MB.")
        else:
            lbl_estado.config(text="No se encontraron archivos grandes.")
            messagebox.showinfo("Sin resultados", "No se encontraron archivos mayores a 512 MB.")

        btn_cancelar.config(state="disabled")

    def eliminar_seleccionados():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "No seleccionaste ningún archivo para eliminar.")
            return

        confirm = messagebox.askyesno("Confirmar eliminación", "¿Deseas eliminar los archivos seleccionados?")
        if not confirm:
            return

        eliminados = 0
        espacio_liberado = 0
        for item in seleccion:
            ruta = tree.item(item, "values")[2]
            try:
                espacio_liberado += os.path.getsize(ruta)
                os.remove(ruta)
                tree.delete(item)
                eliminados += 1
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{ruta}\n{e}")

        espacio_mb = espacio_liberado / 1048576
        messagebox.showinfo("Eliminación completada",
                            f"Se eliminaron {eliminados} archivos.\nEspacio liberado: {espacio_mb:.2f} MB.")
        lbl_estado.config(text=f"Eliminados {eliminados} archivos | Liberados {espacio_mb:.2f} MB")

    def iniciar_escaneo():
        nonlocal scan_thread
        stop_event.clear()
        btn_cancelar.config(state="normal")
        scan_thread = threading.Thread(target=buscar_archivos_grandes)
        scan_thread.daemon = True
        scan_thread.start()

    def cancelar_escaneo():
        stop_event.set()
        btn_cancelar.config(state="disabled")
        lbl_estado.config(text="Cancelando escaneo...")

    def cerrar_o_volver():
        if callable(on_close):
            on_close()
        else:
            # si no hay on_close, destruir el toplevel
            parent.winfo_toplevel().destroy()

    # Botones
    btn_cancelar = ttk.Button(frame_botones, text="Cancelar", command=cancelar_escaneo, state="normal")
    btn_eliminar = ttk.Button(frame_botones, text="Eliminar seleccionados", command=eliminar_seleccionados)
    btn_salir = ttk.Button(frame_botones, text=("Volver" if callable(on_close) else "Salir"), command=cerrar_o_volver)

    btn_eliminar.pack(side="right", padx=(5, 0))
    btn_cancelar.pack(side="right", padx=(0, 5))
    btn_salir.pack(side="right", padx=(0, 5))

    # iniciar escaneo automático
    iniciar_escaneo()

    return frame

# === INTERFAZ GRÁFICA ===
def crear_interfaz():
    root = tk.Tk()
    root.title("🗂️ Asistente de Archivos - Versión GUI")
    root.geometry("640x480")
    root.resizable(False, False)
    root.configure(bg="#f4f4f4")

    # contenedor principal donde alternaremos vistas
    main_container = tk.Frame(root, bg="#f4f4f4")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # pantalla principal (grid)
    frame_principal = tk.Frame(main_container, bg="#f4f4f4")
    frame_principal.pack(fill="both", expand=True)

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
    tk.Label(frame_inf_izq, text="Copia de Seguridad (Backup)", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_izq, text="Crea copias de seguridad\nde las carpetas seleccionadas", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    boton3 = crear_boton_con_zoom(frame_inf_izq, "⚙️ Copia de Seguridad", "#FF9800")
    boton3.pack(pady=10)

    # Botón 4 - Esquina Inferior Derecha (gestor embebido)
    frame_inf_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_der.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_der, text="Gestor de almacenamiento", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_der, text="Busca archivos grandes (mayores a 512MB)\ny elija que hacer (eliminar o mantener.)", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    # referencia para el frame del gestor
    gestor_frame_ref = {"frame": None}

    def mostrar_gestor():
        # ocultar pantalla principal
        frame_principal.pack_forget()
        # crear contenedor del gestor
        fg = tk.Frame(main_container, bg="#f4f4f4")
        fg.pack(fill="both", expand=True)
        gestor_frame_ref["frame"] = fg

        def volver_inicio():
            if gestor_frame_ref["frame"] is not None:
                gestor_frame_ref["frame"].destroy()
                gestor_frame_ref["frame"] = None
            frame_principal.pack(fill="both", expand=True)

        # crear el gestor dentro del frame fg pasando el callback de volver
        gestor_ui = crear_frame_gestor(fg, on_close=volver_inicio)
        gestor_ui.pack(fill="both", expand=True)

    boton4 = crear_boton_con_zoom(frame_inf_der, "🔧 Gestionar Espacio", "#9C27B0", mostrar_gestor)
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
