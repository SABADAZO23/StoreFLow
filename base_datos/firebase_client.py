"""Cliente Firebase unificado - Fachada que integra todos los módulos."""
import logging
import os

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
except Exception:
    firebase_admin = None
    credentials = None
    auth = None
    firestore = None

from .auth_operations import AuthOperations
from .store_operations import StoreOperations
from .staff_operations import StaffOperations
from .product_operations import ProductOperations
from .sales_operations import SalesOperations
from .metrics_operations import MetricsOperations


class FirebaseClient:
    """Fachada que integra todos los módulos de operaciones."""

    def __init__(self, auth_ops=None, store_ops=None, staff_ops=None,
                 product_ops=None, sales_ops=None, metrics_ops=None):
        """Inicializa con instancias de operaciones."""
        self._auth = auth_ops or AuthOperations()
        self._stores = store_ops or StoreOperations()
        self._staff = staff_ops or StaffOperations()
        self._products = product_ops or ProductOperations()
        self._sales = sales_ops or SalesOperations()
        self._metrics = metrics_ops or MetricsOperations()

    @classmethod
    def from_service_account(cls, service_account_path: str = None, api_key: str = None):
        """Inicializa Firebase y crea cliente con todas las operaciones.
        
        Args:
            service_account_path: Ruta al archivo serviceAccountKey.json
            api_key: API key de Firebase para autenticación (opcional)
        """
        if firebase_admin is None:
            logger.error("firebase_admin no está disponible")
            return cls()

        if not service_account_path:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            service_account_path = os.path.join(current_dir, 'configuracion', 'serviceAccountKey.json')

        try:
            api_key_from_file = None
            if os.path.exists(service_account_path):
                # Intentar obtener API key del archivo de configuración
                try:
                    import json
                    with open(service_account_path, 'r') as f:
                        service_data = json.load(f)
                        # La API key no está en serviceAccountKey, se obtiene de Firebase Console
                        # Por ahora usamos la pasada como parámetro o variable de entorno
                        pass
                except Exception:
                    pass

            # Intentar obtener API key de variable de entorno
            if not api_key:
                api_key = os.environ.get('FIREBASE_API_KEY')

            if not os.path.exists(service_account_path):
                logger.warning("No se encontró service account en %s", service_account_path)
                return cls()

            if not firebase_admin._apps:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase inicializado correctamente")
            
            db = firestore.client()
            
            # Crear instancias de operaciones
            auth_ops = AuthOperations(db=db, auth_module=auth, api_key=api_key)
            store_ops = StoreOperations(db=db)
            staff_ops = StaffOperations(db=db)
            product_ops = ProductOperations(db=db)
            sales_ops = SalesOperations(db=db)
            metrics_ops = MetricsOperations(db=db)
            
            return cls(auth_ops, store_ops, staff_ops, product_ops, sales_ops, metrics_ops)
        except Exception as e:
            logger.exception("Error inicializando Firebase: %s", e)
            return cls()

    # === Delegación a módulos de autenticación ===
    def create_account(self, email, password):
        return self._auth.create_account(email, password)

    def verify_credentials(self, email, password):
        return self._auth.verify_credentials(email, password)

    def save_owner_data(self, user_id, owner_data):
        return self._auth.save_owner_data(user_id, owner_data)

    def get_owner_data(self, user_id):
        return self._auth.get_owner_data(user_id)

    # === Delegación a módulos de tiendas ===
    def create_store(self, store_info, owner_id):
        return self._stores.create_store(store_info, owner_id)

    def get_user_stores(self, user_id):
        return self._stores.get_user_stores(user_id)

    def verify_owner(self, user_id, store_id):
        return self._stores.verify_owner(user_id, store_id)

    # === Delegación a módulos de empleados ===
    def add_store_staff(self, store_id, staff_data):
        return self._staff.add_store_staff(store_id, staff_data)

    def get_store_staff(self, store_id):
        return self._staff.get_store_staff(store_id)

    def update_store_staff(self, store_id, staff_id, updates: dict):
        return self._staff.update_store_staff(store_id, staff_id, updates)

    def delete_store_staff(self, store_id, staff_id):
        return self._staff.delete_store_staff(store_id, staff_id)

    # === Delegación a módulos de productos ===
    def create_product(self, store_id, product_data: dict):
        return self._products.create_product(store_id, product_data)

    def get_store_products(self, store_id):
        return self._products.get_store_products(store_id)

    def update_product(self, store_id, product_id, updates: dict):
        return self._products.update_product(store_id, product_id, updates)

    def delete_product(self, store_id, product_id):
        return self._products.delete_product(store_id, product_id)

    # === Delegación a módulos de ventas ===
    def record_sale(self, store_id, sale_data: dict):
        return self._sales.record_sale(store_id, sale_data)

    def get_store_sales(self, store_id, limit=100):
        return self._sales.get_store_sales(store_id, limit)

    def get_sales_by_period(self, store_id, start_date, end_date):
        return self._sales.get_sales_by_period(store_id, start_date, end_date)

    def delete_sale(self, sale_id):
        return self._sales.delete_sale(sale_id)

    # === Delegación a módulos de métricas ===
    def record_metric(self, store_id, metric_data: dict):
        return self._metrics.record_metric(store_id, metric_data)

    def get_store_metrics(self, store_id, metric_type=None, limit=50):
        return self._metrics.get_store_metrics(store_id, metric_type, limit)

    def calculate_revenue(self, sales_list):
        return self._metrics.calculate_revenue(sales_list)

    def calculate_sales_count(self, sales_list):
        return self._metrics.calculate_sales_count(sales_list)

    def get_top_products(self, sales_list, limit=5):
        return self._metrics.get_top_products(sales_list, limit)

    def delete_metric(self, metric_id):
        return self._metrics.delete_metric(metric_id)
