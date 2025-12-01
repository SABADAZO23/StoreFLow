"""Smoke test for basic imports and new product/employee methods.

Prints whether Firestore was initialized and exercises a few service methods
in a safe, non-destructive way.
"""
import json
import sys
from base_datos.firebase_client import FirebaseClient
from gestionar_tienda import GestorTiendasService


def main():
    print("Iniciando smoke test...")
    fc = FirebaseClient()
    print(f"Firestore cliente disponible: {fc.db is not None}")

    service = GestorTiendasService(fc)
    # Set a dummy current user (no real auth in this smoke test)
    service.set_current_user('test-user')

    # Try listing products for a non-existing store (should fail gracefully)
    try:
        res = service.get_store_products('test-store')
        print("get_store_products ->", json.dumps(res, default=str, ensure_ascii=False))
    except Exception as e:
        print("get_store_products raised:", str(e))

    # Try to create a product (will likely fail if Firestore not initialized or permission denied)
    try:
        prod = {'name': 'Prueba', 'price': '9.99', 'stock': '10'}
        res2 = service.create_product('test-store', prod)
        print("create_product ->", json.dumps(res2, default=str, ensure_ascii=False))
    except Exception as e:
        print("create_product raised:", str(e))

    print('Smoke test finalizado.')


if __name__ == '__main__':
    main()
