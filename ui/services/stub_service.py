"""Servicio stub (mock) para desarrollo sin Firebase.

Mantiene datos simples en memoria y proporciona una API similar a la del servicio real.
Útil para pruebas y desarrollo sin depender de credenciales de Firebase.
"""
from typing import Optional, List, Dict, Any


class StubService:
    """Servicio de respaldo mínimo para que la UI funcione sin Firebase.

    Mantiene datos simples en memoria y una API parecida a la del servicio real.
    """

    def __init__(self):
        self._stores = [
            {"id": "demo-1", "name": "Tienda Demo", "address": "Calle Demo 1", "phone": ""},
            {"id": "demo-2", "name": "Tienda Segunda", "address": "Calle Demo 2", "phone": ""},
        ]
        self._staff = {
            "demo-1": [{"id": "emp1", "name": "Vendedor Demo", "role": "seller", "user_id": "u1"}],
            "demo-2": [],
        }
        self._products = {
            "demo-1": [{"id": "p1", "name": "Producto Demo", "price": 9.9, "stock": 10}],
            "demo-2": [],
        }
        self.current_store = None
        self.current_user = None

    # Stores
    def get_user_stores(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Retorna lista de tiendas para compatibilidad con código UI."""
        return list(self._stores)

    def create_store(self, store_info: dict, owner_id: str = None) -> Dict[str, Any]:
        """Crea una nueva tienda."""
        new_id = f"demo-{len(self._stores) + 1}"
        store = {"id": new_id, **store_info}
        self._stores.append(store)
        self._staff[new_id] = []
        self._products[new_id] = []
        return {"success": True, "store_id": new_id}

    def set_current_store(self, store_id: str) -> None:
        """Establece la tienda activa."""
        self.current_store = store_id

    def set_current_user(self, user_id: Optional[str]) -> None:
        """Establece el usuario actual."""
        self.current_user = user_id

    # Staff
    def get_store_staff(self, store_id: str) -> List[Dict[str, Any]]:
        """Obtiene empleados de una tienda."""
        return list(self._staff.get(store_id, []))

    def add_store_staff(self, store_id: str, staff_data: dict) -> Dict[str, Any]:
        """Agrega un empleado a una tienda."""
        sid = f"emp{len(self._staff.get(store_id, [])) + 1}"
        entry = {"id": sid, **staff_data}
        self._staff.setdefault(store_id, []).append(entry)
        return {"success": True, "staff_id": sid}

    def update_employee(self, store_id: str, staff_id: str, updates: dict) -> Dict[str, Any]:
        """Actualiza datos de un empleado."""
        staff_list = self._staff.get(store_id, [])
        for employee in staff_list:
            if employee.get("id") == staff_id:
                employee.update(updates)
                return {"success": True}
        return {"success": False, "error": "Empleado no encontrado"}

    def remove_employee(self, store_id: str, staff_id: str) -> Dict[str, Any]:
        """Elimina un empleado de una tienda."""
        staff_list = self._staff.get(store_id, [])
        for i, employee in enumerate(staff_list):
            if employee.get("id") == staff_id:
                staff_list.pop(i)
                return {"success": True}
        return {"success": False, "error": "Empleado no encontrado"}

    # Products
    def get_store_products(self, store_id: str) -> List[Dict[str, Any]]:
        """Obtiene productos de una tienda."""
        return list(self._products.get(store_id, []))

    def create_product(self, store_id: str, product_data: dict) -> Dict[str, Any]:
        """Crea un nuevo producto."""
        pid = f"p{len(self._products.get(store_id, [])) + 1}"
        entry = {"id": pid, **product_data}
        self._products.setdefault(store_id, []).append(entry)
        return {"success": True, "product_id": pid}

    def update_product(self, store_id: str, product_id: str, updates: dict) -> Dict[str, Any]:
        """Actualiza datos de un producto."""
        products_list = self._products.get(store_id, [])
        for product in products_list:
            if product.get("id") == product_id:
                product.update(updates)
                return {"success": True}
        return {"success": False, "error": "Producto no encontrado"}

    def delete_product(self, store_id: str, product_id: str) -> Dict[str, Any]:
        """Elimina un producto de una tienda."""
        products_list = self._products.get(store_id, [])
        for i, product in enumerate(products_list):
            if product.get("id") == product_id:
                products_list.pop(i)
                return {"success": True}
        return {"success": False, "error": "Producto no encontrado"}

    def add_listener(self, callback) -> None:
        """Interfaz para añadir listeners (compatible con servicio real)."""
        pass
