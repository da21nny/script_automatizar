import tkinter as tk
from tkinter import messagebox, ttk

# importar funciones desde los módulos separados
from organizador import crear_frame_organizador
from gestor_almacenamiento import crear_frame_gestor
from backup_automatico import crear_frame_backup
from eliminar_duplicados import crear_frame_duplicados
import sorpresa  # agregado
from limpieza import crear_frame_limpieza

#función para crear la interfaz principal
def crear_interfaz():
    root = tk.Tk()
    root.title("🗂️ Asistente de Archivos - Versión GUI")
    root.geometry("840x480")  # ampliada horizontalmente
    root.resizable(False, False)
    root.configure(bg="#f4f4f4")

    main_container = tk.Frame(root, bg="#f4f4f4")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    frame_principal = tk.Frame(main_container, bg="#f4f4f4")
    frame_principal.pack(fill="both", expand=True)

    # 3 columnas para los nuevos botones
    frame_principal.grid_columnconfigure(0, weight=1)
    frame_principal.grid_columnconfigure(1, weight=1)
    frame_principal.grid_columnconfigure(2, weight=1)
    frame_principal.grid_rowconfigure(0, weight=1)
    frame_principal.grid_rowconfigure(1, weight=1)

    # === BOTONES DE LA PRIMERA FILA ===
    # 1️⃣ Organizador
    frame_sup_izq = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_sup_izq.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_sup_izq, text="Organizador de Archivos", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_sup_izq, text="Organiza tus archivos\n en carpetas segun su extensión", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    #función para mostrar el organizador
    def mostrar_organizador():
        frame_principal.pack_forget()
        fo = tk.Frame(main_container, bg="#f4f4f4")
        fo.pack(fill="both", expand=True)

        def volver_inicio():
            fo.destroy()
            frame_principal.pack(fill="both", expand=True)

        organizador_ui = crear_frame_organizador(fo, on_close=volver_inicio)
        organizador_ui.pack(fill="both", expand=True)

    boton1 = crear_boton_con_zoom(frame_sup_izq, "📁 Organizar Archivos", "#4CAF50", mostrar_organizador)
    boton1.pack(pady=10)

    # 2️⃣ Duplicados
    frame_sup_centro = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_sup_centro.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_sup_centro, text="Archivos Duplicados", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_sup_centro, text="Encuentra y gestiona\narchivos duplicados", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    duplicados_frame_ref = {"frame": None}

    #función para mostrar el buscador de duplicados
    def mostrar_duplicados():
        frame_principal.pack_forget()
        fd = tk.Frame(main_container, bg="#f4f4f4")
        fd.pack(fill="both", expand=True)
        duplicados_frame_ref["frame"] = fd

        def volver_inicio():
            if duplicados_frame_ref["frame"]:
                duplicados_frame_ref["frame"].destroy()
                duplicados_frame_ref["frame"] = None
            frame_principal.pack(fill="both", expand=True)

        duplicados_ui = crear_frame_duplicados(fd, on_close=volver_inicio)
        duplicados_ui.pack(fill="both", expand=True)

    boton2 = crear_boton_con_zoom(frame_sup_centro, "🔍 Buscar Duplicados", "#2196F3", mostrar_duplicados)
    boton2.pack(pady=10)

    # 3️⃣ Limpieza de Archivos Basura
    frame_sup_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_sup_der.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_sup_der, text="Limpieza de Archivos Basura", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_sup_der, text="Elimina archivos temporales,\nlogs y otros innecesarios", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    #función para mostrar el limpiador de archivos basura
    def mostrar_limpieza_info():
        frame_principal.pack_forget()
        fl = tk.Frame(main_container, bg="#f4f4f4")
        fl.pack(fill="both", expand=True)

        def volver_inicio():
            fl.destroy()
            frame_principal.pack(fill="both", expand=True)

        limpieza_ui = crear_frame_limpieza(fl, on_close=volver_inicio)
        limpieza_ui.pack(fill="both", expand=True)

    boton3 = crear_boton_con_zoom(frame_sup_der, "🧹 Limpiar Archivos Basura", "#607D8B", mostrar_limpieza_info)
    boton3.pack(pady=10)

    # === BOTONES DE LA SEGUNDA FILA ===
    # 4️⃣ Backup
    frame_inf_izq = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_izq.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_izq, text="Copia de Seguridad", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_izq, text="Crea copias de seguridad\nde tus carpetas", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    backup_frame_ref = {"frame": None}

    #función para mostrar el backup
    def mostrar_backup():
        frame_principal.pack_forget()
        fb = tk.Frame(main_container, bg="#f4f4f4")
        fb.pack(fill="both", expand=True)
        backup_frame_ref["frame"] = fb

        def volver_inicio():
            if backup_frame_ref["frame"]:
                backup_frame_ref["frame"].destroy()
                backup_frame_ref["frame"] = None
            frame_principal.pack(fill="both", expand=True)

        backup_ui = crear_frame_backup(fb, on_close=volver_inicio)
        backup_ui.pack(fill="both", expand=True)

    boton4 = crear_boton_con_zoom(frame_inf_izq, "⚙️ Copia de Seguridad", "#FF9800", mostrar_backup)
    boton4.pack(pady=10)

    # 5️⃣ Gestor de almacenamiento
    frame_inf_centro = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_centro.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_centro, text="Gestor de Almacenamiento", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_centro, text="Busca archivos grandes\n(mayores a 512MB)", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    gestor_frame_ref = {"frame": None}

    #función para mostrar el gestor de almacenamiento
    def mostrar_gestor():
        frame_principal.pack_forget()
        fg = tk.Frame(main_container, bg="#f4f4f4")
        fg.pack(fill="both", expand=True)
        gestor_frame_ref["frame"] = fg

        def volver_inicio():
            if gestor_frame_ref["frame"]:
                gestor_frame_ref["frame"].destroy()
                gestor_frame_ref["frame"] = None
            frame_principal.pack(fill="both", expand=True)

        gestor_ui = crear_frame_gestor(fg, on_close=volver_inicio)
        gestor_ui.pack(fill="both", expand=True)

    boton5 = crear_boton_con_zoom(frame_inf_centro, "🔧 Gestionar Espacio", "#9C27B0", mostrar_gestor)
    boton5.pack(pady=10)

    # 6️⃣ Escanear Driver (usa sorpresa.py)
    frame_inf_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_der.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_der, text="Escanear Drivers", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_der, text="Analiza controladores del sistema\n(modo sorpresa 🧠)", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    #función para ejecutar la sorpresa
    def ejecutar_sorpresa():
        frame_principal.pack_forget()
        fs = tk.Frame(main_container, bg="#f4f4f4")
        fs.pack(fill="both", expand=True)

        def volver_inicio():
            fs.destroy()
            frame_principal.pack(fill="both", expand=True)

    # Ahora crea el frame de sorpresa dentro de fs
        sorpresa_ui = sorpresa.crear_frame_sorpresa(fs, on_close=volver_inicio)
        sorpresa_ui.pack(fill="both", expand=True)
    
    boton6 = crear_boton_con_zoom(frame_inf_der, "💽 Escanear Drivers", "#3F51B5", ejecutar_sorpresa)
    boton6.pack(pady=10)

    tk.Label(root, text="Desarrollado por Los Penguin 1 💻", font=("Arial", 9), bg="#f4f4f4", fg="#888").pack(side="bottom", pady=10)

    root.mainloop()

#función para crear botones con efecto zoom
def crear_boton_con_zoom(frame, texto, color, comando=None):
    boton = tk.Button(frame, text=texto, font=("Arial", 12), bg=color, fg="white", command=comando)
    def on_enter(e): boton.config(font=("Arial", 13, "bold"))
    def on_leave(e): boton.config(font=("Arial", 12))
    boton.bind("<Enter>", on_enter)
    boton.bind("<Leave>", on_leave)
    return boton

#ejecutar la interfaz principal
if __name__ == "__main__":
    crear_interfaz()
