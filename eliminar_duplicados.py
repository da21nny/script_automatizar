import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import hashlib


def crear_frame_duplicados(parent, on_close=None):
    """Crea un Frame con el gestor de duplicados dentro de `parent`."""
    frame = tk.Frame(parent)
    archivos_encontrados = []

    usuario = Path.home()
    rutas_seguras = [
    usuario / "Desktop",
    usuario / "Documents",
    usuario / "Downloads",
    usuario / "Pictures",
    usuario / "Music",
    usuario / "Videos"
]


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

    # === FUNCIÓN PRINCIPAL ===
    def buscar_archivos_duplicados():
        nonlocal archivos_encontrados
        archivos_encontrados.clear()
        for item in tree.get_children():
            tree.delete(item)

        lbl_estado.config(text="Buscando archivos duplicados...")
        stop_event.clear()

        # === Contar archivos totales (para la barra de progreso) ===
        total_archivos = 0
        for carpeta in rutas_seguras:
            if not carpeta.exists():
                continue
            for _, _, archivos in os.walk(carpeta):
                total_archivos += len(archivos)

        progreso["value"] = 0
        progreso["maximum"] = max(total_archivos, 1)
        procesados = 0

        hashes = {}
        duplicados = {}

        # === Escanear carpetas seguras del usuario ===
        for carpeta in rutas_seguras:
            if not carpeta.exists():
                continue

            for ruta, _, archivos in os.walk(carpeta):
                # Saltar carpetas ocultas o del sistema
                if "appdata" in ruta.lower() or "programdata" in ruta.lower():
                    continue

                for archivo in archivos:
                    if stop_event.is_set():
                        lbl_estado.config(text="Escaneo cancelado.")
                        return

                    ruta_completa = os.path.join(ruta, archivo)

                    try:
                        # Calcular hash en bloques (seguro para archivos grandes)
                        hasher = hashlib.md5()
                        with open(ruta_completa, "rb") as f:
                            for bloque in iter(lambda: f.read(4096), b""):
                                hasher.update(bloque)
                        hash_archivo = hasher.hexdigest()

                        # === Detección de duplicados ===
                        if hash_archivo in hashes:
                            # si es la primera vez que aparece el duplicado, guardamos el original también
                            if hash_archivo not in duplicados:
                                duplicados[hash_archivo] = [hashes[hash_archivo]]

                            duplicados[hash_archivo].append(ruta_completa)
                            archivos_encontrados.append((ruta_completa, os.path.getsize(ruta_completa)))

                            size = os.path.getsize(ruta_completa)
                            tree.insert("", "end", values=(archivo, f"{size / 1048576:.2f} MB", ruta_completa))
                        else:
                            hashes[hash_archivo] = ruta_completa

                    except Exception as e:
                        # Evitar que errores de lectura interrumpan el escaneo
                        # print(f"Error procesando {ruta_completa}: {e}")
                        pass

                    procesados += 1
                    progreso["value"] = procesados
                    frame.update_idletasks()

        # === Mostrar resultados ===
        if stop_event.is_set():
            lbl_estado.config(text="Escaneo cancelado.")
            return

        if archivos_encontrados:
            lbl_estado.config(text=f"Escaneo completado: {len(archivos_encontrados)} duplicados encontrados.")
            messagebox.showinfo("Completado", f"Se encontraron {len(archivos_encontrados)} archivos duplicados.")
        else:
            lbl_estado.config(text="No se encontraron archivos duplicados.")
            messagebox.showinfo("Sin resultados", "No se encontraron archivos duplicados.")

        btn_cancelar.config(state="disabled")


    # === ELIMINAR ARCHIVOS SELECCIONADOS ===
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
        messagebox.showinfo(
            "Eliminación completada",
            f"Se eliminaron {eliminados} archivos.\nEspacio liberado: {espacio_mb:.2f} MB."
        )
        lbl_estado.config(text=f"Eliminados {eliminados} archivos | Liberados {espacio_mb:.2f} MB")

    # === CONTROLES DE ESCANEO ===
    def iniciar_escaneo():
        nonlocal scan_thread
        stop_event.clear()
        btn_cancelar.config(state="normal")
        scan_thread = threading.Thread(target=buscar_archivos_duplicados)
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

    # === BOTONES ===
    btn_cancelar = ttk.Button(frame_botones, text="Cancelar", command=cancelar_escaneo, state="normal")
    btn_eliminar = ttk.Button(frame_botones, text="Eliminar seleccionados", command=eliminar_seleccionados)
    btn_salir = ttk.Button(
        frame_botones,
        text=("Volver" if callable(on_close) else "Salir"),
        command=cerrar_o_volver
    )

    btn_eliminar.pack(side="right", padx=(5, 0))
    btn_cancelar.pack(side="right", padx=(0, 5))
    btn_salir.pack(side="right", padx=(0, 5))

    iniciar_escaneo()

    return frame
