import re
from functools import wraps

class SecurityManager:
    def __init__(self):
        self.password_min_length = 8
        self.password_requirements = {
            'uppercase': r'[A-Z]',
            'lowercase': r'[a-z]',
            'numbers': r'[0-9]',
            'special': r'[!@#$%^&*(),.?":{}|<>-]'
        }

    def validar_email(self, email):
        """
        Valida el formato del email
        """
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron_email, email))

    def validar_password(self, password):
        """
        Valida que la contraseña cumpla con los requisitos mínimos de seguridad
        """
        if len(password) < self.password_min_length:
            return False

        # Verificar que la contraseña cumple con todos los requisitos
        for patron in self.password_requirements.values():
            if not re.search(patron, password):
                return False

        return True

    def sanitizar_input(self, texto):
        """
        Sanitiza el input para prevenir inyecciones
        """
        if not texto:
            return ""
        
        # Eliminar caracteres potencialmente peligrosos
        texto = re.sub(r'[<>"\';]', '', texto)
        return texto

def requiere_autenticacion(f):
    """
    Decorador para requerir autenticación en rutas protegidas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from .sessionmanager import SessionManager
        session_manager = SessionManager()
        
        # Obtener el session_id (en una aplicación web real vendría del header o cookie)
        session_id = kwargs.get('session_id')
        
        if not session_id:
            return {"success": False, "error": "Se requiere autenticación"}
        
        # Verificar la sesión
        session = session_manager.verificar_sesion(session_id)
        if not session["success"]:
            return {"success": False, "error": "Sesión inválida o expirada"}
        
        # Agregar la información del usuario a los kwargs
        kwargs['user_id'] = session["user_id"]
        kwargs['rol'] = session["rol"]
        
        return f(*args, **kwargs)
    return decorated_function

def requiere_rol(roles_permitidos):
    """
    Decorador para requerir roles específicos en rutas protegidas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rol_usuario = kwargs.get('rol')
            
            if not rol_usuario or rol_usuario not in roles_permitidos:
                return {"success": False, "error": "No tiene permisos suficientes"}
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
