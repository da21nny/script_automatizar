import os
import shutil
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Intentar importar send2trash para mover archivos a la papelera del sistema
try:
    from send2trash import send2trash
except Exception:
    send2trash = None

#función para crear el frame del limpiador de archivos basura
def crear_frame_limpieza(parent, on_close=None):
    frame = tk.Frame(parent, bg="#f4f4f4")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(3, weight=1)

    title = tk.Label(frame, text="🧹 Limpiador simple", font=("Arial", 14, "bold"), bg="#f4f4f4")
    title.grid(row=0, column=0, sticky="w", padx=10, pady=(10,6))

    controles = tk.Frame(frame, bg="#f4f4f4")
    controles.grid(row=1, column=0, sticky="w", padx=10, pady=6)

    umbral_var = tk.IntVar(value=512)  # MB
    dias_var = tk.IntVar(value=365)
    modo_auto_var = tk.BooleanVar(value=False)

    tk.Label(controles, text="Umbral MB:", bg="#f4f4f4").grid(row=0, column=0, padx=(0,4))
    tk.Entry(controles, width=6, textvariable=umbral_var).grid(row=0, column=1, padx=(0,8))
    tk.Label(controles, text="Días:", bg="#f4f4f4").grid(row=0, column=2, padx=(0,4))
    tk.Entry(controles, width=6, textvariable=dias_var).grid(row=0, column=3, padx=(0,8))
    tk.Checkbutton(controles, text="Mover automáticamente (solo temporales/vacíos)", variable=modo_auto_var, bg="#f4f4f4").grid(row=0, column=4, padx=6)
    
    btn_frame = tk.Frame(frame, bg="#f4f4f4")
    btn_frame.grid(row=2, column=0, sticky="w", padx=10, pady=(0,6))

    progress = ttk.Progressbar(frame, mode="indeterminate", length=600)
    progress.grid(row=3, column=0, sticky="we", padx=10, pady=(2,6))

    resultado_label = tk.Label(frame, text="Estado: listo", anchor="w", bg="#f4f4f4")
    resultado_label.grid(row=4, column=0, sticky="we", padx=10, pady=(0,8))

    # Nueva tabla con checkbox simulado
    cols = ("check", "nombre", "tipo", "size_mb", "created", "ruta")
    tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="none", height=12)
    tree.heading("check", text="✔")
    tree.heading("nombre", text="Nombre")
    tree.heading("tipo", text="Tipo")
    tree.heading("size_mb", text="Tamaño (MB)")
    tree.heading("created", text="Creación")
    tree.heading("ruta", text="Ruta")
    tree.column("check", width=32, anchor="center")
    tree.column("nombre", width=160)
    tree.column("tipo", width=80)
    tree.column("size_mb", width=90, anchor="e")
    tree.column("created", width=140)
    tree.column("ruta", width=320)
    tree.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.grid(row=5, column=1, sticky="ns")
    tree.configure(yscrollcommand=vsb.set)

#=== LÓGICA DE ESCANEO Y MANEJO DE ARCHIVOS ===
    HOME = Path.home()
    SEARCH_DIRS = [HOME / d for d in ("Downloads", "Desktop", "Documents", "Pictures", "Music", "Videos", "Temp")]
    TEMP_EXTS = {".tmp", ".part", ".crdownload", ".bak"}
    LOCAL_TRASH = HOME / "Limpieza_Trash"
    if send2trash is None:
        LOCAL_TRASH.mkdir(exist_ok=True)

    state = {"running": False, "cancel": False, "stack": []}

    def is_candidate(p: Path, umbral_mb, dias, now):
        try:
            size_mb = round(p.stat().st_size / (1024 * 1024), 2)
            mtime = p.stat().st_mtime
            ctime = p.stat().st_ctime
        except Exception:
            return None
        tipo = None
        if size_mb == 0:
            tipo = "vacío"
        elif p.suffix.lower() in TEMP_EXTS or p.name.startswith("~"):
            tipo = "temporal"
        elif size_mb >= umbral_mb:
            tipo = "grande"
        elif (now - mtime) >= (dias * 24 * 3600):
            tipo = "antiguo"
        if tipo:
            return {
                "nombre": p.name,
                "tipo": tipo,
                "size_mb": size_mb,
                "created": time.strftime("%Y-%m-%d %H:%M", time.localtime(ctime)),
                "ruta": str(p)
            }
        return None

    def process_batch(umbral_mb, dias, batch_size=200):
        if state["cancel"]:
            state["running"] = False
            progress.stop()
            resultado_label.config(text="Estado: cancelado.")
            scan_btn.config(state="normal")
            cancel_btn.config(state="disabled")
            return
        
        now = time.time()
        processed = 0
        while processed < batch_size and state["stack"]:
            current_dir, depth = state["stack"].pop()
            try:
                with os.scandir(current_dir) as it:
                    for entry in it:
                        if state["cancel"]:
                            break
                        try:
                            p = Path(entry.path)
                            if entry.is_file(follow_symlinks=False):
                                cand = is_candidate(p, umbral_mb, dias, now)
                                if cand:
                                    tree.insert("", "end", values=("☐", cand["nombre"], cand["tipo"], cand["size_mb"], cand["created"], cand["ruta"]))
                            elif entry.is_dir(follow_symlinks=False) and depth > 0:
                                state["stack"].append((p, depth - 1))
                        except Exception:
                            continue
            except Exception:
                continue
            processed += 1

        if state["stack"] and not state["cancel"]:
            parent.after(30, lambda: process_batch(umbral_mb, dias, batch_size))
        else:
            state["running"] = False
            progress.stop()
            if state["cancel"]:
                resultado_label.config(text="Estado: escaneo cancelado.")
            else:
                count = len(tree.get_children())
                resultado_label.config(text=f"Estado: terminado — {count} elementos encontrados.")
                if modo_auto_var.get() and count > 0:
                    target_name = "la Papelera de reciclaje" if send2trash else str(LOCAL_TRASH)
                    if messagebox.askyesno("Mover automáticamente", f"Mover temporales y vacíos a {target_name}?"):
                        moved = 0
                        for iid in list(tree.get_children()):
                            tipo = tree.item(iid, "values")[2]
                            ruta = tree.item(iid, "values")[5]
                            if tipo in ("temporal", "vacío"):
                                try:
                                    src = Path(ruta)
                                    if src.exists():
                                        if send2trash:
                                            send2trash(str(src))
                                        else:
                                            dest = LOCAL_TRASH / f"{int(time.time())}_{src.name}"
                                            shutil.move(str(src), str(dest))
                                        moved += 1
                                        tree.delete(iid)
                                except Exception:
                                    continue
                        dest_text = "Papelera de reciclaje" if send2trash else str(LOCAL_TRASH)
                        resultado_label.config(text=f"Estado: movidos {moved} archivos a {dest_text}")
            scan_btn.config(state="normal")
            cancel_btn.config(state="disabled")

    #función para iniciar el escaneo
    def iniciar_escaneo():
        if state["running"]:
            messagebox.showinfo("Escaneo", "Ya hay un escaneo en curso.")
            return
        tree.delete(*tree.get_children())
        resultado_label.config(text="Estado: iniciando escaneo...")
        umbral_mb = max(1, umbral_var.get())
        dias = max(0, dias_var.get())
        max_depth = 3
        state["stack"] = []
        for d in SEARCH_DIRS:
            if d.exists() and d.is_dir():
                state["stack"].append((d, max_depth))
        if not state["stack"]:
            resultado_label.config(text="Estado: no hay carpetas típicas para escanear.")
            return
        state["running"] = True
        state["cancel"] = False
        progress.start(10)
        scan_btn.config(state="disabled")
        cancel_btn.config(state="normal")
        parent.after(50, lambda: process_batch(umbral_mb, dias))

    #función para cancelar el escaneo
    def cancelar_escaneo():
        if not state["running"]:
            return
        state["cancel"] = True
        resultado_label.config(text="Estado: cancelando...")
        progress.stop()
        cancel_btn.config(state="disabled")

    # Manejo de checkboxes simulados
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

    #función para mover los archivos seleccionados a la papelera
    def mover_seleccionados():
        sel = [iid for iid in tree.get_children() if tree.item(iid, "values")[0] == "✓"]
        if not sel:
            messagebox.showinfo("Seleccionar", "Marca uno o más elementos con la casilla.")
            return
        target_name = "la Papelera de reciclaje" if send2trash else str(LOCAL_TRASH)
        if not messagebox.askyesno("Confirmar", f"Mover seleccionados a {target_name}?"):
            return
        moved = 0
        for iid in list(sel):
            ruta = tree.item(iid, "values")[5]
            try:
                src = Path(ruta)
                if src.exists():
                    if send2trash:
                        send2trash(str(src))
                    else:
                        dest = LOCAL_TRASH / f"{int(time.time())}_{src.name}"
                        shutil.move(str(src), str(dest))
                    moved += 1
                    tree.delete(iid)
            except Exception:
                continue
        dest_text = "Papelera de reciclaje" if send2trash else str(LOCAL_TRASH)
        resultado_label.config(text=f"Estado: movidos {moved} archivos a {dest_text}")

    #función para abrir la papelera
    def abrir_trash():
        try:
            if send2trash:
                os.startfile("shell:RecycleBinFolder")
            else:
                os.startfile(str(LOCAL_TRASH))
        except Exception:
            msg = "Papelera del sistema (requiere send2trash para uso completo)." if send2trash else f"Papelera local: {LOCAL_TRASH}"
            messagebox.showinfo("Papelera", msg)
    def seleccionar_todo():
        for iid in tree.get_children():
            vals = list(tree.item(iid, "values"))
            vals[0] = "✓"
            tree.item(iid, values=vals)

    # Botones de acción
    scan_btn = tk.Button(btn_frame, text="🔎 Escanear", command=iniciar_escaneo, bg="#2196F3", fg="white")
    scan_btn.grid(row=0, column=0, padx=4)
    cancel_btn = tk.Button(btn_frame, text="✖ Cancelar", command=cancelar_escaneo, bg="#B71C1C", fg="white", state="disabled")
    cancel_btn.grid(row=0, column=1, padx=4)
    tk.Button(btn_frame, text="🗑️ Mover seleccionados", command=mover_seleccionados, bg="#f44336", fg="white").grid(row=0, column=2, padx=4)
    tk.Button(btn_frame, text="📁 Abrir papelera", command=abrir_trash, bg="#9E9E9E", fg="white").grid(row=0, column=3, padx=4)
    tk.Button(btn_frame, text="↩️ Volver", command=(on_close if on_close else frame.destroy), bg="#607D8B", fg="white").grid(row=0, column=4, padx=8)
    tk.Button(btn_frame, text="☑️ Seleccionar Todo", command=seleccionar_todo, bg="#8BC34A", fg="white").grid(row=0, column=5, padx=4)

    nota_text = "Los archivos se moverán a la Papelera de reciclaje del sistema." if send2trash else f"send2trash no instalado. Los archivos se moverán a: {LOCAL_TRASH}"
    nota = tk.Label(frame, text=nota_text + "\n(Se recomienda revisar antes de vaciar)", bg="#f4f4f4", fg="#666", justify="left")
    nota.grid(row=6, column=0, sticky="w", padx=10, pady=(6,10))

    return frame