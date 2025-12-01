"""Diálogos de autenticación (login y registro)."""
import tkinter as tk
from tkinter import messagebox

from ui.config import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL, FONT_SIZE_BUTTON
)
from ui.window_utils import center_window


class DialogBase:
    """Base para diálogos."""
    def __init__(self, parent, title: str, width: int = 400, height: int = 250):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=BG_COLOR)
        new_width = int(width * 2.5)
        new_height = int(height * 2.5)
        center_window(self.dialog, new_width, new_height, parent)


class LoginDialog(DialogBase):
    """Diálogo de login."""
    def __init__(self, parent, auth):
        super().__init__(parent, 'Login', 200, 200)
        self.auth = auth
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text='Email:', bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky='e', padx=10, pady=15)
        email = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        email.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text='Contraseña:', bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky='e', padx=10, pady=15)
        pwd = tk.Entry(self.dialog, show='*', font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        pwd.grid(row=1, column=1, padx=10, pady=15)

        def submit():
            e, p = email.get().strip(), pwd.get().strip()
            if not e or not p:
                messagebox.showerror('Error', 'Complete todos los campos')
                return
            try:
                res = self.auth.login(e, p)
            except Exception as exc:
                messagebox.showerror('Error', f'Error: {str(exc)}')
                return

            if isinstance(res, dict) and res.get('success'):
                self.parent._session_id = res.get('session_id')
                try:
                    self.parent.service.set_current_user(res.get('user_id'))
                except Exception:
                    pass
                nombre = res.get('datos_usuario', {}).get('nombre') if isinstance(res.get('datos_usuario'), dict) else None
                self.parent.current_user_var.set(nombre or res.get('user_id'))
                self.parent.session_var.set(f"Sesión: {self.parent._session_id[:8]}..." if self.parent._session_id else "")
                messagebox.showinfo('OK', f"Bienvenido {nombre or res.get('user_id')}")
                self.dialog.destroy()
                self.parent._update_login_ui()
                self.parent.view_manager.show_stores()
            else:
                error_msg = res.get('error', 'Credenciales inválidas') if isinstance(res, dict) else 'Error desconocido'
                messagebox.showerror('Error', f"Login fallido: {error_msg}")

        tk.Button(self.dialog, text='Entrar', bg=ACCENT_COLOR, fg='white',
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=2, column=0, columnspan=2, pady=20)


class RegisterDialog(DialogBase):
    """Diálogo de registro."""
    def __init__(self, parent, auth):
        super().__init__(parent, 'Registrar', 400, 250)
        self.auth = auth
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self.dialog, text='Email:', bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=0, column=0, sticky='e', padx=10, pady=15)
        email = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        email.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text='Nombre completo:', bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=1, column=0, sticky='e', padx=10, pady=15)
        nombre = tk.Entry(self.dialog, font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        nombre.grid(row=1, column=1, padx=10, pady=15)

        tk.Label(self.dialog, text='Contraseña:', bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).grid(row=2, column=0, sticky='e', padx=10, pady=15)
        pwd = tk.Entry(self.dialog, show='*', font=(FONT_FAMILY, FONT_SIZE_LABEL), width=30)
        pwd.grid(row=2, column=1, padx=10, pady=15)

        def submit():
            e, n, p = email.get().strip(), nombre.get().strip(), pwd.get().strip()
            if not e or not n or not p:
                messagebox.showerror('Error', 'Todos los campos son requeridos')
                return
            try:
                res = self.auth.registrar_cuenta(e, p, n)
            except Exception as exc:
                res = {'success': False, 'error': str(exc)}

            if isinstance(res, dict) and res.get('success'):
                self.parent._session_id = res.get('session_id')
                try:
                    self.parent.service.set_current_user(res.get('user_id'))
                except Exception:
                    pass
                nombre_usuario = res.get('datos_usuario', {}).get('nombre') if isinstance(res.get('datos_usuario'), dict) else None
                self.parent.current_user_var.set(nombre_usuario or res.get('user_id'))
                self.parent.session_var.set(f"Sesión: {self.parent._session_id[:8]}..." if self.parent._session_id else "")
                messagebox.showinfo('OK', f"Cuenta creada. Bienvenido {nombre_usuario or res.get('user_id')}")
                self.dialog.destroy()
                self.parent._update_login_ui()
                self.parent.view_manager.show_stores()
            else:
                messagebox.showerror('Error', f"Error: {res.get('error', 'Error desconocido')}")

        tk.Button(self.dialog, text='Registrar', bg=ACCENT_COLOR, fg='white',
                 command=submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=10).grid(row=3, column=0, columnspan=2, pady=20)
