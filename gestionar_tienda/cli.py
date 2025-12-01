"""Adaptador de consola que realiza I/O y llama al servicio puro."""
import logging
from .service import GestorTiendasService
from .cli_stores import StoreCLIMixin
from .cli_staff import StaffCLIMixin
from .cli_products import ProductCLIMixin

logger = logging.getLogger(__name__)


class GestorTiendasCLI(StoreCLIMixin, StaffCLIMixin, ProductCLIMixin):
    """Adaptador de consola que realiza I/O y llama al servicio puro."""
    
    def __init__(self, service: GestorTiendasService):
        self.service = service

    def crear_cuenta(self):
        """Crea una nueva cuenta de usuario."""
        logger.info("\n=== Crear Nueva Cuenta ===")
        email = input("Email: ")
        password = input("Contraseña: ")

        # crear cuenta a través del servicio de Firebase
        result = self.service.firebase.create_account(email, password)
        if result.get("success"):
            logger.info("\nCuenta creada exitosamente")
            self.service.set_current_user(result["user_id"])
            return True
        else:
            logger.error("Error al crear cuenta: %s", result.get('error'))
            return False

    def prueba_rapida(self):
        """Método de prueba rápida para crear una tienda."""
        user_id = self.service.current_user
        if not user_id:
            logger.warning("No hay usuario logueado. Inicie sesión primero.")
            return
        logger.info("=== PRUEBA RÁPIDA ===")
        test_data = {"name": "Tienda de Prueba", "address": "Calle Test 123", "phone": "123456789"}
        result = self.service.create_store(test_data, owner_id=user_id)
        logger.info("Resultado prueba rápida: %s", result)

    def prueba_extra_simple(self):
        """Método de prueba extra simple para crear una tienda."""
        user_id = self.service.current_user
        if not user_id:
            logger.warning("No hay usuario logueado. Inicie sesión primero.")
            return
        logger.info("=== PRUEBA EXTRA SIMPLE ===")
        test_data = {"name": "Mi Tienda", "address": "Mi Dirección", "phone": "123456789"}
        result = self.service.create_store(store_info=test_data, owner_id=user_id)
        logger.info("Resultado prueba extra simple: %s", result)

    def menu(self):
        """Menú principal de la interfaz CLI."""
        while True:
            logger.info("\n=== Gestión de Tiendas ===")
            logger.info("1. Crear cuenta")
            logger.info("2. Registrar nueva tienda")
            logger.info("3. Seleccionar tienda activa")
            logger.info("4. Agregar empleado a tienda")
            logger.info("5. Listar empleados")
            logger.info("6. Actualizar empleado")
            logger.info("7. Eliminar empleado")
            logger.info("8. Listar productos")
            logger.info("9. Crear producto")
            logger.info("10. Actualizar producto")
            logger.info("11. Eliminar producto")
            logger.info("12. Ver mis tiendas")
            logger.info("13. Salir")

            opcion = input("\nSeleccione una opción (1-13): ")

            if opcion == "1":
                self.crear_cuenta()
            elif opcion == "2":
                self.registrar_tienda()
            elif opcion == "3":
                self.seleccionar_tienda_activa()
            elif opcion == "4":
                self.agregar_empleado()
            elif opcion == "5":
                self.listar_empleados()
            elif opcion == "6":
                self.actualizar_empleado()
            elif opcion == "7":
                self.eliminar_empleado()
            elif opcion == "8":
                self.listar_productos()
            elif opcion == "9":
                self.crear_producto()
            elif opcion == "10":
                self.actualizar_producto()
            elif opcion == "11":
                self.eliminar_producto()
            elif opcion == "12":
                self.ver_mis_tiendas()
            elif opcion == "13":
                logger.info("Hasta luego")
                break
            else:
                logger.error("Opción no válida: %s", opcion)

            input("\nPresione Enter para continuar...")

