"""Componentes del sidebar de la aplicación."""
import tkinter as tk
from tkinter import messagebox

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL,
    FONT_SIZE_BUTTON, FONT_SIZE_SMALL, FONT_SIZE_TINY, PADDING_SMALL,
    PADDING_MEDIUM, PADDING_LARGE
)
from ui.window_utils import load_logo


class ScrollableFrame(tk.Frame):
    """Frame con scrollbar para contenido que excede el espacio disponible."""
    
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.canvas = tk.Canvas(self, bg=parent["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=parent["bg"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Permitir scroll con la rueda del ratón
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class SidebarPanel:
    """Construye y gestiona el panel lateral (sidebar)."""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.sidebar = tk.Frame(parent, bg=BG_COLOR, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
    def build(self):
        """Construye todos los componentes del sidebar."""
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        
        # Logo
        load_logo(self.sidebar)
        
        # Panel de login
        self._build_login_panel()
        
        # Separador
        tk.Frame(self.sidebar, bg=TEXT_COLOR, height=1).pack(fill="x", pady=PADDING_LARGE)
        
        # Menú
        self._build_menu()
        
        return self.sidebar

    def _build_login_panel(self):
        """Construye panel de login/sesión."""
        login_frame = tk.Frame(self.sidebar, bg=BG_COLOR)
        login_frame.pack(fill="x", pady=(0, PADDING_MEDIUM))

        tk.Label(login_frame, textvariable=self.main_window.current_user_var, 
                bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack()

        tk.Label(login_frame, textvariable=self.main_window.session_var, 
                bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_TINY)).pack()

        self.main_window._login_btn = tk.Button(
            login_frame, text="Login", bg="white", fg=TEXT_COLOR,
            command=self.main_window._dialog_login, font=(FONT_FAMILY, FONT_SIZE_BUTTON), bd=0
        )
        self.main_window._login_btn.pack(fill="x", pady=(PADDING_MEDIUM, 0))

        tk.Button(login_frame, text="Registrar", bg="white", fg=TEXT_COLOR,
                 command=self.main_window._dialog_register, font=(FONT_FAMILY, FONT_SIZE_BUTTON), bd=0).pack(fill="x", pady=(PADDING_MEDIUM, 0))

        self.main_window._view_session_btn = tk.Button(
            login_frame, text="Ver sesión", bg="white", fg=TEXT_COLOR,
            command=self.main_window._view_session_data, font=(FONT_FAMILY, FONT_SIZE_BUTTON), bd=0
        )
        self.main_window._view_session_btn.pack(fill="x", pady=(PADDING_MEDIUM, 0))

    def _build_menu(self):
        """Construye menú principal con scroll."""
        tk.Label(self.sidebar, text="Menú Principal", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", pady=(PADDING_SMALL, PADDING_SMALL))

        # Frame con scroll
        scrollable = ScrollableFrame(self.sidebar, bg=BG_COLOR, height=300)
        scrollable.pack(fill="both", expand=True, pady=(0, PADDING_MEDIUM))

        btn_style = {
            "bg": ACCENT_COLOR,
            "fg": "white",
            "activebackground": "#e66f39",
            "font": (FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
            "bd": 0,
            "relief": "flat",
            "padx": PADDING_MEDIUM,
            "pady": PADDING_MEDIUM,
        }

        tk.Button(scrollable.scrollable_frame, text="📦 Tiendas", command=self.main_window._show_stores, **btn_style).pack(fill="x", pady=(PADDING_LARGE, PADDING_SMALL))
        tk.Button(scrollable.scrollable_frame, text="👥 Empleados", command=self.main_window._show_staff, **btn_style).pack(fill="x", pady=PADDING_SMALL)
        tk.Button(scrollable.scrollable_frame, text="🛍️ Productos", command=self.main_window._show_products, **btn_style).pack(fill="x", pady=PADDING_SMALL)
        tk.Button(scrollable.scrollable_frame, text="💵 Ventas", command=self.main_window._show_sales, **btn_style).pack(fill="x", pady=PADDING_SMALL)
        tk.Button(scrollable.scrollable_frame, text="📊 Métricas", command=self.main_window._show_metrics, **btn_style).pack(fill="x", pady=PADDING_SMALL)
        tk.Button(scrollable.scrollable_frame, text="⚙️ Gestión Completa", command=self.main_window._show_full_management, **btn_style).pack(fill="x", pady=PADDING_SMALL)

    def update_login_ui(self):
        """Actualiza estado de login."""
        user = getattr(self.main_window.service, 'current_user', None)
        if user:
            self.main_window._login_btn.config(text='Logout', command=self.main_window._logout)
            self.main_window._view_session_btn.config(state='normal')
        else:
            self.main_window._login_btn.config(text='Login', command=self.main_window._dialog_login)
            self.main_window._view_session_btn.config(state='disabled')
