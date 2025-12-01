"""Módulo de servicio para gestión de ventas."""
import logging
from base_datos.firebase_client import FirebaseClient

logger = logging.getLogger(__name__)


class SalesServiceMixin:
    """Mixin con métodos de servicio para ventas."""

    def record_sale(self, store_id: str, sale_data: dict):
        """Registra una venta en una tienda."""
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de registrar ventas."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}
        
        # Validar que el producto existe y tiene stock suficiente
        product_id = sale_data.get('product_id')
        quantity = sale_data.get('quantity', 0)
        
        if product_id:
            products_res = self.firebase.get_store_products(store_id)
            if products_res.get('success'):
                products = products_res.get('products', [])
                product = next((p for p in products if p.get('id') == product_id), None)
                if not product:
                    return {"success": False, "error": "Producto no encontrado"}
                
                # Verificar stock si está disponible
                stock = product.get('stock')
                if stock is not None:
                    try:
                        stock_int = int(stock)
                        if stock_int < quantity:
                            return {"success": False, "error": f"Stock insuficiente. Disponible: {stock_int}"}
                    except (ValueError, TypeError):
                        pass
        
        # Registrar la venta
        result = self.firebase.record_sale(store_id, sale_data)
        
        # Si la venta fue exitosa y hay producto, actualizar stock
        if result.get('success') and product_id and product:
            try:
                stock = product.get('stock')
                if stock is not None:
                    stock_int = int(stock)
                    new_stock = stock_int - quantity
                    if new_stock >= 0:
                        self.firebase.update_product(store_id, product_id, {'stock': str(new_stock)})
            except Exception as e:
                logger.exception("Error actualizando stock después de venta: %s", e)
        
        return result

    def get_store_sales(self, store_id: str, limit: int = 100):
        """Obtiene las ventas de una tienda."""
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de ver ventas."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}
        
        return self.firebase.get_store_sales(store_id, limit)

    def delete_sale(self, sale_id: str):
        """Elimina una venta."""
        if not self._current_user:
            return {"success": False, "error": "No hay usuario autenticado"}
        
        return self.firebase.delete_sale(sale_id)

    def calculate_revenue(self, sales_list: list):
        """Calcula ingresos totales desde lista de ventas."""
        return self.firebase.calculate_revenue(sales_list)

    def calculate_sales_count(self, sales_list: list):
        """Calcula cantidad total de ventas."""
        return self.firebase.calculate_sales_count(sales_list)

    def get_top_products(self, sales_list: list, limit: int = 5):
        """Obtiene productos más vendidos."""
        return self.firebase.get_top_products(sales_list, limit)

