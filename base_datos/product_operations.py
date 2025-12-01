"""Operaciones de productos."""
import logging
from .db_base import DatabaseBase

logger = logging.getLogger(__name__)


class ProductOperations(DatabaseBase):
    """Operaciones CRUD de productos."""

    def create_product(self, store_id, product_data: dict):
        """Crea producto."""
        try:
            if not store_id:
                return self._error_response("ID de tienda requerido")
            
            if not isinstance(product_data, dict):
                return self._error_response("Datos de producto inválidos")
            
            required = ['name', 'price']
            for key in required:
                if key not in product_data:
                    return self._error_response(f"Falta {key}")

            name = str(product_data['name']).strip()
            if not name or len(name) < 2:
                return self._error_response("El nombre del producto debe tener al menos 2 caracteres")
            
            try:
                price = float(product_data['price'])
                if price < 0:
                    return self._error_response("El precio no puede ser negativo")
            except (ValueError, TypeError):
                return self._error_response("El precio debe ser un número válido")

            if not self.stores_ref:
                return self._error_response("Firestore no inicializado")

            products_col = self.stores_ref.document(str(store_id)).collection('products')
            doc_ref = products_col.document()
            # Asegurar que price sea string para consistencia
            product_data['price'] = str(price)
            product_data['name'] = name
            doc_ref.set(product_data)
            
            return self._success_response(product_id=doc_ref.id)
        except Exception as e:
            logger.exception("Error en create_product: %s", e)
            return self._error_response(str(e))

    def get_store_products(self, store_id):
        """Obtiene productos de tienda."""
        try:
            if not store_id:
                return self._error_response("ID de tienda requerido")
            
            if not self.stores_ref:
                return self._error_response("Firestore no inicializado")
            
            products_col = self.stores_ref.document(str(store_id)).collection('products')
            docs = products_col.stream()
            products = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            return self._success_response(products=products)
        except Exception as e:
            logger.exception("Error en get_store_products: %s", e)
            return self._error_response(str(e))

    def update_product(self, store_id, product_id, updates: dict):
        """Actualiza producto."""
        try:
            if not store_id or not product_id:
                return self._error_response("ID de tienda y producto requeridos")
            
            if not isinstance(updates, dict) or not updates:
                return self._error_response("Datos de actualización inválidos")
            
            if not self.stores_ref:
                return self._error_response("Firestore no inicializado")
            
            # Validar price si está presente
            if 'price' in updates:
                try:
                    price = float(updates['price'])
                    if price < 0:
                        return self._error_response("El precio no puede ser negativo")
                    updates['price'] = str(price)
                except (ValueError, TypeError):
                    return self._error_response("El precio debe ser un número válido")
            
            # Validar name si está presente
            if 'name' in updates:
                name = str(updates['name']).strip()
                if not name or len(name) < 2:
                    return self._error_response("El nombre del producto debe tener al menos 2 caracteres")
                updates['name'] = name
            
            products_col = self.stores_ref.document(str(store_id)).collection('products')
            products_col.document(str(product_id)).update(updates)
            return self._success_response()
        except Exception as e:
            logger.exception("Error en update_product: %s", e)
            return self._error_response(str(e))

    def delete_product(self, store_id, product_id):
        """Elimina producto."""
        try:
            if not store_id or not product_id:
                return self._error_response("ID de tienda y producto requeridos")
            
            if not self.stores_ref:
                return self._error_response("Firestore no inicializado")
            
            products_col = self.stores_ref.document(str(store_id)).collection('products')
            products_col.document(str(product_id)).delete()
            return self._success_response()
        except Exception as e:
            logger.exception("Error en delete_product: %s", e)
            return self._error_response(str(e))
