"""Operaciones de ventas."""
import logging
from datetime import datetime
from .db_base import DatabaseBase

logger = logging.getLogger(__name__)

# Importar excepción de Firestore para manejar errores de índice
try:
    from google.api_core import exceptions as gcp_exceptions
except ImportError:
    gcp_exceptions = None


class SalesOperations(DatabaseBase):
    """Operaciones de gestión de ventas con persistencia."""

    def record_sale(self, store_id, sale_data: dict):
        """Registra una venta."""
        try:
            if not self.sales_ref:
                return self._error_response("Firestore no inicializado")
            
            if not store_id:
                return self._error_response("ID de tienda requerido")
            
            required = ['product_id', 'quantity', 'unit_price']
            for key in required:
                if key not in sale_data:
                    return self._error_response(f"Falta {key}")

            quantity = int(sale_data['quantity'])
            unit_price = float(sale_data['unit_price'])
            
            if quantity <= 0 or unit_price < 0:
                return self._error_response("Cantidad y precio deben ser válidos")

            sale_record = {
                'store_id': str(store_id),
                'product_id': str(sale_data['product_id']),
                'product_name': str(sale_data.get('product_name', '')),
                'quantity': quantity,
                'unit_price': unit_price,
                'total': quantity * unit_price,
                'staff_id': sale_data.get('staff_id'),
                'notes': sale_data.get('notes', ''),
                'timestamp': self._get_timestamp()
            }

            doc_ref = self.sales_ref.document()
            doc_ref.set(sale_record)
            
            return self._success_response(sale_id=doc_ref.id)
        except Exception as e:
            logger.exception("Error en record_sale: %s", e)
            return self._error_response(str(e))

    def get_store_sales(self, store_id, limit=100):
        """Obtiene ventas de una tienda."""
        try:
            if not self.sales_ref:
                return self._error_response("Firestore no inicializado")
            
            if not store_id:
                return self._error_response("ID de tienda requerido")
            
            # Intentar obtener con ordenamiento, si falla por falta de índice, obtener sin ordenar
            sales = []
            use_manual_sort = False
            
            try:
                # Intentar consulta con ordenamiento
                query = self.sales_ref.where('store_id', '==', str(store_id)).order_by('timestamp', direction='DESCENDING').limit(limit)
                docs = query.stream()
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    sales.append(data)
            except Exception as e:
                # Verificar si es error de índice faltante
                error_msg = str(e)
                is_index_error = False
                
                if gcp_exceptions:
                    is_index_error = isinstance(e, (gcp_exceptions.FailedPrecondition, gcp_exceptions.InvalidArgument))
                else:
                    # Verificar por mensaje de error
                    is_index_error = 'index' in error_msg.lower() or 'requires an index' in error_msg.lower()
                
                if is_index_error:
                    logger.warning("Índice de Firestore no disponible para ordenamiento, obteniendo ventas sin ordenar")
                    use_manual_sort = True
                else:
                    logger.warning("Error al obtener ventas ordenadas: %s", error_msg)
                
                # Obtener sin ordenar
                try:
                    query = self.sales_ref.where('store_id', '==', str(store_id)).limit(limit * 2)  # Obtener más para ordenar manualmente
                    docs = query.stream()
                    for doc in docs:
                        data = doc.to_dict()
                        data['id'] = doc.id
                        sales.append(data)
                except Exception as e2:
                    logger.exception("Error al obtener ventas sin ordenar: %s", e2)
                    return self._error_response(f"Error al obtener ventas: {str(e2)}")
            
            # Ordenar manualmente si fue necesario
            if use_manual_sort and sales:
                try:
                    def get_timestamp_key(sale):
                        """Obtiene una clave ordenable del timestamp."""
                        ts = sale.get('timestamp')
                        if ts is None:
                            return datetime.min
                        # Si es un objeto datetime (Firestore o Python)
                        if isinstance(ts, datetime):
                            return ts
                        # Si tiene método timestamp (objetos datetime-like)
                        if hasattr(ts, 'timestamp'):
                            try:
                                return datetime.fromtimestamp(ts.timestamp())
                            except:
                                return datetime.min
                        # Si es string ISO, intentar parsear básico
                        if isinstance(ts, str):
                            try:
                                # Formato ISO básico: YYYY-MM-DDTHH:MM:SS
                                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            except:
                                return datetime.min
                        return datetime.min
                    
                    # Ordenar por timestamp descendente (más recientes primero)
                    sales.sort(key=get_timestamp_key, reverse=True)
                    # Limitar después de ordenar
                    sales = sales[:limit]
                except Exception as e:
                    logger.warning("No se pudo ordenar ventas manualmente: %s", e)
                    # Limitar sin ordenar
                    sales = sales[:limit]
            
            return self._success_response(sales=sales)
        except Exception as e:
            logger.exception("Error en get_store_sales: %s", e)
            return self._error_response(str(e))

    def get_sales_by_period(self, store_id, start_date, end_date):
        """Obtiene ventas en un período."""
        try:
            query = self.sales_ref.where('store_id', '==', store_id)
            query = query.where('timestamp', '>=', start_date)
            query = query.where('timestamp', '<=', end_date)
            docs = query.stream()
            sales = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            return self._success_response(sales=sales)
        except Exception as e:
            logger.exception("Error en get_sales_by_period: %s", e)
            return self._error_response(str(e))

    def delete_sale(self, sale_id):
        """Elimina una venta."""
        try:
            self.sales_ref.document(sale_id).delete()
            return self._success_response()
        except Exception as e:
            logger.exception("Error en delete_sale: %s", e)
            return self._error_response(str(e))
