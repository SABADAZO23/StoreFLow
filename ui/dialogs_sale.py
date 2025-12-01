"""Diálogo para registrar ventas."""
import tkinter as tk
from tkinter import messagebox, ttk
from ui.config import BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL, FONT_SIZE_BUTTON
from ui.window_utils import center_window
import threading


class SaleDialog:
    """Diálogo para registrar una nueva venta."""

    def __init__(self, parent, service, store_id, on_success=None):
        """Inicializa el diálogo de venta.
        
        Args:
            parent: Ventana padre
            service: Servicio de tiendas
            store_id: ID de la tienda
            on_success: Callback cuando la venta se registra exitosamente
        """
        self.service = service
        self.store_id = store_id
        self.on_success = on_success
        self.products = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Registrar Venta")
        self.dialog.configure(bg=BG_COLOR)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        center_window(self.dialog, 500, 400, parent)
        
        self._build_ui()
        self._load_products()

    def _build_ui(self):
        """Construye la interfaz del diálogo."""
        # Título
        title = tk.Label(self.dialog, text="Nueva Venta", bg=BG_COLOR, fg=TEXT_COLOR,
                        font=(FONT_FAMILY, 16, "bold"))
        title.pack(pady=10)
        
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Selección de producto
        tk.Label(main_frame, text="Producto:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=5)
        
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(main_frame, textvariable=self.product_var,
                                         state="readonly", width=40)
        self.product_combo.pack(fill="x", pady=5)
        self.product_combo.bind("<<ComboboxSelected>>", self._on_product_selected)
        
        # Información del producto seleccionado
        self.product_info = tk.Label(main_frame, text="", bg=BG_COLOR, fg=TEXT_COLOR,
                                    font=(FONT_FAMILY, FONT_SIZE_LABEL - 2))
        self.product_info.pack(anchor="w", pady=5)
        
        # Cantidad
        tk.Label(main_frame, text="Cantidad:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=(10, 5))
        
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(main_frame, textvariable=self.quantity_var,
                                 font=(FONT_FAMILY, FONT_SIZE_LABEL), width=20)
        quantity_entry.pack(anchor="w", pady=5)
        
        # Precio unitario (se llena automáticamente pero se puede editar)
        tk.Label(main_frame, text="Precio unitario:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=(10, 5))
        
        self.price_var = tk.StringVar()
        price_entry = tk.Entry(main_frame, textvariable=self.price_var,
                              font=(FONT_FAMILY, FONT_SIZE_LABEL), width=20)
        price_entry.pack(anchor="w", pady=5)
        
        # Total
        self.total_label = tk.Label(main_frame, text="Total: $0.00", bg=BG_COLOR,
                                   fg=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold"))
        self.total_label.pack(anchor="w", pady=(10, 5))
        
        # Calcular total cuando cambian cantidad o precio
        quantity_entry.bind("<KeyRelease>", self._calculate_total)
        price_entry.bind("<KeyRelease>", self._calculate_total)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg=BG_COLOR)
        buttons_frame.pack(fill="x", pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", bg="#ccc", fg=TEXT_COLOR,
                 command=self.dialog.destroy,
                 font=(FONT_FAMILY, FONT_SIZE_BUTTON), padx=20, pady=5).pack(side="right", padx=5)
        
        tk.Button(buttons_frame, text="Registrar Venta", bg=ACCENT_COLOR, fg="white",
                 command=self._submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=5).pack(side="right", padx=5)

    def _load_products(self):
        """Carga los productos de la tienda."""
        try:
            res = self.service.get_store_products(self.store_id)
            if res.get('success'):
                self.products = res.get('products', [])
                product_names = [f"{p.get('name', 'Sin nombre')} (ID: {p.get('id')})" 
                                for p in self.products]
                self.product_combo['values'] = product_names
                if product_names:
                    self.product_combo.current(0)
                    self._on_product_selected()
        except Exception as e:
            messagebox.showerror('Error', f'Error al cargar productos: {str(e)}')

    def _on_product_selected(self, event=None):
        """Se ejecuta cuando se selecciona un producto."""
        selection = self.product_combo.current()
        if selection >= 0 and selection < len(self.products):
            product = self.products[selection]
            product_id = product.get('id')
            price = product.get('price', '0')
            stock = product.get('stock', 'N/A')
            
            self.price_var.set(str(price))
            self.product_info.config(
                text=f"Stock disponible: {stock} | Precio: ${price}"
            )
            self._calculate_total()

    def _calculate_total(self, event=None):
        """Calcula el total de la venta."""
        try:
            quantity = int(self.quantity_var.get() or "0")
            price = float(self.price_var.get() or "0")
            total = quantity * price
            self.total_label.config(text=f"Total: ${total:.2f}")
        except (ValueError, TypeError):
            self.total_label.config(text="Total: $0.00")

    def _submit(self):
        """Registra la venta."""
        try:
            selection = self.product_combo.current()
            if selection < 0:
                messagebox.showerror('Error', 'Selecciona un producto')
                return
            
            product = self.products[selection]
            product_id = product.get('id')
            
            quantity = int(self.quantity_var.get() or "0")
            if quantity <= 0:
                messagebox.showerror('Error', 'La cantidad debe ser mayor a 0')
                return
            
            price = float(self.price_var.get() or "0")
            if price < 0:
                messagebox.showerror('Error', 'El precio no puede ser negativo')
                return
            
            # Verificar stock
            stock = product.get('stock')
            if stock is not None:
                try:
                    stock_int = int(stock)
                    if stock_int < quantity:
                        messagebox.showerror('Error', 
                                           f'Stock insuficiente. Disponible: {stock_int}')
                        return
                except (ValueError, TypeError):
                    pass
            
            sale_data = {
                'product_id': product_id,
                'product_name': product.get('name', ''),
                'quantity': quantity,
                'unit_price': price
            }
            
            # Ejecutar grabado en background para no bloquear la UI
            def worker():
                try:
                    res = self.service.record_sale(self.store_id, sale_data)
                except Exception as e:
                    res = {"success": False, "error": str(e)}

                def on_done():
                    if res.get('success'):
                        messagebox.showinfo('Éxito', 'Venta registrada correctamente')
                        try:
                            self.dialog.destroy()
                        except Exception:
                            pass
                        if self.on_success:
                            try:
                                self.on_success()
                            except Exception:
                                pass
                    else:
                        messagebox.showerror('Error', res.get('error', 'Error desconocido'))

                # Volver al hilo principal
                self.dialog.after(0, on_done)

            # Deshabilitar botones mientras se procesa
            for child in self.dialog.winfo_children():
                try:
                    child.config(state='disabled')
                except Exception:
                    pass

            t = threading.Thread(target=worker, daemon=True)
            t.start()
        except ValueError:
            messagebox.showerror('Error', 'Ingresa números válidos')
        except Exception as e:
            messagebox.showerror('Error', f'Error: {str(e)}')

