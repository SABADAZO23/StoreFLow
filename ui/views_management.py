"""Vista de gestión completa."""
import tkinter as tk
from typing import List

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_SMALL,
    FONT_SIZE_SECTION, PADDING_SMALL, PADDING_MEDIUM, WHITE_COLOR
)
from ui.views_base import ViewBase


class ManagementView(ViewBase):
    """Vista de gestión completa de tiendas."""

    def show_full_management(self):
        """Muestra la vista de gestión completa con todas las opciones."""
        self.clear_view()
        self.title_label.config(text="Gestión Completa de Tiendas")

        user = getattr(self.service, 'current_user', None)
        if not user:
            tk.Label(self.view_frame, text="⚠️ Debe iniciar sesión primero para acceder a la gestión de tiendas.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)).pack(anchor="nw", pady=PADDING_MEDIUM)
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

        from ui.views_stores import StoreView
        store_view = StoreView(self.main_window)

        from ui.views_staff import StaffView
        staff_view = StaffView(self.main_window)

        from ui.views_products import ProductView
        product_view = ProductView(self.main_window)

        self._add_management_section(scrollable_frame, "📦 Gestión de Tiendas", [
            ("1. Registrar nueva tienda", store_view._create_store_dialog),
            ("2. Seleccionar tienda activa", store_view._select_active_store_dialog),
            ("3. Ver mis tiendas", store_view.show_my_stores),
        ])

        self._add_management_section(scrollable_frame, "👥 Gestión de Empleados", [
            ("4. Agregar empleado a tienda", lambda: self._add_employee_wrapper(staff_view)),
            ("5. Listar empleados", staff_view.show_staff),
            ("6. Actualizar empleado", lambda: staff_view.show_staff()),
            ("7. Eliminar empleado", lambda: staff_view.show_staff()),
        ])

        self._add_management_section(scrollable_frame, "🛍️ Gestión de Productos", [
            ("8. Listar productos", product_view.show_products),
            ("9. Crear producto", lambda: self._create_product_wrapper(product_view)),
            ("10. Actualizar producto", lambda: product_view.show_products()),
            ("11. Eliminar producto", lambda: product_view.show_products()),
        ])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _add_management_section(self, parent, title: str, buttons: List[tuple]):
        """Añade una sección de gestión con botones.
        
        Args:
            parent: Widget padre
            title: Título de la sección
            buttons: Lista de tuplas (texto, comando)
        """
        section_frame = tk.Frame(parent, bg=WHITE_COLOR, relief="raised", bd=1)
        section_frame.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        tk.Label(section_frame, text=title, bg=WHITE_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_SECTION, "bold")).pack(anchor="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        btn_frame = tk.Frame(section_frame, bg=WHITE_COLOR)
        btn_frame.pack(fill="x", padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        for text, command in buttons:
            tk.Button(btn_frame, text=text, bg=ACCENT_COLOR, fg="white",
                     command=command, font=(FONT_FAMILY, FONT_SIZE_SMALL),
                     bd=0).pack(fill="x", pady=PADDING_SMALL)

    def _add_employee_wrapper(self, staff_view):
        """Wrapper para agregar empleado desde gestión completa."""
        store_id = self._get_active_store_id()
        if store_id:
            staff_view._add_employee_dialog(store_id)

    def _create_product_wrapper(self, product_view):
        """Wrapper para crear producto desde gestión completa."""
        store_id = self._get_active_store_id()
        if store_id:
            product_view._create_product_dialog(store_id)
