"""Vistas de ventas."""
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List, Dict, Any
from datetime import datetime
import threading

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL,
    PADDING_SMALL, PADDING_MEDIUM, FONT_SIZE_BUTTON, WHITE_COLOR, FONT_SIZE_SMALL
)
from ui.views_base import ViewBase
from ui.dialogs_sale import SaleDialog


class SalesView(ViewBase):
    """Vista de gestión de ventas."""

    def show_sales(self):
        """Muestra la vista de ventas."""
        self.clear_view()
        self.title_label.config(text="Ventas")

        store_id = self._get_active_store_id()
        if not store_id:
            tk.Label(self.view_frame, text="No hay tienda activa.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
            return
        # Preparar interfaz (header + lista vacía) y cargar ventas en background
        header = tk.Frame(self.view_frame, bg=BG_COLOR)
        header.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        tk.Button(header, text="➕ Registrar venta", bg=ACCENT_COLOR, fg="white",
                 command=lambda: self._register_sale(store_id), 
                 font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"), bd=0,
                 padx=15, pady=8).pack(side="left")

        # Frame para lista de ventas
        list_frame = tk.Frame(self.view_frame, bg=BG_COLOR)
        list_frame.pack(fill='both', expand=True, padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # Listbox con scrollbar
        self._sales_listbox = tk.Listbox(list_frame, bg=WHITE_COLOR, fg=TEXT_COLOR,
                                         font=(FONT_FAMILY, FONT_SIZE_SMALL), bd=1, 
                                         yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        scrollbar.config(command=self._sales_listbox.yview)
        self._sales_listbox.insert('end', 'Cargando ventas...')
        self._sales_listbox.pack(fill='both', expand=True)

        # Acciones (se actualizarán cuando lleguen las ventas)
        self._sales_actions_frame = tk.Frame(self.view_frame, bg=BG_COLOR)
        self._sales_actions_frame.pack(fill='x', padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        # Cargar ventas en background
        def worker():
            try:
                res = self.service.get_store_sales(store_id, limit=100)
            except Exception as e:
                res = {"success": False, "error": str(e)}

            def on_complete():
                self._populate_sales_ui(res)

            self.view_frame.after(0, on_complete)

        threading.Thread(target=worker, daemon=True).start()

    def _populate_sales_ui(self, res):
        """Actualiza la UI con los resultados de ventas (se ejecuta en hilo principal)."""
        self._sales_listbox.delete(0, 'end')
        if not res.get('success'):
            error_msg = res.get('error', 'Error desconocido')
            self._sales_listbox.insert('end', f"Error al cargar ventas: {error_msg}")
            self._sales_listbox.config(state=tk.DISABLED)
            return

        sales = res.get('sales', [])
        if not sales:
            self._sales_listbox.insert('end', "No hay ventas registradas")
            self._sales_listbox.config(state=tk.DISABLED)
        else:
            for sale in sales:
                total = sale.get('total', 0)
                quantity = sale.get('quantity', 0)
                product_id = sale.get('product_id', 'N/A')
                timestamp = sale.get('timestamp')

                # Formatear fecha si está disponible
                date_str = ""
                if timestamp:
                    try:
                        if hasattr(timestamp, 'strftime'):
                            date_str = timestamp.strftime('%Y-%m-%d %H:%M')
                        else:
                            date_str = str(timestamp)[:16]
                    except:
                        date_str = ""

                display_text = f"${total:.2f} | {quantity} unidades | Producto: {product_id}"
                if date_str:
                    display_text += f" | {date_str}"

                self._sales_listbox.insert('end', display_text)

            # Añadir botón eliminar
            for child in self._sales_actions_frame.winfo_children():
                child.destroy()

            tk.Button(self._sales_actions_frame, text='🗑️ Eliminar seleccionada',
                     command=lambda: self._delete_sale(self._sales_listbox, sales),
                     bg="#dc3545", fg="white",
                     font=(FONT_FAMILY, FONT_SIZE_BUTTON),
                     padx=15, pady=5).pack(side='left', padx=PADDING_SMALL)

    def _register_sale(self, store_id):
        """Abre diálogo para registrar venta."""
        SaleDialog(self.main_window, self.service, store_id, on_success=self.show_sales)

    def _delete_sale(self, listbox, sales):
        """Elimina una venta."""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning('Advertencia', 'Selecciona una venta')
            return

        if messagebox.askyesno('Confirmar', '¿Eliminar esta venta?'):
            try:
                sale_id = sales[selection[0]].get('id')
                res = self.service.delete_sale(sale_id)
                if res.get('success'):
                    messagebox.showinfo('OK', 'Venta eliminada')
                    self.show_sales()
            except Exception as e:
                messagebox.showerror('Error', str(e))
