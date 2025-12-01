"""Vistas de métricas."""
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any
import threading

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL,
    PADDING_SMALL, PADDING_MEDIUM, FONT_SIZE_BUTTON, FONT_SIZE_SMALL,
    WHITE_COLOR
)
from ui.views_base import ViewBase


class MetricsView(ViewBase):

    def show_metrics(self):
        self.clear_view()
        self.title_label.config(text="Métricas")

        store_id = self._get_active_store_id()
        if not store_id:
            tk.Label(self.view_frame, text="No hay tienda activa. Selecciona o crea una tienda primero.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
            return

        frame = tk.Frame(self.view_frame, bg=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        loading_label = tk.Label(frame, text="Cargando métricas...", bg=BG_COLOR, fg=TEXT_COLOR,
                                 font=(FONT_FAMILY, FONT_SIZE_LABEL))
        loading_label.pack(anchor='nw', pady=PADDING_SMALL)

        def worker():
            try:
                sales_res = self.service.get_store_sales(store_id, limit=1000)
                if not sales_res.get('success'):
                    sales = []
                else:
                    sales = sales_res.get('sales', [])
                
                # Enriquecer ventas con nombres de productos si no están disponibles
                if sales:
                    try:
                        products_res = self.service.get_store_products(store_id)
                        if products_res.get('success'):
                            products = products_res.get('products', [])
                            # Crear mapa de producto_id -> nombre
                            product_map = {p.get('id'): p.get('name', 'N/A') for p in products}
                            # Enriquecer ventas
                            for sale in sales:
                                if not sale.get('product_name') or sale.get('product_name') == '':
                                    pid = sale.get('product_id')
                                    sale['product_name'] = product_map.get(pid, 'N/A')
                    except Exception:
                        pass
            except Exception:
                sales = []

            if not sales:
                result = {"demo": True}
            else:
                revenue_res = self.service.calculate_revenue(sales)
                sales_count_res = self.service.calculate_sales_count(sales)
                top_res = self.service.get_top_products(sales, limit=5)

                result = {
                    "demo": False,
                    "revenue": revenue_res.get('revenue', 0) if revenue_res.get('success') else 0,
                    "count": sales_count_res.get('count', 0) if sales_count_res.get('success') else 0,
                    "average": sales_count_res.get('average', 0) if sales_count_res.get('success') else 0,
                    "top_products": top_res.get('top_products', []) if top_res.get('success') else []
                }

            def on_done():
                for child in frame.winfo_children():
                    child.destroy()

                if result.get('demo'):
                    self._show_demo_metrics(frame)
                else:
                    revenue = result.get('revenue', 0)
                    count = result.get('count', 0)
                    avg = result.get('average', 0)
                    top_products = result.get('top_products', [])

                    metrics_frame = tk.Frame(frame, bg=WHITE_COLOR, relief="raised", bd=1)
                    metrics_frame.pack(fill="x", pady=PADDING_SMALL)

                    tk.Label(metrics_frame, text="MÉTRICAS GENERALES", bg=WHITE_COLOR, fg=TEXT_COLOR,
                            font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

                    tk.Label(metrics_frame, text=f"Ingresos totales: ${revenue:.2f}", bg=WHITE_COLOR,
                            fg=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM)

                    tk.Label(metrics_frame, text=f"Total de ventas: {count}", bg=WHITE_COLOR,
                            fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", padx=PADDING_MEDIUM)

                    tk.Label(metrics_frame, text=f"Promedio por venta: ${avg:.2f}", bg=WHITE_COLOR,
                            fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))

                    if top_products:
                        top_frame = tk.Frame(frame, bg=WHITE_COLOR, relief="raised", bd=1)
                        top_frame.pack(fill="x", pady=PADDING_SMALL)

                        tk.Label(top_frame, text="PRODUCTOS MÁS VENDIDOS", bg=WHITE_COLOR, fg=TEXT_COLOR,
                                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

                        for product in top_products:
                            pid = product.get('product_id', 'N/A')
                            pname = product.get('product_name', 'N/A')
                            qty = product.get('quantity', 0)
                            rev = product.get('revenue', 0)
                            tk.Label(top_frame, text=f"  • {pname} ({pid}): {qty} unidades (${rev:.2f})", bg=WHITE_COLOR,
                                    fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="w", padx=PADDING_MEDIUM)

            self.view_frame.after(0, on_done)

        threading.Thread(target=worker, daemon=True).start()

    def _show_demo_metrics(self, parent):
        demo_data = {
            'revenue': 2500.00,
            'count': 15,
            'average': 166.67,
            'top_products': [
                {'product_id': 'PROD001', 'product_name': 'Camiseta Azul', 'quantity': 5, 'revenue': 750.00},
                {'product_id': 'PROD002', 'product_name': 'Pantalón Negro', 'quantity': 4, 'revenue': 600.00},
                {'product_id': 'PROD003', 'product_name': 'Zapatillas', 'quantity': 3, 'revenue': 450.00},
            ]
        }

        # Header
        header = tk.Frame(parent, bg=ACCENT_COLOR)
        header.pack(fill="x", pady=(0, PADDING_MEDIUM))
        
        tk.Label(header, text="📊 DEMOSTRACIÓN DE MÉTRICAS", bg=ACCENT_COLOR, fg="white",
                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        # Mensaje info
        tk.Label(parent, text="⚠️ Sin datos de ventas aún. Aquí hay un ejemplo de cómo se verán las métricas:",
                bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL, "italic")).pack(anchor="w", pady=(0, PADDING_MEDIUM))

        # Métricas generales
        metrics_frame = tk.Frame(parent, bg=WHITE_COLOR, relief="raised", bd=1)
        metrics_frame.pack(fill="x", pady=PADDING_SMALL)

        tk.Label(metrics_frame, text="MÉTRICAS GENERALES", bg=WHITE_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        tk.Label(metrics_frame, text=f"Ingresos totales: ${demo_data['revenue']:.2f}", bg=WHITE_COLOR,
                fg=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM)

        tk.Label(metrics_frame, text=f"Total de ventas: {demo_data['count']}", bg=WHITE_COLOR,
                fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", padx=PADDING_MEDIUM)

        tk.Label(metrics_frame, text=f"Promedio por venta: ${demo_data['average']:.2f}", bg=WHITE_COLOR,
                fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))

        # Top productos
        top_frame = tk.Frame(parent, bg=WHITE_COLOR, relief="raised", bd=1)
        top_frame.pack(fill="x", pady=PADDING_SMALL)

        tk.Label(top_frame, text="PRODUCTOS MÁS VENDIDOS", bg=WHITE_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        for product in demo_data['top_products']:
            pid = product.get('product_id', 'product_name ')
            pname = product.get('product_name', 'Producto Demo')
            qty = product.get('quantity', 0)
            rev = product.get('revenue', 0)
            tk.Label(top_frame, text=f"  • {pname} ({pid}): {qty} unidades (${rev:.2f})", bg=WHITE_COLOR,
                    fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="w", padx=PADDING_MEDIUM)

        # Instrucciones
        instr_frame = tk.Frame(parent, bg=ACCENT_COLOR, relief="raised", bd=1)
        instr_frame.pack(fill="x", pady=PADDING_MEDIUM)

        tk.Label(instr_frame, text="✏️ Pasos para ver tus métricas reales:", bg=ACCENT_COLOR, fg="white",
                font=(FONT_FAMILY, FONT_SIZE_LABEL, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=(PADDING_SMALL, PADDING_SMALL))

        steps = [
            "1. Ve a '💵 Ventas' desde el menú",
            "2. Haz clic en 'Registrar venta'",
            "3. Ingresa cantidad, precio y ID del producto",
            "4. Vuelve a '📊 Métricas' para ver tus datos"
        ]

        for step in steps:
            tk.Label(instr_frame, text=step, bg=ACCENT_COLOR, fg="white",
                    font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="w", padx=PADDING_MEDIUM)
