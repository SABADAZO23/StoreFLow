#!/usr/bin/env python3
"""Script para crear un ejecutable de TiendaHub usando PyInstaller."""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Construye el ejecutable del proyecto."""
    
    # Obtener ruta del proyecto
    project_root = Path(__file__).parent.absolute()
    main_script = project_root / "main.py"
    
    if not main_script.exists():
        print(f"❌ Error: No se encontró {main_script}")
        sys.exit(1)
    
    print("🔨 Construyendo ejecutable de TiendaHub...")
    print(f"📁 Directorio del proyecto: {project_root}")
    
    # Configuración de PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=TiendaHub",  # Nombre del ejecutable
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin ventana de consola
        "--icon=NONE",  # Sin icono personalizado (opcional: agregar luego)
        "--add-data=configuracion:configuracion",  # Incluir carpeta de configuración
        "--add-data=ui:ui",  # Incluir módulos UI
        "--add-data=autenticacion:autenticacion",  # Incluir módulos de autenticación
        "--add-data=base_datos:base_datos",  # Incluir módulos de BD
        "--collect-all=firebase_admin",  # Recopilar todos los archivos de firebase_admin
        "--hidden-import=tkinter",
        "--hidden-import=firebase_admin",
        "--hidden-import=firebase_admin.auth",
        "--hidden-import=firebase_admin.firestore",
        "--distpath=dist",  # Directorio de salida
        "--buildpath=build",  # Directorio de construcción
        "--specpath=.",  # Ubicación del archivo .spec
        str(main_script)
    ]
    
    try:
        print(f"\n📦 Ejecutando: {' '.join(pyinstaller_cmd)}\n")
        result = subprocess.run(pyinstaller_cmd, check=True)
        
        exe_path = project_root / "dist" / "TiendaHub.exe"
        
        if exe_path.exists():
            print("\n✅ ¡Ejecutable creado exitosamente!")
            print(f"📍 Ubicación: {exe_path}")
            print(f"📊 Tamaño: {exe_path.stat().st_size / (1024*1024):.2f} MB")
            print("\n💡 Instrucciones:")
            print(f"1. El ejecutable está en: {exe_path.parent}")
            print(f"2. Asegúrate de tener 'serviceAccountKey.json' en la misma carpeta que el .exe")
            print("3. Ejecuta: TiendaHub.exe")
        else:
            print(f"⚠️ Advertencia: No se encontró {exe_path}")
            print("Revisa los errores arriba.")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la construcción: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
