"""Diálogos para gestión de tiendas."""
import tkinter as tk
from tkinter import messagebox

from ui.config import BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL, FONT_SIZE_BUTTON
from ui.dialogs_auth import DialogBase


class CreateStoreDialog(DialogBase):
    """Crea una tienda."""
    def __init__(self, parent, service):
        super().__init__(parent, "Crear Tienda", 400, 250)
        self.service = service
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Dirección:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        address = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        address.grid(row=1, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Teléfono:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=2, column=0, sticky="e", padx=10, pady=15)
        phone = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        phone.grid(row=2, column=1, padx=10, pady=15)

        def submit():
            info = {'name': name.get().strip(), 'address': address.get().strip(), 'phone': phone.get().strip()}
            try:
                res = self.service.create_store(info)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', f"Tienda creada: {res.get('store_id')}")
                self.dialog.destroy()
                self.parent.view_manager.show_stores()
            else:
                messagebox.showerror('Error', f"Error: {res.get('error', '')}")

        tk.Button(self.dialog, text="Crear", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=3, column=0, columnspan=2, pady=20)


class SelectStoreDialog(DialogBase):
    """Selecciona tienda activa."""
    def __init__(self, parent, service, stores):
        super().__init__(parent, "Seleccionar Tienda Activa", 400, 300)
        self.service = service
        self.stores = stores
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text="Seleccione una tienda:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, 14, "bold")).pack(pady=20)

        listbox = tk.Listbox(self.dialog, bg="white", fg=TEXT_COLOR,
                            font=(FONT_FAMILY, FONT_SIZE_LABEL), bd=0, highlightthickness=1)
        listbox.pack(fill="both", expand=True, padx=20, pady=15)

        for store in self.stores:
            listbox.insert("end", f"{store.get('name')} (ID: {store.get('id')})")

        def select_store():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning('Advertencia', 'Seleccione una tienda')
                return
            store = self.stores[selection[0]]
            try:
                if hasattr(self.service, 'set_current_store'):
                    self.service.set_current_store(store.get('id'))
                messagebox.showinfo('Éxito', f"Tienda activa: {store.get('name')}")
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror('Error', f'Error: {str(e)}')

        tk.Button(self.dialog, text="Seleccionar", bg=ACCENT_COLOR, fg="white",
                 command=select_store, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).pack(pady=20)
