"""Módulo de gestión de permisos."""
from base_datos.firebase_client import FirebaseClient

# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    'owner': ['products.create', 'products.update', 'products.delete', 'products.view'],
    'manager': ['products.create', 'products.update', 'products.delete', 'products.view'],
    'seller': ['products.create', 'products.update', 'products.view'],
    'viewer': ['products.view']
}


def has_permission(firebase: FirebaseClient, user_id: str, store_id: str, action: str) -> bool:
    """Comprueba si `user_id` tiene permiso `action` sobre `store_id`.

    Reglas sencillas:
    - Si `user_id` es el owner (verify_owner) => True
    - En otro caso, buscar en staff de la tienda un documento con `user_id` y comprobar role->permissions mapping
    """
    try:
        # Owner check
        owner_check = firebase.verify_owner(user_id, store_id)
        if owner_check.get('success') and owner_check.get('is_owner'):
            return True

        # Obtener lista de staff y buscar user_id
        staff_res = firebase.get_store_staff(store_id)
        if not staff_res.get('success'):
            return False
        staff_list = staff_res.get('staff', [])
        
        for s in staff_list:
            # staff entries may store either 'user_id' or not; if not, skip
            if s.get('user_id') and str(s.get('user_id')) == str(user_id):
                role = s.get('role', '').lower()
                perms = ROLE_PERMISSIONS.get(role, [])
                return action in perms
        return False
    except Exception:
        return False

