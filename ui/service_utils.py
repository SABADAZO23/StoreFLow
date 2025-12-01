"""Utilidades para servicios."""


def get_service_instance(fallback_to_stub: bool = True):
    """Obtiene una instancia del servicio (real o stub).
    
    Args:
        fallback_to_stub: Si True, intenta el servicio real y cae back a stub
        
    Returns:
        Instancia del servicio
    """
    if not fallback_to_stub:
        from services.stub_service import StubService
        return StubService()

    try:
        from gestionar_tienda import GestorTiendasService
        try:
            return GestorTiendasService()
        except Exception:
            pass
    except Exception:
        pass

    from services.stub_service import StubService
    return StubService()
