"""Métodos CLI relacionados con gestión de empleados."""
import logging

logger = logging.getLogger(__name__)


class StaffCLIMixin:
    """Mixin con métodos CLI para gestión de empleados."""

    def _get_store_id(self, prompt: str = "ID de la tienda (Enter = tienda activa): "):
        """Helper para obtener store_id con soporte para tienda activa."""
        store_id = input(prompt)
        if not store_id.strip():
            store_id = self.service.current_store
            if not store_id:
                logger.warning("No hay tienda activa. Seleccione la tienda o indique un ID.")
                return None
        else:
            self.service.set_current_store(store_id.strip())
            store_id = self.service.current_store
        return store_id

    def agregar_empleado(self):
        """Agrega un nuevo empleado a una tienda."""
        user_id = self.service.current_user
        if not user_id:
            logger.warning("No hay usuario logueado. Inicie sesión primero.")
            return
        logger.info("Agregar Perfil de Empleado")
        store_id = input("ID de la tienda: ")

        staff_data = {
            "name": input("Nombre del empleado: "),
            "role": input("Rol (cajero/vendedor/gerente): "),
            "pin": input("PIN de acceso (4 dígitos): ")
        }

        result = self.service.add_store_staff(store_id, staff_data)
        if result.get("success"):
            logger.info("Empleado agregado exitosamente — ID: %s", result.get('staff_id'))
        else:
            logger.error("Error al agregar empleado: %s", result.get('error', 'Error desconocido'))

    def listar_empleados(self):
        """Lista empleados de una tienda."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        res = self.service.get_store_staff(store_id)
        if not res.get('success'):
            logger.error("Error obteniendo empleados: %s", res.get('error', 'Error desconocido'))
            return
        staff = res.get('staff', [])
        if not staff:
            logger.info("No hay empleados registrados")
            return
        logger.info("=== Empleados ===")
        for s in staff:
            logger.info("ID: %s - %s (%s)", s.get('id'), s.get('name'), s.get('role'))

    def actualizar_empleado(self):
        """Actualiza datos de un empleado."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        staff_id = input("ID del empleado: ")
        logger.info("Ingrese los campos a actualizar (dejar vacío para omitir):")
        name = input("Nombre: ")
        role = input("Rol: ")
        updates = {}
        if name.strip():
            updates['name'] = name.strip()
        if role.strip():
            updates['role'] = role.strip()

        if not updates:
            logger.info("Nada para actualizar")
            return

        res = self.service.update_employee(store_id, staff_id, updates)
        if res.get('success'):
            logger.info("Empleado actualizado")
        else:
            logger.error("Error al actualizar empleado: %s", res.get('error', 'Error desconocido'))

    def eliminar_empleado(self):
        """Elimina un empleado de una tienda."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        staff_id = input("ID del empleado: ")
        res = self.service.remove_employee(store_id, staff_id)
        if res.get('success'):
            logger.info("Empleado eliminado")
        else:
            logger.error("Error al eliminar empleado: %s", res.get('error', 'Error desconocido'))

