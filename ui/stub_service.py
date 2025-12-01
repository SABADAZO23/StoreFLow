"""Servicio stub para cuando no hay servicio real disponible."""


class StubService:
    """Servicio stub que proporciona respuestas simuladas."""

    def __init__(self):
        self.current_user = None
        self.current_store = None

    def get_user_stores(self):
        """Retorna lista vacía."""
        return {"success": True, "stores": []}

    def get_store_staff(self, store_id):
        """Retorna lista vacía."""
        return {"success": True, "staff": []}

    def get_store_products(self, store_id):
        """Retorna lista vacía."""
        return {"success": True, "products": []}

    def get_store_sales(self, store_id, limit=100):
        """Retorna lista vacía."""
        return {"success": True, "sales": []}

    def record_sale(self, store_id, sale_data):
        """Registra venta simulada."""
        return {"success": True, "sale_id": "stub_001"}

    def delete_sale(self, sale_id):
        """Elimina venta simulada."""
        return {"success": True}

    def calculate_revenue(self, sales_list):
        """Calcula ingresos."""
        return {"success": True, "revenue": 0}

    def calculate_sales_count(self, sales_list):
        """Calcula cantidad de ventas."""
        return {"success": True, "count": 0, "average": 0}

    def get_top_products(self, sales_list, limit=5):
        """Obtiene productos top."""
        return {"success": True, "top_products": []}

    def set_current_store(self, store_id):
        """Establece tienda actual."""
        self.current_store = store_id
