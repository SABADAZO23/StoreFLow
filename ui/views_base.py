"""Base para vistas."""
import tkinter as tk
from typing import List, Dict, Any, Optional

from ui.config import BG_COLOR, TEXT_COLOR


class ViewBase:
    """Clase base para todas las vistas."""

    def __init__(self, main_window):
        """Inicializa la vista base.
        
        Args:
            main_window: Instancia de MainWindow
        """
        self.main_window = main_window
        self.service = main_window.service
        self.view_frame = main_window.view_frame
        self.title_label = main_window.title_label

    def clear_view(self):
        """Limpia los widgets de la vista actual."""
        for w in self.view_frame.winfo_children():
            w.destroy()

    def _get_stores(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de tiendas."""
        try:
            res = self.service.get_user_stores()
        except Exception:
            res = []

        if isinstance(res, dict):
            if not res.get('success'):
                return []
            return res.get('stores', [])
        return list(res or [])

    def _get_active_store_id(self) -> Optional[str]:
        """Obtiene la tienda activa o la primera disponible."""
        try:
            if hasattr(self.service, 'current_store') and self.service.current_store:
                return self.service.current_store
            
            stores = self._get_stores()
            if stores and len(stores) > 0:
                return stores[0].get("id")
        except Exception:
            pass
        
        return None
