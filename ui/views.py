"""Gestor unificado de vistas."""
from ui.views_base import ViewBase
from ui.views_stores import StoreView
from ui.views_staff import StaffView
from ui.views_products import ProductView
from ui.views_management import ManagementView
from ui.views_sales import SalesView
from ui.views_metrics import MetricsView


class ViewManager(ViewBase):
    """Gestor centralizado de vistas que delega a submódulos."""

    def show_stores(self):
        """Muestra la vista de tiendas."""
        view = StoreView(self.main_window)
        view.show_stores()

    def show_staff(self):
        """Muestra la vista de empleados."""
        view = StaffView(self.main_window)
        view.show_staff()

    def show_products(self):
        """Muestra la vista de productos."""
        view = ProductView(self.main_window)
        view.show_products()

    def show_sales(self):
        """Muestra la vista de ventas."""
        view = SalesView(self.main_window)
        view.show_sales()

    def show_metrics(self):
        """Muestra la vista de métricas."""
        view = MetricsView(self.main_window)
        view.show_metrics()

    def show_full_management(self):
        """Muestra la vista de gestión completa."""
        view = ManagementView(self.main_window)
        view.show_full_management()

    def show_my_stores(self):
        """Muestra la vista de mis tiendas."""
        view = StoreView(self.main_window)
        view.show_my_stores()
