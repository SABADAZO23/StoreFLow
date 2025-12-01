"""Métodos CLI relacionados con gestión de productos."""
import logging

logger = logging.getLogger(__name__)


class ProductCLIMixin:
    """Mixin con métodos CLI para gestión de productos."""

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

    def listar_productos(self):
        """Lista productos de una tienda."""
        user_id = self.service.current_user
        if not user_id:
            logger.warning("No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        res = self.service.get_store_products(store_id)
        if not res.get('success'):
            logger.error("Error al listar productos: %s", res.get('error', 'Error desconocido'))
            return
        products = res.get('products', [])
        if not products:
            logger.info("No hay productos registrados")
            return
        logger.info("=== Productos ===")
        for p in products:
            logger.info("ID: %s - %s | Precio: %s | Stock: %s", 
                       p.get('id'), p.get('name'), p.get('price', ''), p.get('stock', ''))

    def crear_producto(self):
        """Crea un nuevo producto."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        logger.info("Ingrese datos del producto:")
        name = input("Nombre: ")
        price = input("Precio: ")
        stock = input("Stock: ")
        
        # Validar que precio sea numérico
        try:
            price_float = float(price.strip())
            if price_float < 0:
                logger.error("El precio no puede ser negativo")
                return
        except ValueError:
            logger.error("El precio debe ser un número válido")
            return
        
        # Validar que stock sea un entero positivo
        try:
            stock_int = int(stock.strip())
            if stock_int < 0:
                logger.error("El stock no puede ser negativo")
                return
        except ValueError:
            logger.error("El stock debe ser un número entero válido")
            return
        
        product_data = {'name': name.strip(), 'price': str(price_float), 'stock': str(stock_int)}
        res = self.service.create_product(store_id, product_data)
        if res.get('success'):
            logger.info("Producto creado: %s", res.get('product_id'))
        else:
            logger.error("Error al crear producto: %s", res.get('error', 'Error desconocido'))

    def actualizar_producto(self):
        """Actualiza datos de un producto."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        product_id = input("ID del producto: ")
        logger.info("Ingrese los campos a actualizar (dejar vacío para omitir):")
        name = input("Nombre: ")
        price = input("Precio: ")
        stock = input("Stock: ")
        updates = {}
        if name.strip():
            updates['name'] = name.strip()
        if price.strip():
            try:
                price_float = float(price.strip())
                if price_float < 0:
                    logger.error("El precio no puede ser negativo")
                    return
                updates['price'] = str(price_float)
            except ValueError:
                logger.error("El precio debe ser un número válido")
                return
        if stock.strip():
            try:
                stock_int = int(stock.strip())
                if stock_int < 0:
                    logger.error("El stock no puede ser negativo")
                    return
                updates['stock'] = str(stock_int)
            except ValueError:
                logger.error("El stock debe ser un número entero válido")
                return
        if not updates:
            logger.info("Nada para actualizar")
            return
        res = self.service.update_product(store_id, product_id, updates)
        if res.get('success'):
            logger.info("Producto actualizado")
        else:
            logger.error("Error al actualizar producto: %s", res.get('error', 'Error desconocido'))

    def eliminar_producto(self):
        """Elimina un producto."""
        user_id = self.service.current_user
        if not user_id:
            print("⚠️  No hay usuario logueado. Inicie sesión primero.")
            return

        store_id = self._get_store_id()
        if not store_id:
            return

        product_id = input("ID del producto: ")
        res = self.service.delete_product(store_id, product_id)
        if res.get('success'):
            logger.info("Producto eliminado")
        else:
            logger.error("Error al eliminar producto: %s", res.get('error', 'Error desconocido'))

