"""Ventana principal de la aplicación."""
import tkinter as tk
from tkinter import messagebox

from ui.config import BG_COLOR, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
from ui.stub_service import StubService
from ui.dialogs_auth import LoginDialog, RegisterDialog
from ui.views import ViewManager
from ui.sidebar import SidebarPanel
from ui.window_utils import center_window


class MainWindow(tk.Tk):
    """Ventana principal."""

    def __init__(self, service=None, auth=None):
        super().__init__()
        self.title("StoreFlow")
        self.configure(bg=BG_COLOR)
        self.geometry(f"{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")
        center_window(self)

        self.auth = auth
        self.service = service or self._get_service()
        self.current_user_var = tk.StringVar(value="No autenticado")
        self.session_var = tk.StringVar(value="")
        self._session_id = None
        self.view_manager = None
        self.sidebar_panel = None

        self._build_ui()

    def _get_service(self):
        """Obtiene servicio real o stub."""
        try:
            from gestionar_tienda import GestorTiendasService
            return GestorTiendasService()
        except Exception:
            return StubService()

    def _build_ui(self):
        """Construye UI."""
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_panel = SidebarPanel(self, self)
        self.sidebar = self.sidebar_panel.build()

        # Content area
        self.content = tk.Frame(self, bg=BG_COLOR, padx=10, pady=10)
        self.content.grid(row=0, column=1, sticky="nsew")

        # Title
        self.title_label = tk.Label(self.content, text="Bienvenido", bg=BG_COLOR, fg="#212A3E", font=("Helvetica", 18, "bold"))
        self.title_label.pack(anchor="nw")

        # View frame
        self.view_frame = tk.Frame(self.content, bg=BG_COLOR)
        self.view_frame.pack(fill="both", expand=True, pady=(10, 0))

        # ViewManager
        self.view_manager = ViewManager(self)

        # Listeners
        try:
            if hasattr(self.service, 'add_listener'):
                self.service.add_listener(self._on_service_event)
        except Exception:
            pass

        self._update_login_ui()
        self.view_manager.show_stores()

    def _on_service_event(self, ev: dict):
        """Callback de eventos del servicio."""
        def _apply():
            try:
                if ev.get('type') == 'user':
                    val = ev.get('value')
                    self.current_user_var.set(str(val) if val else 'No autenticado')
                    self._update_login_ui()
            except Exception:
                pass
        try:
            self.after(0, _apply)
        except Exception:
            _apply()

    def _update_login_ui(self):
        """Actualiza UI de login."""
        user = getattr(self.service, 'current_user', None)
        if user:
            self._login_btn.config(text='Logout', command=self._logout)
            self._view_session_btn.config(state='normal')
        else:
            self._login_btn.config(text='Login', command=self._dialog_login)
            self._view_session_btn.config(state='disabled')

    def _logout(self):
        """Logout."""
        if self.auth and self._session_id:
            try:
                res = self.auth.logout(self._session_id)
                if not res.get('success'):
                    messagebox.showerror('Error', f"Error: {res.get('error', '')}")
                    return
            except Exception:
                pass

        self._session_id = None
        self.session_var.set('')
        try:
            if hasattr(self.service, 'set_current_user'):
                self.service.set_current_user(None)
        except Exception:
            pass
        self.current_user_var.set('No autenticado')
        self._update_login_ui()

    def _dialog_login(self):
        """Abre login."""
        if not self.auth:
            messagebox.showerror('Error', 'Autenticación no disponible.')
            return
        LoginDialog(self, self.auth)

    def _dialog_register(self):
        """Abre registro."""
        if not self.auth:
            messagebox.showerror('Error', 'Autenticación no disponible.')
            return
        RegisterDialog(self, self.auth)

    def _view_session_data(self):
        """Muestra datos de sesión."""
        if not self.auth or not self._session_id:
            messagebox.showwarning('Advertencia', 'No hay sesión activa.')
            return
        try:
            datos = self.auth.get_datos_sesion(self._session_id)
            if datos.get("success"):
                user_data = datos.get('datos_usuario', {})
                info = f"Usuario: {user_data.get('nombre', 'N/A')}\nEmail: {user_data.get('email', 'N/A')}\nSession: {self._session_id[:16]}..."
                messagebox.showinfo('Datos de Sesión', info)
        except Exception as e:
            messagebox.showerror('Error', f'Error: {str(e)}')

    def _show_stores(self):
        if self.view_manager:
            self.view_manager.show_stores()

    def _show_staff(self):
        if self.view_manager:
            self.view_manager.show_staff()

    def _show_products(self):
        if self.view_manager:
            self.view_manager.show_products()

    def _show_sales(self):
        if self.view_manager:
            self.view_manager.show_sales()

    def _show_metrics(self):
        if self.view_manager:
            self.view_manager.show_metrics()

    def _show_full_management(self):
        if self.view_manager:
            self.view_manager.show_full_management()


def run_app(service=None, auth=None):
    """Ejecuta la app."""
    app = MainWindow(service=service, auth=auth)
    app.mainloop()


if __name__ == "__main__":
    run_app()
