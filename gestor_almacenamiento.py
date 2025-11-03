import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

def crear_frame_gestor(parent, on_close=None):
    """Crea un Frame con el gestor de almacenamiento dentro de `parent`."""
    frame = tk.Frame(parent)
    archivos_encontrados = []

    usuario = Path.home()
    carpeta_raiz = usuario

    frame_botones = tk.Frame(frame)
    frame_botones.pack(side="bottom", anchor="e", padx=10, pady=10)

    progreso = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=520)
    progreso.pack(pady=10)

    lbl_estado = tk.Label(frame, text="Esperando para escanear...", font=("Arial", 10))
    lbl_estado.pack()

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
            parent.winfo_toplevel().destroy()

    btn_cancelar = ttk.Button(frame_botones, text="Cancelar", command=cancelar_escaneo, state="normal")
    btn_eliminar = ttk.Button(frame_botones, text="Eliminar seleccionados", command=eliminar_seleccionados)
    btn_salir = ttk.Button(frame_botones, text=("Volver" if callable(on_close) else "Salir"), command=cerrar_o_volver)

    btn_eliminar.pack(side="right", padx=(5, 0))
    btn_cancelar.pack(side="right", padx=(0, 5))
    btn_salir.pack(side="right", padx=(0, 5))

    iniciar_escaneo()

    return frame