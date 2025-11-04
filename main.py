import tkinter as tk
from tkinter import messagebox, ttk

# importar funciones desde los módulos separados
from organizador import crear_frame_organizador
from gestor_almacenamiento import crear_frame_gestor
from backup_automatico import crear_frame_backup
from eliminar_duplicados import crear_frame_duplicados

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
    tk.Label(frame_sup_izq, text="Organiza tus archivos\n en carpetas segun \n su extensión", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)
    
    def mostrar_organizador():
        frame_principal.pack_forget()
        
        fo = tk.Frame(main_container, bg="#f4f4f4")
        fo.pack(fill="both", expand=True)
        
        def volver_inicio():
            fo.destroy()
            frame_principal.pack(fill="both", expand=True)
        
        # Usar la nueva función crear_frame_organizador
        organizador_ui = crear_frame_organizador(fo, on_close=volver_inicio)
        organizador_ui.pack(fill="both", expand=True)

    # Modificar la línea donde se crea el botón del organizador
    boton1 = crear_boton_con_zoom(frame_sup_izq, "📁 Organizar Archivos", "#4CAF50", mostrar_organizador)
    boton1.pack(pady=10)

    # Botón 2 - Esquina Superior Derecha
    frame_sup_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_sup_der.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_sup_der, text="Archivos Duplicados", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_sup_der, text="Encuentra y gestiona\narchivos duplicados\n", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    #Crear referencia para el frame de duplicados
    duplicados_frame_ref = {"frame": None}
   
    def mostrar_duplicados():
        # ocultar pantalla principal
        frame_principal.pack_forget()
        # crear contenedor de duplicados
        fd = tk.Frame(main_container, bg="#f4f4f4")
        fd.pack(fill="both", expand=True)
        duplicados_frame_ref["frame"] = fd

        def volver_inicio():
            if duplicados_frame_ref["frame"] is not None:
                duplicados_frame_ref["frame"].destroy()
                duplicados_frame_ref["frame"] = None
            frame_principal.pack(fill="both", expand=True)

        # crear el gestor de duplicados dentro del frame fd pasando el callback de volver
        duplicados_ui = crear_frame_duplicados(fd, on_close=volver_inicio)
        duplicados_ui.pack(fill="both", expand=True)

    boton2 = crear_boton_con_zoom(frame_sup_der, "🔍 Buscar Duplicados", "#2196F3", mostrar_duplicados)
    boton2.pack(pady=10)

    # Botón 3 - Esquina Inferior Izquierda
    frame_inf_izq = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_izq.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_izq, text="Copia de Seguridad", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_izq, text="Crea copias de seguridad\nde sus carpetas\n", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

    # Crear referencia para el frame de backup
    backup_frame_ref = {"frame": None}

    def mostrar_backup():
        # ocultar pantalla principal
        frame_principal.pack_forget()
        # crear contenedor del backup
        fb = tk.Frame(main_container, bg="#f4f4f4")
        fb.pack(fill="both", expand=True)
        backup_frame_ref["frame"] = fb

        def volver_inicio():
            if backup_frame_ref["frame"] is not None:
                backup_frame_ref["frame"].destroy()
                backup_frame_ref["frame"] = None
            frame_principal.pack(fill="both", expand=True)

        # crear el backup dentro del frame fb pasando el callback de volver
        backup_ui = crear_frame_backup(fb, on_close=volver_inicio)
        backup_ui.pack(fill="both", expand=True)

    boton3 = crear_boton_con_zoom(frame_inf_izq, "⚙️ Copia de Seguridad", "#FF9800", mostrar_backup)
    boton3.pack(pady=10)

    # Botón 4 - Esquina Inferior Derecha (gestor embebido)
    frame_inf_der = tk.Frame(frame_principal, bg="#f4f4f4")
    frame_inf_der.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    tk.Label(frame_inf_der, text="Gestor de almacenamiento", font=("Arial", 14, "bold"), bg="#f4f4f4").pack()
    tk.Label(frame_inf_der, text="Busca archivos grandes\n(mayores a 512MB) y elija\nque hacer (eliminar o mantener.)", font=("Arial", 12), bg="#f4f4f4").pack(pady=5)

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

if __name__ == "__main__":
    crear_interfaz()