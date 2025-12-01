import logging
from base_datos.firebase_client import FirebaseClient

logger = logging.getLogger(__name__)


class MetricsServiceMixin:

    def record_metric(self, store_id: str, metric_data: dict):
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de registrar métricas."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}
        
        if not self._current_user:
            return {"success": False, "error": "No hay usuario autenticado"}
        
        if 'metric_type' not in metric_data:
            return {"success": False, "error": "Tipo de métrica requerido"}
        if 'value' not in metric_data:
            return {"success": False, "error": "Valor de métrica requerido"}
        
        try:
            float(metric_data['value'])
        except (ValueError, TypeError):
            return {"success": False, "error": "El valor debe ser un número válido"}
        
        return self.firebase.record_metric(store_id, metric_data)

    def get_store_metrics(self, store_id: str, metric_type: str = None, limit: int = 50):
        if not self._current_store:
            return {"success": False, "error": "No hay tienda activa. Seleccione la tienda antes de ver métricas."}
        if str(store_id) != str(self._current_store):
            return {"success": False, "error": "El ID de la tienda no coincide con la tienda activa."}
        
        return self.firebase.get_store_metrics(store_id, metric_type, limit)

    def update_metric(self, metric_id: str, updates: dict):
        if not self._current_user:
            return {"success": False, "error": "No hay usuario autenticado"}
        
        if not updates:
            return {"success": False, "error": "No hay datos para actualizar"}
        
        if 'value' in updates:
            try:
                float(updates['value'])
            except (ValueError, TypeError):
                return {"success": False, "error": "El valor debe ser un número válido"}
        
        
        return {"success": False, "error": "Actualización de métricas no implementada aún"}

    def delete_metric(self, metric_id: str):
        if not self._current_user:
            return {"success": False, "error": "No hay usuario autenticado"}
        
        return self.firebase.delete_metric(metric_id)

