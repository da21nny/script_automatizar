import os
import shutil
from tkinter import *
from tkinter import filedialog, messagebox, ttk

def crear_frame_organizador(parent, on_close=None):
    """
    Crea y devuelve un Frame con el organizador de archivos
    - parent: widget contenedor donde se añadirá el Frame
    - on_close: callback opcional que se llamará al pulsar 'Volver'
    """
    frame = Frame(parent)
    
    # Frame principal
    main_frame = Frame(frame, padx=10, pady=10)
    main_frame.pack(fill=BOTH, expand=True)
    
    # Título
    titulo = Label(main_frame, text="Organizador de Archivos", font=("Arial", 14, "bold"))
    titulo.pack(pady=5)
    
    # Botón seleccionar carpeta
    btn_seleccionar = Button(main_frame, text="Seleccionar Carpeta", 
                            command=lambda: seleccionar_carpeta())
    btn_seleccionar.pack(pady=5)
    
    # Barra de progreso
    progress = ttk.Progressbar(main_frame, mode='determinate')
    progress.pack(fill=X, pady=5)
    
    # Lista de archivos
    frame_lista = Frame(main_frame)
    frame_lista.pack(fill=BOTH, expand=True)
    
    scrollbar = Scrollbar(frame_lista)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    lista_archivos = Listbox(frame_lista, yscrollcommand=scrollbar.set)
    lista_archivos.pack(fill=BOTH, expand=True)
    scrollbar.config(command=lista_archivos.yview)
    
    # Frame para botones
    frame_botones = Frame(main_frame)
    frame_botones.pack(fill=X, pady=5)
    
    carpeta_seleccionada = None
    
    # Agregar variable para almacenar movimientos
    movimientos = []
    
    def seleccionar_carpeta():
        nonlocal carpeta_seleccionada
        carpeta_seleccionada = filedialog.askdirectory(title="Selecciona la carpeta a organizar")
        if carpeta_seleccionada:
            btn_seleccionar.config(text=f"Carpeta: {os.path.basename(carpeta_seleccionada)}")
            
    def procesar_archivos(simular=True):
        if not carpeta_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor seleccione una carpeta primero")
            return
            
        lista_archivos.delete(0, END)
        total = 0
        otros = 0
        carpetas_creadas = set()
        # Limpiar movimientos anteriores si no es simulación
        if not simular:
            movimientos.clear()
        
        archivos = [f for f in os.listdir(carpeta_seleccionada) 
                   if os.path.isfile(os.path.join(carpeta_seleccionada, f))]
        
        progress['maximum'] = len(archivos)
        
        for i, archivo in enumerate(archivos):
            ruta = os.path.join(carpeta_seleccionada, archivo)
            ext = archivo.split(".")[-1].lower()
            
            if ext in reglas:
                destino = os.path.join(carpeta_seleccionada, reglas[ext])
                categoria = reglas[ext]
            else:
                destino = os.path.join(carpeta_seleccionada, "Otros")
                categoria = "Otros"
                otros += 1
                
            if not simular:
                os.makedirs(destino, exist_ok=True)
                carpetas_creadas.add(categoria)
                ruta_destino = os.path.join(destino, archivo)
                shutil.move(ruta, ruta_destino)
                # Guardar movimiento para poder deshacerlo
                movimientos.append((ruta_destino, ruta))
            
            lista_archivos.insert(END, f"{'[Simulación] ' if simular else ''}Moviendo: {archivo} → {categoria}")
            lista_archivos.see(END)
            total += 1
            
            progress['value'] = i + 1
            frame.update_idletasks()
            
        resultado = f"{'[Simulación] ' if simular else ''}Se {'procesarían' if simular else 'procesaron'} {total} archivos\n"
        resultado += f"{'Se crearían' if simular else 'Se crearon'} {len(carpetas_creadas)} carpetas\n"
        resultado += f"{otros} archivos {'irían' if simular else 'fueron'} a la carpeta 'Otros'"
        lbl_resultado.config(text=resultado)
        
        # Habilitar/deshabilitar botón deshacer
        btn_deshacer.config(state="normal" if movimientos else "disabled")
    
    def deshacer_cambios():
        if not movimientos:
            return
            
        lista_archivos.delete(0, END)
        progress['maximum'] = len(movimientos)
        
        for i, (origen, destino) in enumerate(reversed(movimientos)):
            try:
                if os.path.exists(origen):
                    shutil.move(origen, destino)
                    lista_archivos.insert(END, f"Deshaciendo: {os.path.basename(origen)} → {os.path.dirname(destino)}")
                    lista_archivos.see(END)
            except Exception as e:
                lista_archivos.insert(END, f"Error al deshacer {os.path.basename(origen)}: {str(e)}")
            
            progress['value'] = i + 1
            frame.update_idletasks()
        
        movimientos.clear()
        lbl_resultado.config(text="Se han deshecho todos los cambios")
        btn_deshacer.config(state="disabled")
        
        # Intentar eliminar carpetas vacías
        for categoria in reglas.values():
            try:
                ruta_categoria = os.path.join(carpeta_seleccionada, categoria)
                if os.path.exists(ruta_categoria) and not os.listdir(ruta_categoria):
                    os.rmdir(ruta_categoria)
            except:
                pass
    
    # Botones de acción
    btn_simular = Button(
        frame_botones, text="Simular", command=lambda: procesar_archivos(True),
        font=("Arial", 9, "bold"), height=1, width=10, padx=5, pady=2
    )
    btn_simular.pack(side=LEFT, padx=4)

    btn_ejecutar = Button(
        frame_botones, text="Ejecutar", command=lambda: procesar_archivos(False),
        font=("Arial", 9, "bold"), height=1, width=10, padx=5, pady=2
    )
    btn_ejecutar.pack(side=LEFT, padx=4)

    btn_deshacer = Button(
        frame_botones, text="Deshacer", command=deshacer_cambios, state="disabled",
        font=("Arial", 9, "bold"), height=1, width=10, padx=5, pady=2
    )
    btn_deshacer.pack(side=LEFT, padx=4)

    def volver():
        if callable(on_close):
            on_close()
        else:
            parent.winfo_toplevel().destroy()

    btn_volver = Button(
        frame_botones, text="Volver", command=volver,
        font=("Arial", 9, "bold"), height=1, width=10, padx=5, pady=2
    )
    btn_volver.pack(side=RIGHT, padx=4)

    # Label para resultados
    lbl_resultado = Label(main_frame, text="", wraplength=580)
    lbl_resultado.pack(pady=5)
    
    return frame

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