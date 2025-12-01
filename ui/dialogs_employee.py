"""Diálogos para gestión de empleados."""
import tkinter as tk
from tkinter import messagebox

from ui.config import BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL, FONT_SIZE_BUTTON
from ui.dialogs_auth import DialogBase


class AddEmployeeDialog(DialogBase):
    """Agrega empleado."""
    def __init__(self, parent, service, store_id):
        super().__init__(parent, "Agregar Empleado", 400, 200)
        self.service = service
        self.store_id = store_id
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Rol:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        role = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        role.grid(row=1, column=1, padx=10, pady=15)

        def submit():
            staff = {'name': name.get().strip(), 'role': role.get().strip()}
            try:
                res = self.service.add_store_staff(self.store_id, staff)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Empleado agregado')
                self.dialog.destroy()
                self.parent.view_manager.show_staff()
            else:
                messagebox.showerror('Error', f"Error: {res.get('error', '')}")

        tk.Button(self.dialog, text="Agregar", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=2, column=0, columnspan=2, pady=20)


class UpdateEmployeeDialog(DialogBase):
    """Actualiza empleado."""
    def __init__(self, parent, service, store_id, employee):
        super().__init__(parent, "Actualizar Empleado", 400, 200)
        self.service = service
        self.store_id = store_id
        self.employee = employee
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name.insert(0, self.employee.get('name', ''))
        name.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text="Rol:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        role = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        role.insert(0, self.employee.get('role', ''))
        role.grid(row=1, column=1, padx=10, pady=15)

        def submit():
            updates = {}
            if name.get().strip() and name.get().strip() != self.employee.get('name'):
                updates['name'] = name.get().strip()
            if role.get().strip() and role.get().strip() != self.employee.get('role'):
                updates['role'] = role.get().strip()
            if not updates:
                messagebox.showinfo('Info', 'No hay cambios')
                self.dialog.destroy()
                return
            try:
                res = self.service.update_employee(self.store_id, self.employee.get('id'), updates)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Empleado actualizado')
                self.dialog.destroy()
                self.parent.view_manager.show_staff()
            else:
                messagebox.showerror('Error', f"Error: {res.get('error', '')}")

        tk.Button(self.dialog, text="Actualizar", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=2, column=0, columnspan=2, pady=20)
