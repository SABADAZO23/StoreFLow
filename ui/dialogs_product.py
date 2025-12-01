"""Diálogos para gestión de productos."""
import tkinter as tk
from tkinter import messagebox

from ui.config import BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL, FONT_SIZE_BUTTON
from ui.dialogs_auth import DialogBase


class CreateProductDialog(DialogBase):
    """Crea producto."""
    def __init__(self, parent, service, store_id):
        super().__init__(parent, "Crear Producto", 400, 200)
        self.service = service
        self.store_id = store_id
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Precio:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        price = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        price.grid(row=1, column=1, padx=10, pady=15)

        def submit():
            product = {'name': name.get().strip(), 'price': price.get().strip()}
            try:
                res = self.service.create_product(self.store_id, product)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Producto creado')
                self.dialog.destroy()
                self.parent.view_manager.show_products()
            else:
                messagebox.showerror('Error', f"Error: {res.get('error', '')}")

        tk.Button(self.dialog, text="Crear", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=2, column=0, columnspan=2, pady=20)


class UpdateProductDialog(DialogBase):
    """Actualiza producto."""
    def __init__(self, parent, service, store_id, product):
        super().__init__(parent, "Actualizar Producto", 400, 300)
        self.service = service
        self.store_id = store_id
        self.product = product
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name.insert(0, self.product.get('name', ''))
        name.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Precio:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        price = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        price.insert(0, str(self.product.get('price', '')))
        price.grid(row=1, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Stock:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=2, column=0, sticky="e", padx=10, pady=15)
        stock = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        stock.insert(0, str(self.product.get('stock', '')))
        stock.grid(row=2, column=1, padx=10, pady=15)

        def submit():
            updates = {}
            if name.get().strip() and name.get().strip() != self.product.get('name'):
                updates['name'] = name.get().strip()
            if price.get().strip():
                try:
                    if float(price.get().strip()) != float(self.product.get('price', 0)):
                        updates['price'] = price.get().strip()
                except ValueError:
                    messagebox.showerror('Error', 'Precio inválido')
                    return
            if stock.get().strip():
                try:
                    if int(stock.get().strip()) != int(self.product.get('stock', 0)):
                        updates['stock'] = stock.get().strip()
                except ValueError:
                    messagebox.showerror('Error', 'Stock inválido')
                    return
            if not updates:
                messagebox.showinfo('Info', 'No hay cambios')
                self.dialog.destroy()
                return
            try:
                res = self.service.update_product(self.store_id, self.product.get('id'), updates)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Producto actualizado')
                self.dialog.destroy()
                self.parent.view_manager.show_products()
            else:
                messagebox.showerror('Error', f"Error: {res.get('error', '')}")

        tk.Button(self.dialog, text="Actualizar", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=3, column=0, columnspan=2, pady=20)
