# 📁 Proyecto: Asistente de Automatización de Archivos

Automatiza tareas comunes con Python: organización, respaldo, limpieza y análisis de archivos.  
Ideal para practicar lógica, condicionales, bucles y manejo del sistema de archivos.

---

## 🧠 Descripción General

Este script permite realizar distintas tareas desde consola:
1. Organizar archivos por tipo  
2. Crear copias de respaldo (backup)  
3. Buscar archivos duplicados  
4. Gestionar almacenamiento (detectar archivos grandes)
5. Limpieza de Archivos Basura
6. Escaneo de Drivers (Sorpresa)

Cada función es independiente y puede ejecutarse desde un **menú principal**.

---

## ⚙️ Requisitos

- **Python 3.x**
- Módulos estándar: `os`, `shutil`, `time`, `datetime`, `tkinter`, `filedialog`, `messagebox`
- Editor recomendado: Visual Studio Code o Thonny
- Sistema operativo: Windows, Linux o macOS

## ➕ Opcional
- Pyinstaller para generar un executable del script para que sea mas amigable al usuario
- Para instalar PYinstaller, desde la terminal de vscode o editor que este usando:
> pip install pyinstaller
- Para generar el executable :
> pyinstaller --onefile --windowed --icon=icono.ico --name "Asistente_de_Archivos" asistente_de_archivos.py
---
