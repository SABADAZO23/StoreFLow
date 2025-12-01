"""Utilidades para ventanas Tkinter."""
import os
import tkinter as tk
from typing import Optional

from ui.config import BG_COLOR, TEXT_COLOR, FONT_FAMILY, DEFAULT_LOGO_PATH


def center_window(window: tk.Tk, width: Optional[int] = None, height: Optional[int] = None, parent: Optional[tk.Tk] = None):
    """Centra una ventana en la pantalla o respecto a la ventana padre.
    
    Args:
        window: Ventana a centrar
        width: Ancho de la ventana (opcional)
        height: Alto de la ventana (opcional)
        parent: Ventana padre (si es Toplevel)
    """
    window.update_idletasks()

    if width and height:
        window.geometry(f"{width}x{height}")
        window.update_idletasks()
    else:
        width = window.winfo_width()
        height = window.winfo_height()

    if isinstance(window, tk.Toplevel) and parent:
        parent.update_idletasks()
        main_x = parent.winfo_x()
        main_y = parent.winfo_y()
        main_width = parent.winfo_width()
        main_height = parent.winfo_height()

        x = main_x + (main_width // 2) - (width // 2)
        y = main_y + (main_height // 2) - (height // 2)
    else:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")


def load_logo(parent: tk.Frame) -> bool:
    """Carga el logo y lo muestra en el widget padre.
    
    Returns True si se cargó la imagen, False si se usó placeholder.
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    assets_logo = os.path.join(project_root, "ui", "assets", "logo.png")
    logo_path = None

    if os.path.exists(assets_logo):
        logo_path = assets_logo
    elif os.path.exists(DEFAULT_LOGO_PATH):
        logo_path = DEFAULT_LOGO_PATH

    if logo_path:
        try:
            logo_img = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(parent, image=logo_img, bg=BG_COLOR)
            logo_label.image = logo_img
            logo_label.pack(pady=(0, 10))
            return True
        except Exception:
            pass

    logo_label = tk.Label(parent, text="[Logo]", bg=BG_COLOR, fg=TEXT_COLOR,
                         font=(FONT_FAMILY, 14, "bold"))
    logo_label.pack(pady=(0, 10))
    return False
