from tools.integration_test import FakeFirebaseClient
from gestionar_tienda import GestorTiendasService


def test_manager_permissions():
    fake = FakeFirebaseClient()
    svc = GestorTiendasService(fake)

    # Owner creates account and store
    owner = fake.create_account('owner@test', 'pw')
    owner_id = owner['user_id']
    svc.set_current_user(owner_id)
    res = svc.create_store({'name': 'Tienda Test', 'address': 'Dir 1'}, owner_id=owner_id)
    assert res.get('success')
    store_id = res.get('store_id')

    # Owner selects store and adds employee linked to user_id
    svc.set_current_store(store_id)
    emp = fake.create_account('emp@test', 'pw')
    emp_id = emp['user_id']
    add = svc.add_store_staff(store_id, {'name': 'Bob', 'role': 'manager', 'user_id': emp_id})
    assert add.get('success')

    # Now employee should have manager permissions
    assert svc.has_permission(emp_id, store_id, 'products.create')
    assert svc.has_permission(emp_id, store_id, 'products.update')
    assert svc.has_permission(emp_id, store_id, 'products.delete')
    assert svc.has_permission(emp_id, store_id, 'products.view')
