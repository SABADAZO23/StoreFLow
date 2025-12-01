"""Servicio puro que implementa la lógica de negocio sobre tiendas."""
import logging
from base_datos.firebase_client import FirebaseClient
from .permissions import has_permission
from .sales_service import SalesServiceMixin
from .metrics_service import MetricsServiceMixin

logger = logging.getLogger(__name__)


class GestorTiendasService(SalesServiceMixin, MetricsServiceMixin):
    """Servicio puro que implementa la lógica de negocio sobre tiendas.
    No realiza I/O ni interacción con el usuario; devuelve estructuras de datos.
    """
    def __init__(self, firebase_client: FirebaseClient):
        self.firebase = firebase_client
        self._current_user = None
        self._user_data = {}
        self._current_store = None
        # listeners: functions that receive events {'type': 'user'|'store', 'value': ...}
        self._listeners = []

    # Listener management for UI synchronization
    def add_listener(self, fn):
        try:
            if fn not in self._listeners:
                self._listeners.append(fn)
        except Exception:
            pass

    def remove_listener(self, fn):
        try:
            if fn in self._listeners:
                self._listeners.remove(fn)
        except Exception:
            pass

    def _notify_listeners(self, ev_type: str, value):
        for fn in list(self._listeners):
            try:
                fn({'type': ev_type, 'value': value})
            except Exception:
                # listener errors should not break the service
                continue

    def set_current_user(self, value):
        """Establece el usuario actual (acepta str o dict con 'user_id')."""
        if value is None:
            self._current_user = None
            self._user_data = {}
            return

        if isinstance(value, dict):
            user_id = value.get("user_id")
            if user_id:
                self._current_user = user_id
                self._user_data = value
            else:
                self._current_user = None
                self._user_data = {}
        elif isinstance(value, str):
            self._current_user = value
        else:
            self._current_user = None
            self._user_data = {}
        # notify listeners about user change
        try:
            self._notify_listeners('user', self._current_user)
        except Exception:
            pass

    @property
    def current_user(self):
        return self._current_user

    @property
    def user_data(self):
        return self._user_data

    @property
    def current_store(self):
        """ID de la tienda actualmente seleccionada (o None)"""
        return self._current_store

    def set_current_store(self, store_id: str):
        """Establece la tienda activa. Pasa None para limpiar la selección."""
        if store_id is None:
            self._current_store = None
            return
        # permitimos dicts con 'id' o strings
        if isinstance(store_id, dict):
            self._current_store = store_id.get('id') or store_id.get('store_id')
        else:
            self._current_store = str(store_id)
        # notify listeners about store change
        try:
            self._notify_listeners('store', self._current_store)
        except Exception:
            pass

    def create_store(self, store_info: dict, owner_id: str = None):
        """Crea una tienda; owner_id opcional usa el current_user.
        Retorna el dict result como lo devuelve FirebaseClient.
        """
        if owner_id is None:
            owner_id = self._current_user

        return self.firebase.create_store(store_info=store_info, owner_id=owner_id)

    def add_store_staff(self, store_id: str, staff_data: dict):
        """Agrega empleado verificando permisos del current_user."""
        user_id = self._current_user
        if not user_id:
            return {"success": False, "error": "No hay usuario autenticado"}

        # require explicit store context: it must match current_store
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de administrar empleados."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}

        verify = self.firebase.verify_owner(user_id, store_id)
        if not verify.get("success") or not verify.get("is_owner"):
            return {"success": False, "error": "No tiene permisos"}

        return self.firebase.add_store_staff(store_id, staff_data)

    def update_employee(self, store_id: str, staff_id: str, updates: dict):
        """Actualiza datos de un empleado (solo propietario puede hacerlo)."""
        user_id = self._current_user
        if not user_id:
            return {"success": False, "error": "No hay usuario autenticado"}

        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de administrar empleados."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}

        verify = self.firebase.verify_owner(user_id, store_id)
        if not verify.get("success") or not verify.get("is_owner"):
            return {"success": False, "error": "No tiene permisos"}

        return self.firebase.update_store_staff(store_id, staff_id, updates)

    def remove_employee(self, store_id: str, staff_id: str):
        """Elimina un empleado (solo propietario puede hacerlo)."""
        user_id = self._current_user
        if not user_id:
            return {"success": False, "error": "No hay usuario autenticado"}
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de administrar empleados."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}
        verify = self.firebase.verify_owner(user_id, store_id)
        if not verify.get("success") or not verify.get("is_owner"):
            return {"success": False, "error": "No tiene permisos"}

        return self.firebase.delete_store_staff(store_id, staff_id)

    def create_product(self, store_id: str, product_data: dict):
        """Crea un producto en una tienda (solo propietario)."""
        user_id = self._current_user
        if not user_id:
            return {"success": False, "error": "No hay usuario autenticado"}
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de administrar productos."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}

        # Permisos: propietario o empleado con permisos específicos
        if not has_permission(self.firebase, user_id, store_id, 'products.create'):
            return {"success": False, "error": "No tiene permisos para crear productos"}

        return self.firebase.create_product(store_id, product_data)

    def get_store_products(self, store_id: str):
        """Lista productos de una tienda. Requiere tienda activa y que coincida."""
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de ver productos."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}
        # Allow viewing if has view permission
        if not has_permission(self.firebase, self._current_user, store_id, 'products.view'):
            return {"success": False, "error": "No tiene permisos para ver productos"}
        return self.firebase.get_store_products(store_id)

    def update_product(self, store_id: str, product_id: str, updates: dict):
        """Actualiza un producto (only owner)."""
        user_id = self._current_user
        if not user_id:
            return {"success": False, "error": "No hay usuario autenticado"}
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de administrar productos."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}

        if not has_permission(self.firebase, user_id, store_id, 'products.update'):
            return {"success": False, "error": "No tiene permisos para actualizar productos"}

        return self.firebase.update_product(store_id, product_id, updates)

    def delete_product(self, store_id: str, product_id: str):
        """Elimina un producto (only owner)."""
        user_id = self._current_user
        if not user_id:
            return {"success": False, "error": "No hay usuario autenticado"}
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de administrar productos."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}

        if not has_permission(self.firebase, user_id, store_id, 'products.delete'):
            return {"success": False, "error": "No tiene permisos para eliminar productos"}

        return self.firebase.delete_product(store_id, product_id)

    def get_user_stores(self, user_id: str = None):
        if user_id is None:
            user_id = self._current_user
        return self.firebase.get_user_stores(user_id)

    def get_store_staff(self, store_id: str):
        return self.firebase.get_store_staff(store_id)
    
    # Métodos delegados a Firebase para compatibilidad
    # Los métodos de ventas y métricas están en los mixins

