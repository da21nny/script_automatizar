# 📁 Proyecto: Asistente de Automatización de Archivos

Automatiza tareas comunes con Python: organización, respaldo, limpieza y análisis de archivos.  
Ideal para practicar lógica, condicionales, bucles y manejo del sistema de archivos.

---

## 🧠 Descripción General

Este script permite realizar distintas tareas desde consola:
1. Organizar archivos por tipo  
2. Crear copias de respaldo (backup)  
3. Simular un formateo de disco (educativo)  
4. Buscar archivos duplicados  
5. Gestionar almacenamiento (detectar archivos grandes)

Cada función es independiente y puede ejecutarse desde un **menú principal**.

---

## ⚙️ Requisitos

- **Python 3.x**
- Módulos estándar: `os`, `shutil`, `time`, `datetime`,
- Editor recomendado: Visual Studio Code o Thonny
- Sistema operativo: Windows, Linux o macOS

---

## 🧩 Menú principal (ejemplo)

```python
def menu():
    print("""
    === Asistente de Automatización de Archivos ===
    1. Organizar archivos
    2. Crear backup
    3. Simular formateo
    4. Buscar duplicados
    5. Gestor de almacenamiento
    0. Salir
    """)
    opcion = input("Selecciona una opción: ")
    if opcion == "1":
        organizar_archivos()
    elif opcion == "2":
        crear_backup()
    elif opcion == "3":
        simular_formateo()
    elif opcion == "4":
        buscar_duplicados()
    elif opcion == "5":
        gestor_almacenamiento()
    else:
        print("¡Hasta luego!")
