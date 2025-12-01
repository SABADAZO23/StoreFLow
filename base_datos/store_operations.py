"""Operaciones de tiendas."""
import logging
from datetime import datetime
from .db_base import DatabaseBase

logger = logging.getLogger(__name__)


class StoreOperations(DatabaseBase):
    """Operaciones CRUD de tiendas."""

    def create_store(self, store_info, owner_id):
        """Crea una tienda."""
        try:
            if not isinstance(store_info, dict):
                return self._error_response("Datos de tienda inválidos")
            
            if not owner_id:
                return self._error_response("ID de propietario requerido")
            
            required_keys = ['name', 'address']
            for key in required_keys:
                if key not in store_info:
                    return self._error_response(f"Falta {key}")

            name = store_info['name'].strip()
            address = store_info['address'].strip()
            phone = store_info.get('phone', '').strip()

            if not name or not address:
                return self._error_response("Nombre y dirección son requeridos")
            
            if len(name) < 2:
                return self._error_response("El nombre de la tienda debe tener al menos 2 caracteres")

            if not self.stores_ref:
                return self._error_response("Firestore no inicializado")

            owner_id_str = str(owner_id.get('user_id') if isinstance(owner_id, dict) else owner_id)
            
            if not owner_id_str:
                return self._error_response("ID de propietario inválido")

            store_data = {
                'name': name,
                'address': address,
                'phone': phone,
                'owner_id': owner_id_str,
                'created_at': self._get_timestamp(),
                'is_active': True,
                'employees': []
            }

            doc_ref = self.stores_ref.document()
            doc_ref.set(store_data)
            store_id = doc_ref.id

            # Asociar con usuario
            try:
                user_ref = self.users_ref.document(owner_id_str)
                user_doc = user_ref.get()
                if user_doc.exists:
                    owned = user_doc.to_dict().get('owned_stores', []) or []
                    if store_id not in owned:
                        owned.append(store_id)
                        user_ref.update({'owned_stores': owned})
                else:
                    user_ref.set({
                        'owned_stores': [store_id],
                        'created_at': self._get_timestamp()
                    })
            except Exception:
                logger.exception("Advertencia al asociar tienda con usuario")

            return self._success_response(store_id=store_id)
        except Exception as e:
            logger.exception("Error en create_store: %s", e)
            return self._error_response(str(e))

    def get_user_stores(self, user_id):
        """Obtiene tiendas del usuario."""
        try:
            if not user_id:
                return self._error_response("ID de usuario requerido")
            
            if isinstance(user_id, dict):
                user_id = user_id.get("user_id", "")
            else:
                user_id = str(user_id)
            
            if not user_id:
                return self._error_response("ID de usuario inválido")

            if not self.users_ref:
                return self._error_response("Firestore no inicializado")
            
            user_doc = self.users_ref.document(user_id).get()
            if not user_doc.exists:
                return self._error_response("Usuario no encontrado")

            user_data = user_doc.to_dict()
            stores = []

            if 'owned_stores' in user_data:
                for store_id in user_data['owned_stores']:
                    store_doc = self.stores_ref.document(store_id).get()
                    if store_doc.exists:
                        data = store_doc.to_dict()
                        data['id'] = store_id
                        stores.append(data)

            return self._success_response(stores=stores)
        except Exception as e:
            logger.exception("Error en get_user_stores: %s", e)
            return self._error_response(str(e))

    def verify_owner(self, user_id, store_id):
        """Verifica si el usuario es propietario de la tienda."""
        try:
            if not user_id or not store_id:
                return self._error_response("ID de usuario y tienda requeridos")
            
            if not self.stores_ref:
                return self._error_response("Firestore no inicializado")
            
            store = self.stores_ref.document(str(store_id)).get()
            if not store.exists:
                return self._error_response("Tienda no encontrada")
            
            owner = store.to_dict().get('owner_id')
            is_owner = str(user_id) == str(owner)
            return self._success_response(is_owner=is_owner)
        except Exception as e:
            logger.exception("Error en verify_owner: %s", e)
            return self._error_response(str(e))
