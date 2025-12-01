"""Vistas de empleados."""
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL,
    PADDING_SMALL, PADDING_MEDIUM, FONT_SIZE_BUTTON, WHITE_COLOR
)
from ui.dialogs_employee import AddEmployeeDialog, UpdateEmployeeDialog
from ui.views_base import ViewBase
from ui.window_utils import center_window


class StaffView(ViewBase):
    """Vista de gestión de empleados."""

    def show_staff(self):
        """Muestra la vista de empleados."""
        self.clear_view()
        self.title_label.config(text="Empleados")

        store_id = self._get_active_store_id()
        if not store_id:
            tk.Label(self.view_frame, text="No hay tienda activa. Selecciona o crea una tienda primero.",
                    bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
            return

        try:
            res = self.service.get_store_staff(store_id)
        except Exception:
            res = []

        if isinstance(res, dict):
            if not res.get('success'):
                tk.Label(self.view_frame, text=f"Error: {res.get('error', '')}",
                        bg=BG_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="nw")
                return
            staff = res.get('staff', [])
        else:
            staff = list(res or [])

        header = tk.Frame(self.view_frame, bg=BG_COLOR)
        header.pack(fill="x")
        tk.Button(header, text="Agregar empleado", bg=ACCENT_COLOR, fg="white",
                 command=lambda: self._add_employee_dialog(store_id), font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 bd=0).pack(side="right")

        lb = tk.Listbox(self.view_frame, bg=WHITE_COLOR, fg=TEXT_COLOR,
                       font=(FONT_FAMILY, FONT_SIZE_LABEL), bd=0, highlightthickness=0)
        for e in staff:
            lb.insert('end', f"{e.get('name')} — {e.get('role')} (id:{e.get('id')})")
        lb.pack(fill='both', expand=True, pady=PADDING_MEDIUM)

        actions = tk.Frame(self.view_frame, bg=BG_COLOR)
        actions.pack(fill='x')
        tk.Button(actions, text='Actualizar seleccionado',
                 command=lambda: self._update_employee_dialog(store_id, lb, staff),
                 bg=WHITE_COLOR, fg=TEXT_COLOR).pack(side='left', padx=PADDING_SMALL)
        tk.Button(actions, text='Eliminar seleccionado',
                 command=lambda: self._delete_employee(store_id, lb, staff),
                 bg=WHITE_COLOR, fg=TEXT_COLOR).pack(side='left', padx=PADDING_SMALL)

    def _add_employee_dialog(self, store_id: str):
        """Abre diálogo para agregar empleado."""
        AddEmployeeDialog(self.main_window, self.service, store_id)

    def _update_employee_dialog(self, store_id: str, listbox: tk.Listbox, staff: List[Dict[str, Any]]):
        """Abre diálogo para actualizar empleado."""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning('Advertencia', 'Por favor seleccione un empleado de la lista')
            return

        employee = staff[selection[0]]
        staff_id = employee.get('id')

        dialog = tk.Toplevel(self.main_window)
        dialog.title("Actualizar Empleado")
        dialog.configure(bg=BG_COLOR)
        center_window(dialog, 400, 250, self.main_window)

        tk.Label(dialog, text="Nombre:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky="e", padx=10, pady=15)
        name_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        name_entry.insert(0, employee.get('name', ''))
        name_entry.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(dialog, text="Rol:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky="e", padx=10, pady=15)
        role_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        role_entry.insert(0, employee.get('role', ''))
        role_entry.grid(row=1, column=1, padx=10, pady=15)

        def submit():
            updates = {}
            if name_entry.get().strip() and name_entry.get().strip() != employee.get('name'):
                updates['name'] = name_entry.get().strip()
            if role_entry.get().strip() and role_entry.get().strip() != employee.get('role'):
                updates['role'] = role_entry.get().strip()

            if not updates:
                messagebox.showinfo('Info', 'No hay cambios para actualizar')
                dialog.destroy()
                return

            try:
                res = self.service.update_employee(store_id, staff_id, updates)
            except Exception:
                res = {'success': False, 'error': 'Error interno'}

            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Empleado actualizado')
                dialog.destroy()
                self.show_staff()
            else:
                messagebox.showerror('Error', f"No se pudo actualizar: {res.get('error', '')}")

        tk.Button(dialog, text="Actualizar", bg=ACCENT_COLOR, fg="white",
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=2, column=0, columnspan=2, pady=20)

    def _delete_employee(self, store_id: str, listbox: tk.Listbox, staff: List[Dict[str, Any]]):
        """Elimina un empleado seleccionado."""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning('Advertencia', 'Por favor seleccione un empleado de la lista')
            return

        if not messagebox.askyesno('Confirmar', '¿Está seguro de que desea eliminar este empleado?'):
            return

        try:
            staff_id = staff[selection[0]].get('id')
            res = self.service.remove_employee(store_id, staff_id)
            if isinstance(res, dict) and res.get('success'):
                messagebox.showinfo('OK', 'Empleado eliminado')
                self.show_staff()
            else:
                messagebox.showerror('Error', f"No se pudo eliminar: {res.get('error', '')}")
        except Exception as e:
            messagebox.showerror('Error', f'Error al eliminar empleado: {str(e)}')
