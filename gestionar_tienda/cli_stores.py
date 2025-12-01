"""Métodos CLI relacionados con gestión de tiendas."""
import logging

logger = logging.getLogger(__name__)


class StoreCLIMixin:
    """Mixin con métodos CLI para gestión de tiendas."""

    def registrar_tienda(self):
        """Registra una nueva tienda."""
        user_id = self.service.current_user
        if not user_id:
            logger.warning("No hay usuario logueado. Inicie sesión primero.")
            return
        logger.info("Registrar Nueva Tienda")
        name = input("Nombre de la tienda: ")
        address = input("Dirección: ")
        phone = input("Teléfono: ")

        store_data = {"name": name, "address": address, "phone": phone}

        result = self.service.create_store(store_data, owner_id=user_id)
        if result.get("success"):
            logger.info("Tienda registrada exitosamente — ID: %s", result.get('store_id'))
            # Select the newly created store as active for convenience
            try:
                self.service.set_current_store(result.get('store_id'))
                logger.info("Tienda seleccionada como activa.")
            except Exception:
                pass
        else:
            logger.error("Error al registrar tienda: %s", result.get('error', 'Error desconocido'))

    def ver_mis_tiendas(self):
        """Muestra todas las tiendas del usuario."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        result = self.service.get_user_stores(user_id)
        if result.get("success"):
            stores = result.get("stores", [])
            if not stores:
                logger.info("No tienes tiendas registradas.")
                return

            logger.info("=== Mis Tiendas ===")
            for store in stores:
                logger.info("ID: %s", store.get('id'))
                logger.info("Nombre: %s", store.get('name'))
                logger.info("Dirección: %s", store.get('address'))
                logger.info("Teléfono: %s", store.get('phone'))

                staff_result = self.service.get_store_staff(store.get('id'))
                if staff_result.get("success") and staff_result.get("staff"):
                    logger.info("Empleados:")
                    for emp in staff_result["staff"]:
                        logger.info("- %s (%s)", emp.get('name'), emp.get('role'))
                else:
                    logger.info("Empleados: Ninguno registrado")
        else:
            logger.error("Error al recuperar tiendas: %s", result.get('error', 'Error desconocido'))

    def seleccionar_tienda_activa(self):
        """Lista las tiendas del usuario y permite seleccionar una como tienda activa."""
        user_id = self.service.current_user
        if not user_id:
            logger.warning("No hay usuario logueado. Inicie sesión primero.")
            return

        res = self.service.get_user_stores(user_id)
        if not res.get('success'):
            logger.error("Error obteniendo tiendas: %s", res.get('error', 'Error desconocido'))
            return

        stores = res.get('stores', [])
        if not stores:
            logger.info("No tienes tiendas registradas.")
            return

        logger.info("=== Seleccionar Tienda Activa ===")
        for idx, s in enumerate(stores, start=1):
            logger.info("%d. %s (ID: %s)", idx, s.get('name'), s.get('id'))
        logger.info("0. Cancelar")

        try:
            choice = int(input("Seleccione una tienda por número: "))
        except Exception:
            logger.error("Entrada inválida")
            return

        if choice == 0:
            logger.info("Operación cancelada")
            return

        if choice < 1 or choice > len(stores):
            logger.error("Número fuera de rango")
            return

        selected = stores[choice - 1]
        store_id = selected.get('id')
        self.service.set_current_store(store_id)
        logger.info("Tienda activa establecida: %s (ID: %s)", selected.get('name'), store_id)

