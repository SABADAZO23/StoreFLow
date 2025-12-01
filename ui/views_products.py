"""Vistas de productos."""
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL,
    PADDING_SMALL, PADDING_MEDIUM, FONT_SIZE_BUTTON, WHITE_COLOR
)
from ui.dialogs_product import CreateProductDialog, UpdateProductDialog
from ui.views_base import ViewBase
from ui.window_utils import center_window


class ProductView(ViewBase):
    """Vista de gestión de productos."""

    def show_products(self):
        """Muestra la vista de productos."""
        self.clear_view()
        self.title_label.config(text="Productos")

        store_id = self._get_active_store_id()
        if not store_id:
            tk.Label(self.view_frame, text="No hay tienda activa. Selecciona o crea una tienda primero.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
            return

        try:
            res = self.service.get_store_products(store_id)
        except Exception:
            res = []

        if isinstance(res, dict):
            if not res.get('success'):
                tk.Label(self.view_frame, text=f"Error: {res.get('error', '')}",
                        bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
                return
            products = res.get('products', [])
        else:
            products = list(res or [])

        header = tk.Frame(self.view_frame, bg=BG_COLOR)
        header.pack(fill="x")
        tk.Button(header, text="Crear producto", bg=ACCENT_COLOR, fg="white",
                 command=lambda: self._create_product_dialog(store_id), font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 bd=0).pack(side="right")

        lb = tk.Listbox(self.view_frame, bg=WHITE_COLOR, fg=TEXT_COLOR,
                       font=(FONT_FAMILY, FONT_SIZE_LABEL), bd=0, highlightthickness=0)
        for p in products:
            lb.insert('end', f"{p.get('name')} — ${p.get('price')} (id:{p.get('id')})")
        lb.pack(fill='both', expand=True, pady=PADDING_MEDIUM)

        actions = tk.Frame(self.view_frame, bg=BG_COLOR)
        actions.pack(fill='x')
        tk.Button(actions, text='Actualizar seleccionado',
                 command=lambda: self._update_product_dialog(store_id, lb, products),
                 bg=WHITE_COLOR, fg=TEXT_COLOR).pack(side='left', padx=PADDING_SMALL)
        tk.Button(actions, text='Eliminar seleccionado',
                 command=lambda: self._delete_product(store_id, lb, products),
                 bg=WHITE_COLOR, fg=TEXT_COLOR).pack(side='left', padx=PADDING_SMALL)

    def _create_product_dialog(self, store_id: str):
        """Abre diálogo para crear producto."""
        CreateProductDialog(self.main_window, self.service, store_id)

    def _update_product_dialog(self, store_id: str, listbox: tk.Listbox, products: List[Dict[str, Any]]):
        """Abre diálogo para actualizar producto."""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning('Advertencia', 'Por favor seleccione un producto de la lista')
            return

        product = products[selection[0]]
        product_id = product.get('id')

        dialog = tk.Toplevel(self.main_window)
        dialog.title("Actualizar Producto")
        dialog.configure(bg=BG_COLOR)
        center_window(dialog, 400, 300, self.main_window)

        tk.Label(dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name_entry.insert(0, product.get('name', ''))
        name_entry.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(dialog, text="Precio:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        price_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        price_entry.insert(0, str(product.get('price', '')))
        price_entry.grid(row=1, column=1, padx=10, pady=15)

        tk.Label(dialog, text="Stock:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=2, column=0, sticky="e", padx=10, pady=15)
        stock_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        stock_entry.insert(0, str(product.get('stock', '')))
        stock_entry.grid(row=2, column=1, padx=10, pady=15)

        def submit():
            updates = {}
            if name_entry.get().strip() and name_entry.get().strip() != product.get('name'):
                updates['name'] = name_entry.get().strip()
            
            price_val = price_entry.get().strip()
            if price_val:
                try:
                    if float(price_val) != float(product.get('price', 0)):
                        updates['price'] = price_val
                except ValueError:
                    messagebox.showerror('Error', 'El precio debe ser un número válido')
                    return
            
            stock_val = stock_entry.get().strip()
            if stock_val:
                try:
                    if int(stock_val) != int(product.get('stock', 0)):
                        updates['stock'] = stock_val
                except ValueError:
                    messagebox.showerror('Error', 'El stock debe ser un número entero válido')
                    return

            if not updates:
                messagebox.showinfo('Info', 'No hay cambios para actualizar')
                dialog.destroy()
                return

            try:
                res = self.service.update_product(store_id, product_id, updates)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}

            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Producto actualizado')
                dialog.destroy()
                self.show_products()
            else:
                messagebox.showerror('Error', f"No se pudo actualizar: {res.get('error', '')}")

        tk.Button(dialog, text="Actualizar", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=3, column=0, columnspan=2, pady=20)

    def _delete_product(self, store_id: str, listbox: tk.Listbox, products: List[Dict[str, Any]]):
        """Elimina un producto seleccionado."""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning('Advertencia', 'Por favor seleccione un producto de la lista')
            return

        if not messagebox.askyesno('Confirmar', '¿Está seguro de que desea eliminar este producto?'):
            return

        try:
            product_id = products[selection[0]].get('id')
            res = self.service.delete_product(store_id, product_id)
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Producto eliminado')
                self.show_products()
            else:
                messagebox.showerror('Error', f"No se pudo eliminar: {res.get('error', '')}")
        except Exception as e:
            messagebox.showerror('Error', f'Error al eliminar producto: {str(e)}')
