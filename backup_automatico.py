import os
import zipfile
from datetime import datetime
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Carpetas a incluir (tanto nombres en español como en inglés)
FOLDERS_TO_INCLUDE = [
    ("Downloads", "Descargas"),
    ("Music", "Musica"),
    ("Pictures", "Imagenes", "Imágenes"),
    ("Videos", "Videos"),
]

#función para crear el frame del backup automático
def crear_frame_backup(parent, on_close=None):
    """
    Crea y devuelve un Frame que ejecuta un backup (ZIP) de las carpetas:
    Descargas, Música, Imágenes y Videos del perfil del usuario.
    - parent: widget contenedor donde se añadirá el Frame.
    - on_close: callback opcional que se llamará cuando el usuario pulse 'Volver'
      (o cuando se cierre la vista). Si no se proporciona, se destruirá el toplevel.
    """
    # Obtener rutas importantes
    user_home = Path.home()
    desktop = user_home / "Desktop"

    frame = tk.Frame(parent)

    # Top info
    frame_top = tk.Frame(frame)
    frame_top.pack(fill="x", padx=10, pady=(10, 0))
    lbl_info = tk.Label(
        frame_top,
        text="Se harán Copias de Seguridad solo de las carpetas: Descargas, Música, Imágenes y Videos",
        anchor="w",
    )
    lbl_info.pack(fill="x")

    progreso = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=600)
    progreso.pack(padx=10, pady=10)

    lbl_estado = tk.Label(frame, text="Preparando...", anchor="w")
    lbl_estado.pack(fill="x", padx=10)

    # Listado de archivos añadidos
    frame_list = tk.Frame(frame)
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)
    listbox = tk.Listbox(frame_list, height=12)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)

    # Botones (abajo derecha)
    frame_bot = tk.Frame(frame)
    frame_bot.pack(fill="x", padx=10, pady=10)
    btn_cancel = ttk.Button(frame_bot, text="Cancelar")
    btn_cancel.pack(side="right")

    stop_event = threading.Event()

    #función para encontrar las carpetas fuente
    def find_source_folders():
        """Devuelve lista de Path de carpetas existentes a incluir."""
        sources = []
        for names in FOLDERS_TO_INCLUDE:
            for name in names:
                candidate = user_home / name
                if candidate.exists() and candidate.is_dir():
                    sources.append(candidate)
                    break
        return sources

    def add_list_item_safe(text):
        frame.after(0, lambda: listbox.insert(tk.END, text))

    def set_status_safe(text):
        frame.after(0, lambda: lbl_estado.config(text=text))

    def update_progress_safe(value):
        frame.after(0, lambda: progreso.config(value=value))

    def finish_ui(message=None):
        """Se ejecuta cuando finaliza o se cancela el backup."""
        if message:
            frame.after(0, lambda: messagebox.showinfo("Resultado", message))
        # cambiar botón cancelar por volver
        def volver_action():
            if callable(on_close):
                on_close()
            else:
                # si no hay on_close, cerrar el toplevel
                try:
                    parent.winfo_toplevel().destroy()
                except Exception:
                    pass

        frame.after(0, lambda: btn_cancel.config(text="Volver", command=volver_action, state="normal"))

    #función worker del backup (se ejecuta en hilo separado)
    def worker():
        sources = find_source_folders()
        if not sources:
            set_status_safe("No se encontraron carpetas seleccionadas.")
            finish_ui("No se encontraron las carpetas Descargas/Música/Imágenes/Videos en el perfil.")
            return

        # Contar archivos totales
        total_files = 0
        files_list = []
        for src in sources:
            for dirpath, _, filenames in os.walk(src):
                for f in filenames:
                    files_list.append(Path(dirpath) / f)
                    total_files += 1

        if total_files == 0:
            set_status_safe("No hay archivos para respaldar.")
            finish_ui("No se encontraron archivos en las carpetas seleccionadas.")
            return

        frame.after(0, lambda: progreso.config(maximum=total_files, value=0))
        set_status_safe(f"Iniciando backup ({total_files} archivos)...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = desktop / f"backup_selected_{timestamp}.zip"

        try:
            with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                processed = 0
                for file_path in files_list:
                    if stop_event.is_set():
                        set_status_safe("Backup cancelado por el usuario.")
                        finish_ui("Backup cancelado. El ZIP parcial puede haber sido creado.")
                        return
                    try:
                        arcname = file_path.relative_to(user_home)
                        zf.write(str(file_path), arcname.as_posix())
                        processed += 1
                        update_progress_safe(processed)
                        add_list_item_safe(str(arcname))
                        set_status_safe(f"Añadidos {processed}/{total_files}")
                    except Exception:
                        processed += 1
                        update_progress_safe(processed)
                        add_list_item_safe(f"[ERROR] {file_path.name}")
                        continue
            set_status_safe(f"Backup completado: {zip_name.name}")
            finish_ui(f"Backup creado en el Escritorio:\n{zip_name}")
        except Exception as e:
            set_status_safe("Error creando ZIP.")
            finish_ui(f"Error al crear el ZIP: {e}")

    #función para manejar el botón cancelar
    def on_cancel():
        # Si botón ya fue convertido a "Volver", ejecutar el callback
        if btn_cancel.cget("text") == "Volver":
            if callable(on_close):
                on_close()
            else:
                try:
                    parent.winfo_toplevel().destroy()
                except Exception:
                    pass
            return
        stop_event.set()
        btn_cancel.config(state="disabled")
        set_status_safe("Cancelando...")

    btn_cancel.config(command=on_cancel)

    # iniciar worker en hilo (no bloquea la UI)
    th = threading.Thread(target=worker, daemon=True)
    th.start()

    return frame