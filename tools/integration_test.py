"""In-memory integration test that simulates owner and employee flows without Firebase.

This test uses a FakeFirebaseClient that mimics the interface used by the service.
It verifies:
- owner creates account and store
- owner sets active store and adds an employee (with user_id)
- employee logs in (simulated) and can create/update/delete products according to role
"""
import os
import sys
# ensure package root is on sys.path so imports like 'gestionar_tienda' resolve
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from gestionar_tienda import GestorTiendasService
from base_datos.firebase_client import FirebaseClient
import uuid
import json


class FakeFirebaseClient:
    def __init__(self):
        self.users = {}
        self.stores = {}

    # --- Users ---
    def create_account(self, email, password):
        user_id = 'u-' + uuid.uuid4().hex[:8]
        self.users[user_id] = {'email': email, 'rol': 'owner', 'owned_stores': []}
        return {'success': True, 'user_id': user_id}

    def verify_credentials(self, email, password):
        for uid, u in self.users.items():
            if u.get('email') == email:
                return {'success': True, 'user_id': uid}
        return {'success': False, 'error': 'Usuario no encontrado'}

    def save_owner_data(self, user_id, owner_data):
        if user_id in self.users:
            self.users[user_id].update(owner_data)
            return {'success': True}
        return {'success': False, 'error': 'No existe usuario'}

    def get_owner_data(self, user_id):
        u = self.users.get(user_id)
        if not u:
            return {'success': False, 'error': 'Usuario no encontrado'}
        return {'success': True, 'datos': u}

    # --- Stores ---
    def create_store(self, store_info, owner_id):
        sid = 's-' + uuid.uuid4().hex[:8]
        store = dict(store_info)
        store.update({'owner_id': owner_id, 'created_at': 'now', 'employees': [], 'products': {}})
        self.stores[sid] = store
        # link to user
        if owner_id in self.users:
            self.users[owner_id].setdefault('owned_stores', []).append(sid)
        return {'success': True, 'store_id': sid}

    def verify_owner(self, user_id, store_id):
        st = self.stores.get(store_id)
        if not st:
            return {'success': False, 'error': 'Tienda no encontrada'}
        return {'success': True, 'is_owner': str(st.get('owner_id')) == str(user_id)}

    def add_store_staff(self, store_id, staff_data):
        st = self.stores.get(store_id)
        if not st:
            return {'success': False, 'error': 'Tienda no encontrada'}
        staff_id = 'st-' + uuid.uuid4().hex[:8]
        entry = dict(staff_data)
        entry['id'] = staff_id
        st.setdefault('employees', []).append(entry)
        return {'success': True, 'staff_id': staff_id}

    def get_store_staff(self, store_id):
        st = self.stores.get(store_id)
        if not st:
            return {'success': False, 'error': 'Tienda no encontrada'}
        return {'success': True, 'staff': list(st.get('employees', []))}

    # --- Products ---
    def create_product(self, store_id, product_data):
        st = self.stores.get(store_id)
        if not st:
            return {'success': False, 'error': 'Tienda no encontrada'}
        pid = 'p-' + uuid.uuid4().hex[:8]
        st['products'][pid] = dict(product_data)
        st['products'][pid]['id'] = pid
        return {'success': True, 'product_id': pid}

    def get_store_products(self, store_id):
        st = self.stores.get(store_id)
        if not st:
            return {'success': False, 'error': 'Tienda no encontrada'}
        return {'success': True, 'products': list(st.get('products', {}).values())}

    def update_product(self, store_id, product_id, updates):
        st = self.stores.get(store_id)
        if not st or product_id not in st.get('products', {}):
            return {'success': False, 'error': 'Producto no encontrado'}
        st['products'][product_id].update(updates)
        return {'success': True}

    def delete_product(self, store_id, product_id):
        st = self.stores.get(store_id)
        if not st or product_id not in st.get('products', {}):
            return {'success': False, 'error': 'Producto no encontrado'}
        del st['products'][product_id]
        return {'success': True}


def run():
    print('Starting in-memory integration test')
    fake = FakeFirebaseClient()
    svc = GestorTiendasService(fake)

    # Owner registers
    owner = fake.create_account('owner@example.com', 'password')
    assert owner['success']
    owner_id = owner['user_id']
    print('Owner id:', owner_id)

    svc.set_current_user(owner_id)

    # Owner creates store
    r = svc.create_store({'name': 'Tienda X', 'address': 'Calle 1'}, owner_id=owner_id)
    assert r['success']
    store_id = r['store_id']
    print('Store created:', store_id)

    # Select active store
    svc.set_current_store(store_id)

    # Owner adds employee with user_id
    # First create an employee user
    emp = fake.create_account('emp@example.com', 'pw')
    emp_id = emp['user_id']
    # Add staff entry linking to user_id
    add = svc.add_store_staff(store_id, {'name': 'Alice', 'role': 'manager', 'user_id': emp_id})
    assert add['success']
    staff_id = add['staff_id']
    print('Added staff:', staff_id, 'linked user:', emp_id)

    # Now simulate employee session
    svc.set_current_user(emp_id)
    # Employee should have permission to create products (manager)
    p = svc.create_product(store_id, {'name': 'Prod A', 'price': '10.00', 'stock': '5'})
    print('Employee create product result:', p)
    assert p.get('success')
    pid = p.get('product_id')

    # List products
    lst = svc.get_store_products(store_id)
    print('Products after create:', json.dumps(lst, ensure_ascii=False))

    # Update product
    up = svc.update_product(store_id, pid, {'price': '12.00'})
    print('Update result:', up)
    assert up.get('success')

    # Delete product
    de = svc.delete_product(store_id, pid)
    print('Delete result:', de)
    assert de.get('success')

    print('Integration test completed successfully')


if __name__ == '__main__':
    run()
