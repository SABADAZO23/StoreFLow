"""Operaciones de métricas."""
import logging
from datetime import datetime
from .db_base import DatabaseBase

logger = logging.getLogger(__name__)


class MetricsOperations(DatabaseBase):
    """Operaciones de cálculo y almacenamiento de métricas."""

    def record_metric(self, store_id, metric_data: dict):
        """Registra una métrica."""
        try:
            if not self.metrics_ref:
                return self._error_response("Firestore no inicializado")
            
            if not store_id:
                return self._error_response("ID de tienda requerido")
            
            if 'metric_type' not in metric_data:
                return self._error_response("Tipo de métrica requerido")
            
            if 'value' not in metric_data:
                return self._error_response("Valor de métrica requerido")
            
            try:
                value = float(metric_data.get('value', 0))
            except (ValueError, TypeError):
                return self._error_response("El valor debe ser un número válido")
            
            metric_record = {
                'store_id': str(store_id),
                'metric_type': str(metric_data.get('metric_type')),  # sales, revenue, inventory, etc
                'value': value,
                'description': str(metric_data.get('description', '')),
                'period': str(metric_data.get('period', 'daily')),  # daily, weekly, monthly
                'timestamp': self._get_timestamp()
            }

            doc_ref = self.metrics_ref.document()
            doc_ref.set(metric_record)
            
            return self._success_response(metric_id=doc_ref.id)
        except Exception as e:
            logger.exception("Error en record_metric: %s", e)
            return self._error_response(str(e))

    def get_store_metrics(self, store_id, metric_type=None, limit=50):
        """Obtiene métricas de una tienda."""
        try:
            if not self.metrics_ref:
                return self._error_response("Firestore no inicializado")
            
            if not store_id:
                return self._error_response("ID de tienda requerido")
            
            # Importar excepción de Firestore para manejar errores de índice
            try:
                from google.api_core import exceptions as gcp_exceptions
            except ImportError:
                gcp_exceptions = None
            
            metrics = []
            use_manual_sort = False
            
            try:
                query = self.metrics_ref.where('store_id', '==', str(store_id))
                
                if metric_type:
                    query = query.where('metric_type', '==', str(metric_type))
                
                # Intentar ordenar por timestamp
                query = query.order_by('timestamp', direction='DESCENDING').limit(limit)
                docs = query.stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    metrics.append(data)
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
                    logger.warning("Índice de Firestore no disponible para ordenamiento, obteniendo métricas sin ordenar")
                    use_manual_sort = True
                else:
                    logger.warning("Error al obtener métricas ordenadas: %s", error_msg)
                
                # Obtener sin ordenar
                try:
                    query = self.metrics_ref.where('store_id', '==', str(store_id))
                    if metric_type:
                        query = query.where('metric_type', '==', str(metric_type))
                    query = query.limit(limit * 2)  # Obtener más para ordenar manualmente
                    docs = query.stream()
                    
                    for doc in docs:
                        data = doc.to_dict()
                        data['id'] = doc.id
                        metrics.append(data)
                except Exception as e2:
                    logger.exception("Error al obtener métricas sin ordenar: %s", e2)
                    return self._error_response(f"Error al obtener métricas: {str(e2)}")
            
            # Ordenar manualmente si fue necesario
            if use_manual_sort and metrics:
                try:
                    def get_timestamp_key(metric):
                        """Obtiene una clave ordenable del timestamp."""
                        ts = metric.get('timestamp')
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
                    metrics.sort(key=get_timestamp_key, reverse=True)
                    # Limitar después de ordenar
                    metrics = metrics[:limit]
                except Exception as e:
                    logger.warning("No se pudo ordenar métricas manualmente: %s", e)
                    # Limitar sin ordenar
                    metrics = metrics[:limit]
            
            return self._success_response(metrics=metrics)
        except Exception as e:
            logger.exception("Error en get_store_metrics: %s", e)
            return self._error_response(str(e))

    def calculate_revenue(self, sales_list):
        """Calcula ingresos totales desde lista de ventas."""
        try:
            total = sum(sale.get('total', 0) for sale in sales_list)
            return self._success_response(revenue=total)
        except Exception as e:
            logger.exception("Error en calculate_revenue: %s", e)
            return self._error_response(str(e))

    def calculate_sales_count(self, sales_list):
        """Calcula cantidad total de ventas."""
        try:
            count = len(sales_list)
            avg_value = sum(s.get('total', 0) for s in sales_list) / count if count > 0 else 0
            return self._success_response(count=count, average=avg_value)
        except Exception as e:
            logger.exception("Error en calculate_sales_count: %s", e)
            return self._error_response(str(e))

    def get_top_products(self, sales_list, limit=5):
        """Obtiene productos más vendidos."""
        try:
            product_stats = {}
            for sale in sales_list:
                product_id = sale.get('product_id')
                product_name = sale.get('product_name', 'N/A')
                if product_id:
                    if product_id not in product_stats:
                        product_stats[product_id] = {'quantity': 0, 'revenue': 0, 'product_name': product_name}
                    product_stats[product_id]['quantity'] += sale.get('quantity', 0)
                    product_stats[product_id]['revenue'] += sale.get('total', 0)
            
            top = sorted(product_stats.items(), 
                        key=lambda x: x[1]['quantity'], 
                        reverse=True)[:limit]
            
            return self._success_response(top_products=[{'product_id': p[0], **p[1]} for p in top])
        except Exception as e:
            logger.exception("Error en get_top_products: %s", e)
            return self._error_response(str(e))

    def delete_metric(self, metric_id):
        """Elimina una métrica."""
        try:
            self.metrics_ref.document(metric_id).delete()
            return self._success_response()
        except Exception as e:
            logger.exception("Error en delete_metric: %s", e)
            return self._error_response(str(e))
