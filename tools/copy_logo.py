"""Copia y redimensiona un logo desde una ruta absoluta hacia `ui/assets/logo.png`.

Uso:
    python tools\copy_logo.py "C:\Users\Usuario\Pictures\Screenshots\logo.png"

Si la imagen no existe o falla la lectura, mostrará un error.

Este script usa Pillow para abrir/redimensionar y guardar PNG.
"""
import sys
import os
from PIL import Image

MAX_SIZE = (256, 256)

def copy_and_resize(src_path, dst_path):
    if not os.path.exists(src_path):
        print(f"Ruta de origen no encontrada: {src_path}")
        return 2

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    try:
        with Image.open(src_path) as im:
            im = im.convert('RGBA')
            im.thumbnail(MAX_SIZE, Image.LANCZOS)
            im.save(dst_path, format='PNG')
        print(f"Logo copiado y redimensionado a: {dst_path}")
        return 0
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python tools\\copy_logo.py <ruta_origen_logo>")
        sys.exit(2)
    src = sys.argv[1]
    dst = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'assets', 'logo.png')
    code = copy_and_resize(src, dst)
    sys.exit(code)
