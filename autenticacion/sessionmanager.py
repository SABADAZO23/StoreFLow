import uuid
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}  # En una aplicación real, esto estaría en una base de datos

    def crear_sesion(self, user_id, rol, tienda_id=None):
        """
        Crea una nueva sesión para un usuario
        """
        session_id = str(uuid.uuid4())
        expiry_time = datetime.now() + timedelta(hours=24)  # La sesión expira en 24 horas
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "rol": rol,
            "tienda_id": tienda_id,
            "expiry_time": expiry_time
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "expiry_time": expiry_time
        }

    def verificar_sesion(self, session_id):
        """
        Verifica si una sesión es válida y no ha expirado
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Sesión no encontrada"}
        
        if datetime.now() > session["expiry_time"]:
            self.cerrar_sesion(session_id)
            return {"success": False, "error": "Sesión expirada"}
        
        return {"success": True, "user_id": session["user_id"], "rol": session["rol"]}

    def cerrar_sesion(self, session_id):
        """
        Cierra una sesión existente
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return {"success": True, "message": "Sesión cerrada correctamente"}
        return {"success": False, "error": "Sesión no encontrada"}

    def get_sesion(self, session_id):
        """
        Obtiene los detalles de una sesión
        """
        session = self.sessions.get(session_id)
        if session:
            return {"success": True, "user_id": session["user_id"], "rol": session["rol"]}
        return {"success": False, "error": "Sesión no encontrada"}

    def limpiar_sesiones_expiradas(self):
        """
        Limpia todas las sesiones expiradas
        """
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time > session["expiry_time"]
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
