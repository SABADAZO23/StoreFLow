"""Operaciones de empleados."""
import logging
from .db_base import DatabaseBase

logger = logging.getLogger(__name__)


class StaffOperations(DatabaseBase):
    """Operaciones CRUD de empleados."""

    def add_store_staff(self, store_id, staff_data):
        """Agrega empleado a tienda."""
        try:
            if not isinstance(staff_data, dict):
                return self._error_response("Datos de empleado inválidos")
            
            if 'name' not in staff_data or 'role' not in staff_data:
                return self._error_response("Nombre y rol son requeridos")

            staff_col = self.stores_ref.document(store_id).collection('staff')
            doc_ref = staff_col.document()
            doc_ref.set(staff_data)
            
            return self._success_response(staff_id=doc_ref.id)
        except Exception as e:
            logger.exception("Error en add_store_staff: %s", e)
            return self._error_response(str(e))

    def get_store_staff(self, store_id):
        """Obtiene empleados de tienda."""
        try:
            staff_col = self.stores_ref.document(store_id).collection('staff')
            docs = staff_col.stream()
            staff = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            return self._success_response(staff=staff)
        except Exception as e:
            logger.exception("Error en get_store_staff: %s", e)
            return self._error_response(str(e))

    def update_store_staff(self, store_id, staff_id, updates: dict):
        """Actualiza empleado."""
        try:
            staff_col = self.stores_ref.document(store_id).collection('staff')
            staff_col.document(staff_id).update(updates)
            return self._success_response()
        except Exception as e:
            logger.exception("Error en update_store_staff: %s", e)
            return self._error_response(str(e))

    def delete_store_staff(self, store_id, staff_id):
        """Elimina empleado."""
        try:
            staff_col = self.stores_ref.document(store_id).collection('staff')
            staff_col.document(staff_id).delete()
            return self._success_response()
        except Exception as e:
            logger.exception("Error en delete_store_staff: %s", e)
            return self._error_response(str(e))

