"""Base para operaciones de base de datos."""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseBase:
    """Clase base para todas las operaciones de BD."""

    def __init__(self, db=None):
        """Inicializa con referencia a Firestore.
        
        Args:
            db: Cliente de Firestore (firestore.client())
        """
        self.db = db
        self.users_ref = None
        self.stores_ref = None
        self.products_ref = None
        self.sales_ref = None
        self.metrics_ref = None

        if self.db:
            self.users_ref = self.db.collection('users')
            self.stores_ref = self.db.collection('stores')
            self.products_ref = self.db.collection('products')
            self.sales_ref = self.db.collection('sales')
            self.metrics_ref = self.db.collection('metrics')

    def _get_timestamp(self):
        """Retorna timestamp actual."""
        return datetime.now()

    def _safe_get(self, value, default=None):
        """Obtiene valor de forma segura."""
        return value if value is not None else default

    def _success_response(self, **kwargs):
        """Crea respuesta exitosa."""
        return {"success": True, **kwargs}

    def _error_response(self, error: str):
        """Crea respuesta de error."""
        return {"success": False, "error": error}
