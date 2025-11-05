import os   # Para manejo de rutas y operaciones con archivos
import threading  # Para ejecutar el escaneo en segundo plano
import tkinter as tk  # Para la interfaz gráfica
from tkinter import ttk, messagebox  # Widgets modernos y cuadros de diálogo
from pathlib import Path  # Manejo moderno de rutas
import hashlib  # Para generar hashes únicos de archivos

# Módulo opcional: send2trash
# Permite enviar archivos a la papelera de reciclaje en lugar de eliminarlos permanentemente
# Si no está disponible, los archivos se eliminarán de forma permanente
try:
    from send2trash import send2trash
except ImportError:
    send2trash = None

# Funcion principal para crear el frame o ventana donde se buscan los archivos duplicados
def crear_frame_duplicados(parent, on_close=None):
    frame = tk.Frame(parent)
    archivos_encontrados = []

# Rutas seguras para escanear
    usuario = Path.home()
    rutas_seguras = [
        usuario / "Desktop",
        usuario / "Documents",
        usuario / "Downloads",
        usuario / "Pictures",
        usuario / "Music",
        usuario / "Videos"
    ]

    # Crear widgets de la interfaz
    frame_botones = tk.Frame(frame)
    frame_botones.pack(side="bottom", anchor="e", padx=10, pady=10)

#progreso de escaneo
    progreso = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=520)
    progreso.pack(pady=10)

#Estado del escaneo
    lbl_estado = tk.Label(frame, text="Esperando para escanear...", font=("Arial", 10))
    lbl_estado.pack()

# Crear Treeview para mostrar Resultados
    columnas = ("check", "Archivo", "Tamaño", "Ruta completa")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=12)
    tree.heading("check", text="✔")
    tree.heading("Archivo", text="Archivo")
    tree.heading("Tamaño", text="Tamaño")
    tree.heading("Ruta completa", text="Ruta completa")
    tree.column("check", width=32, anchor="center")
    tree.column("Archivo", width=200)
    tree.column("Tamaño", width=80)
    tree.column("Ruta completa", width=340)
    tree.pack(pady=10, fill="both", expand=True)

# Agrega una srollbar a la lista de resultados
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

# Boton evento para detener el escaneo
    stop_event = threading.Event()
    scan_thread = None

    # Funcion principal para buscar archivos duplicados
    def buscar_archivos_duplicados():
        
        #que hace nonlocal: permite modificar la variable archivos_encontrados para que no se cree una nueva variable local
        nonlocal archivos_encontrados
        archivos_encontrados.clear() #limpia la lista de archivos duplicados
        for item in tree.get_children():
            tree.delete(item) #Limpia la lista de resultados

        lbl_estado.config(text="Buscando archivos duplicados...") #actualiza el estado
        stop_event.clear()

        # === Contar archivos totales (para la barra de progreso) ===
        total_archivos = 0 #cuenta todos los archivos
        for carpeta in rutas_seguras: #recorre las rutas seguraas
            if not carpeta.exists(): 
                continue
            for _, _, archivos in os.walk(carpeta): #
                total_archivos += len(archivos)

        progreso["value"] = 0 #inicia la barra de progreso en 0
        progreso["maximum"] = max(total_archivos, 1) #establece el maximo de la barra
        procesados = 0 #contador de archivos procesados

#que es hash: el hash es una cadena de caracteres que representa de forma unica el contenido de un archivo
        hashes = {} #diccionario para guardar los hashes
        duplicados = {} #diccionario para guardar los duplicados

        # === Escanear carpetas seguras del usuario ===
        for carpeta in rutas_seguras: 
            if not carpeta.exists():
                continue

                # Recorre los archivos en la carpeta
            for ruta, _, archivos in os.walk(carpeta):
                # Saltar carpetas ocultas o del sistema
                if "appdata" in ruta.lower() or "programdata" in ruta.lower(): # Si son carpetas sensibles del sistema, las salta
                    continue

                for archivo in archivos: 
                    if stop_event.is_set():
                        lbl_estado.config(text="Escaneo cancelado.") 
                        return
                
                    ruta_completa = os.path.join(ruta, archivo) 

                    try:
                        # Calcular hash en bloques (seguro para archivos grandes)
                        hasher = hashlib.md5() 
                        with open(ruta_completa, "rb") as f: # abre el archivo en modo lectura binaria
                            for bloque in iter(lambda: f.read(4096), b""): #lee el archivo en bloques de 4096 bytes 
                                hasher.update(bloque) 
                        hash_archivo = hasher.hexdigest()

                        # detector de  duplicados
                        if hash_archivo in hashes:
                            # si es la primera vez que aparece el duplicado, guardamos el original también
                            if hash_archivo not in duplicados:
                                duplicados[hash_archivo] = [hashes[hash_archivo]] 

                            duplicados[hash_archivo].append(ruta_completa)
                            archivos_encontrados.append((ruta_completa, os.path.getsize(ruta_completa)))

                            size = os.path.getsize(ruta_completa)
                            tree.insert("", "end", values=("☐", archivo, f"{size / 1048576:.2f} MB", ruta_completa))
                        else:
                            hashes[hash_archivo] = ruta_completa

                    except Exception as e:
                        pass

                    procesados += 1
                    progreso["value"] = procesados
                    frame.update_idletasks()

        # Mostramos los resultados finales
        if stop_event.is_set(): #si se ha solicitado la cancelancion se detiene el escaneo
            lbl_estado.config(text="Escaneo cancelado.") 
            return

        if archivos_encontrados: #si se encontraron duplicados 
            lbl_estado.config(text=f"Escaneo completado: {len(archivos_encontrados)} duplicados encontrados.")
            # monstrar mensaje con la cantidad de archivos duplicados encontrados
            messagebox.showinfo("Completado", f"Se encontraron {len(archivos_encontrados)} archivos duplicados.")
        else: #si no
            lbl_estado.config(text="No se encontraron archivos duplicados.")
            #mostrar mensaje que no se encontraron
            messagebox.showinfo("Sin resultados", "No se encontraron archivos duplicados.")

        btn_cancelar.config(state="disabled")

    # checkboxes simulados
    def on_tree_click(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            col = tree.identify_column(event.x)
            if col == "#1":  # Columna del checkbox
                row = tree.identify_row(event.y)
                if row:
                    vals = list(tree.item(row, "values"))
                    vals[0] = "✓" if vals[0] == "☐" else "☐"
                    tree.item(row, values=vals)

    tree.bind("<Button-1>", on_tree_click)

    # boton para seleccionar todos los archivos
    def seleccionar_todo():
        for iid in tree.get_children():
            vals = list(tree.item(iid, "values"))
            vals[0] = "✓"
            tree.item(iid, values=vals)

    # boton para deseleccionar todos los archivos
    def deseleccionar_todo():
        for iid in tree.get_children():
            vals = list(tree.item(iid, "values"))
            vals[0] = "☐"
            tree.item(iid, values=vals)

    # boton para eliminar los archivos seleccionados
    def eliminar_seleccionados():
        seleccion = [iid for iid in tree.get_children() if tree.item(iid, "values")[0] == "✓"]
        if not seleccion: # si no hay seleccionados mostrar advertencia
            messagebox.showwarning("Atención", "No seleccionaste ningún archivo para eliminar.")
            return

        #solicitar confirmacion antes de eliminar
        confirm = messagebox.askyesno("Confirmar eliminación", "¿Deseas enviar los archivos seleccionados a la papelera?")
        if not confirm:
            return

        #cantidad de archivos eliminados y espacio liberado 
        eliminados = 0
        espacio_liberado = 0
        for item in seleccion:
            ruta = tree.item(item, "values")[3]
            try:
                espacio_liberado += os.path.getsize(ruta)
                if send2trash:
                    send2trash(ruta)
                else:
                    os.remove(ruta)
                tree.delete(item)
                eliminados += 1
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{ruta}\n{e}")

        espacio_mb = espacio_liberado / 1048576
        messagebox.showinfo(
            "Eliminación completada",
            f"Se enviaron {eliminados} archivos a la papelera.\nEspacio liberado: {espacio_mb:.2f} MB."
        )
        lbl_estado.config(text=f"Eliminados {eliminados} archivos | Liberados {espacio_mb:.2f} MB")

    def abrir_papelera():
        try:
            os.startfile("shell:RecycleBinFolder")
        except Exception:
            messagebox.showinfo("Papelera", "No se pudo abrir la papelera de reciclaje.")

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
    btn_sel_todo = ttk.Button(frame_botones, text="Seleccionar todo", command=seleccionar_todo)
    btn_desel_todo = ttk.Button(frame_botones, text="Deseleccionar todo", command=deseleccionar_todo)
    btn_papelera = ttk.Button(frame_botones, text="Abrir papelera", command=abrir_papelera)
    btn_salir = ttk.Button(
        frame_botones,
        text=("Volver" if callable(on_close) else "Salir"),
        command=cerrar_o_volver
    )

    btn_eliminar.pack(side="right", padx=(5, 0))
    btn_cancelar.pack(side="right", padx=(0, 5))
    btn_papelera.pack(side="right", padx=(0, 5))
    btn_desel_todo.pack(side="right", padx=(0, 5))
    btn_sel_todo.pack(side="right", padx=(0, 5))
    btn_salir.pack(side="right", padx=(0, 5))

    iniciar_escaneo()

    return frame
