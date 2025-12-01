"""Diálogo para gestionar métricas."""
import tkinter as tk
from tkinter import messagebox, ttk
from ui.config import BG_COLOR, TEXT_COLOR, ACCENT_COLOR, FONT_FAMILY, FONT_SIZE_LABEL, FONT_SIZE_BUTTON
from ui.window_utils import center_window


class MetricDialog:
    """Diálogo para registrar o actualizar métricas."""

    def __init__(self, parent, service, store_id, metric_data=None, on_success=None):
        """Inicializa el diálogo de métrica.
        
        Args:
            parent: Ventana padre
            service: Servicio de tiendas
            store_id: ID de la tienda
            metric_data: Datos de métrica existente (para edición) o None (para nueva)
            on_success: Callback cuando la métrica se guarda exitosamente
        """
        self.service = service
        self.store_id = store_id
        self.metric_data = metric_data
        self.on_success = on_success
        self.is_edit = metric_data is not None
        
        self.dialog = tk.Toplevel(parent)
        title = "Editar Métrica" if self.is_edit else "Nueva Métrica"
        self.dialog.title(title)
        self.dialog.configure(bg=BG_COLOR)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        center_window(self.dialog, 450, 350, parent)
        
        self._build_ui()

    def _build_ui(self):
        """Construye la interfaz del diálogo."""
        # Título
        title_text = "Editar Métrica" if self.is_edit else "Nueva Métrica"
        title = tk.Label(self.dialog, text=title_text, bg=BG_COLOR, fg=TEXT_COLOR,
                        font=(FONT_FAMILY, 16, "bold"))
        title.pack(pady=10)
        
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tipo de métrica
        tk.Label(main_frame, text="Tipo de métrica:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=5)
        
        self.metric_type_var = tk.StringVar()
        metric_types = ['sales', 'revenue', 'inventory', 'customers', 'other']
        self.metric_type_combo = ttk.Combobox(main_frame, textvariable=self.metric_type_var,
                                             values=metric_types, state="readonly", width=40)
        self.metric_type_combo.pack(fill="x", pady=5)
        
        # Valor
        tk.Label(main_frame, text="Valor:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=(10, 5))
        
        self.value_var = tk.StringVar()
        value_entry = tk.Entry(main_frame, textvariable=self.value_var,
                              font=(FONT_FAMILY, FONT_SIZE_LABEL), width=20)
        value_entry.pack(anchor="w", pady=5)
        
        # Período
        tk.Label(main_frame, text="Período:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=(10, 5))
        
        self.period_var = tk.StringVar(value="daily")
        period_combo = ttk.Combobox(main_frame, textvariable=self.period_var,
                                   values=['daily', 'weekly', 'monthly', 'yearly'],
                                   state="readonly", width=40)
        period_combo.pack(fill="x", pady=5)
        
        # Descripción
        tk.Label(main_frame, text="Descripción:", bg=BG_COLOR, fg=TEXT_COLOR,
                font=(FONT_FAMILY, FONT_SIZE_LABEL)).pack(anchor="w", pady=(10, 5))
        
        self.description_text = tk.Text(main_frame, height=3, width=40,
                                       font=(FONT_FAMILY, FONT_SIZE_LABEL - 2))
        self.description_text.pack(fill="x", pady=5)
        
        # Cargar datos si es edición
        if self.is_edit:
            self.metric_type_var.set(self.metric_data.get('metric_type', ''))
            self.value_var.set(str(self.metric_data.get('value', '')))
            self.period_var.set(self.metric_data.get('period', 'daily'))
            self.description_text.insert('1.0', self.metric_data.get('description', ''))
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg=BG_COLOR)
        buttons_frame.pack(fill="x", pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", bg="#ccc", fg=TEXT_COLOR,
                 command=self.dialog.destroy,
                 font=(FONT_FAMILY, FONT_SIZE_BUTTON), padx=20, pady=5).pack(side="right", padx=5)
        
        button_text = "Actualizar" if self.is_edit else "Registrar"
        tk.Button(buttons_frame, text=button_text, bg=ACCENT_COLOR, fg="white",
                 command=self._submit, font=(FONT_FAMILY, FONT_SIZE_BUTTON, "bold"),
                 padx=20, pady=5).pack(side="right", padx=5)

    def _submit(self):
        """Guarda la métrica."""
        try:
            metric_type = self.metric_type_var.get().strip()
            if not metric_type:
                messagebox.showerror('Error', 'Selecciona un tipo de métrica')
                return
            
            value_str = self.value_var.get().strip()
            if not value_str:
                messagebox.showerror('Error', 'Ingresa un valor')
                return
            
            try:
                value = float(value_str)
            except ValueError:
                messagebox.showerror('Error', 'El valor debe ser un número válido')
                return
            
            description = self.description_text.get('1.0', 'end-1c').strip()
            period = self.period_var.get()
            
            metric_data = {
                'metric_type': metric_type,
                'value': value,
                'description': description,
                'period': period
            }
            
            if self.is_edit:
                # Actualizar métrica (por ahora solo registramos una nueva)
                # En una implementación completa, necesitaríamos update_metric
                messagebox.showinfo('Info', 
                                  'Actualización de métricas se implementará próximamente.\n'
                                  'Por ahora, se registrará una nueva métrica.')
                metric_data = metric_data  # Continuar con registro
            
            res = self.service.record_metric(self.store_id, metric_data)
            if res.get('success'):
                action = "actualizada" if self.is_edit else "registrada"
                messagebox.showinfo('Éxito', f'Métrica {action} correctamente')
                self.dialog.destroy()
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showerror('Error', res.get('error', 'Error desconocido'))
        except Exception as e:
            messagebox.showerror('Error', f'Error: {str(e)}')

