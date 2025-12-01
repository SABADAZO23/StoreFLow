"""Vistas de tiendas."""
import tkinter as tk
from tkinter import messagebox

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL,
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE, FONT_SIZE_BUTTON,
    FONT_SIZE_SMALL, WHITE_COLOR
)
from ui.dialogs_store import CreateStoreDialog, SelectStoreDialog
from ui.views_base import ViewBase


class StoreView(ViewBase):
    """Vista de gestión de tiendas."""

    def show_stores(self):
        """Muestra la vista de tiendas."""
        self.clear_view()
        self.title_label.config(text="Tiendas")

        stores = self._get_stores()

        if not stores:
            tk.Label(self.view_frame, text="No hay tiendas disponibles.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
            tk.Button(self.view_frame, text="Crear tienda", bg=ACCENT_COLOR, fg="white",
                     command=self._create_store_dialog, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                     bd=0).pack(pady=PADDING_LARGE)
            return

        frame = tk.Frame(self.view_frame, bg=BG_COLOR)
        frame.pack(fill="both", expand=True)

        listbox = tk.Listbox(frame, bg=WHITE_COLOR, fg=TEXT_COLOR,
                            font=(FONT_FAMILY, FONT_SIZE_LABEL), bd=0, highlightthickness=0)
        for s in stores:
            listbox.insert("end", f"{s.get('name')} (id: {s.get('id')})")
        listbox.pack(side="left", fill="both", expand=True, padx=(0, PADDING_MEDIUM), pady=PADDING_SMALL)

        def on_store_dbl(event):
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            store = stores[idx]
            try:
                if hasattr(self.service, 'set_current_store'):
                    self.service.set_current_store(store.get('id'))
                messagebox.showinfo('Tienda', f"Tienda {store.get('name')} seleccionada como activa")
                self.show_stores()
            except Exception:
                messagebox.showerror('Error', 'No se pudo seleccionar la tienda')

        listbox.bind('<Double-1>', on_store_dbl)

        detail = tk.Frame(frame, bg=BG_COLOR)
        detail.pack(side="right", fill="y")

        tk.Label(detail, text="Acciones", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="n", pady=(0, PADDING_MEDIUM))
        
        tk.Button(detail, text="➕ Crear tienda", bg=ACCENT_COLOR, fg="white",
                 command=self._create_store_dialog, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 bd=0).pack(fill="x", pady=PADDING_SMALL)
        
        tk.Button(detail, text="✓ Seleccionar tienda activa", bg=ACCENT_COLOR, fg="white",
                 command=self._select_active_store_dialog, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 bd=0).pack(fill="x", pady=PADDING_SMALL)

        current_store_id = getattr(self.service, 'current_store', None)
        if current_store_id:
            current_store = next((s for s in stores if s.get('id') == current_store_id), None)
            if current_store:
                tk.Label(detail, text=f"Activa: {current_store.get('name')}", bg=BG_COLOR,
                        fg=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold")).pack(pady=PADDING_SMALL)

        tk.Button(detail, text="📋 Ver mis tiendas", bg=WHITE_COLOR, fg=TEXT_COLOR,
                 command=self.show_my_stores, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(fill="x", pady=PADDING_SMALL)

    def show_my_stores(self):
        """Muestra todas las tiendas del usuario con detalles."""
        self.clear_view()
        self.title_label.config(text="Mis Tiendas")

        stores = self._get_stores()

        if not stores:
            tk.Label(self.view_frame, text="No tienes tiendas registradas.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
            return

        frame = tk.Frame(self.view_frame, bg=BG_COLOR)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame, bg=BG_COLOR)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        scrollable_frame.bind("<Configure>",
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for store in stores:
            store_frame = tk.Frame(scrollable_frame, bg=WHITE_COLOR, relief="raised", bd=1)
            store_frame.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

            tk.Label(store_frame, text=f"Nombre: {store.get('name', 'N/A')}", bg=WHITE_COLOR,
                    fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            tk.Label(store_frame, text=f"ID: {store.get('id', 'N/A')}", bg=WHITE_COLOR,
                    fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            tk.Label(store_frame, text=f"Dirección: {store.get('address', 'N/A')}", bg=WHITE_COLOR,
                    fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            tk.Label(store_frame, text=f"Teléfono: {store.get('phone', 'N/A')}", bg=WHITE_COLOR,
                    fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

            tk.Button(store_frame, text="Seleccionar como activa", bg=ACCENT_COLOR, fg="white",
                     command=lambda s=store: self._select_store(s), font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(pady=PADDING_SMALL)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_store_dialog(self):
        """Abre diálogo para crear tienda."""
        CreateStoreDialog(self.main_window, self.service)

    def _select_active_store_dialog(self):
        """Abre diálogo para seleccionar tienda activa."""
        stores = self._get_stores()
        if not stores:
            messagebox.showinfo('Info', 'No tienes tiendas registradas. Crea una tienda primero.')
            return
        SelectStoreDialog(self.main_window, self.service, stores)

    def _select_store(self, store):
        """Selecciona una tienda."""
        try:
            if hasattr(self.service, 'set_current_store'):
                self.service.set_current_store(store.get('id'))
        except Exception:
            pass
        messagebox.showinfo("Tienda seleccionada", f"Tienda {store.get('name')} seleccionada")
