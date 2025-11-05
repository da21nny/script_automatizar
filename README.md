# 📁 Proyecto: PYClean - Gestor de Archivos - Version GUI

Automatiza tareas comunes con Python: Organización de archivos, Copia de Seguridad, Limpieza de archivos basura, Eliminacion de archivos Duplicados, Gestion de Almacenamiento, Escaner de Drivers(Proyecto a futuro).  

Proyecto nos ayudo con la lógica, condicionales, bucles, manejo del sistema de archivos y entorno grafico.

---

## 🧠 Descripción General

Este script permite realizar distintas tareas desde una Interfaz Grafica (TKinter):
1. Organizar archivos por tipo  
2. Crear copias de respaldo (backup)  
3. Buscar archivos duplicados  
4. Gestionar almacenamiento (detectar archivos grandes)
5. Limpieza de Archivos Basura
6. Escaneo de Drivers (Proyecto a futuro)

Cada función es independiente y se ejecuta desde un **menú principal**.

---

## ⚙️ Requisitos

- **Python > 3.11
- Módulos estándar: `os`, `shutil`, `time`, `datetime`, `tkinter`, `filedialog`, `messagebox`, `send2trash`
- Editor recomendado: Visual Studio Code
- Sistema operativo: Solo Windows 10 y posteriores

## ➕ Para empaquetar el entorno grafico en un executable (.exe)
- Pyinstaller para generar un executable del script para que sea mas amigable al usuario
- Para instalar PYinstaller, desde la terminal de vscode o editor que este usando:
> pip install pyinstaller
- Algunas funciones necesitan Send2Trash, incluir en el pip:
> pip install send2trash
- Para generar el executable :
> pyinstaller --onefile --windowed --icon=icono.ico --add-data "bsod.gif;." --name "PYClean" main.py
---
