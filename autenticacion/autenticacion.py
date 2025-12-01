import os
import sys
import re
from datetime import datetime, timedelta

# Agregar el directorio raíz al path de Python
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importaciones absolutas
from base_datos.firebase_client import FirebaseClient
from autenticacion.seguridad import SecurityManager
from .sessionmanager import SessionManager

class Autenticacion:
    def __init__(self, firebase_client: FirebaseClient = None):
        # Permitir inyección del cliente Firebase para pruebas o inicialización controlada
        self.firebase_client = firebase_client or FirebaseClient()
        self.security_manager = SecurityManager()
        self.session_manager = SessionManager()

    def registrar_cuenta(self, email, password, nombre):
        """
        Registra una nueva cuenta de dueño de tienda
        """
        # Validar el formato del email usando SecurityManager
        if not self.security_manager.validar_email(email):
            return {"success": False, "error": "Formato de email inválido"}
        
        # Validar la contraseña usando SecurityManager (requiere mayúscula, minúscula, número y carácter especial)
        if not self.security_manager.validar_password(password):
            return {"success": False, "error": "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial"}
        
        # Validar el nombre
        if not nombre or len(nombre.strip()) < 3:
            return {"success": False, "error": "El nombre debe tener al menos 3 caracteres"}

        # Crear cuenta en Firebase
        result = self.firebase_client.create_account(email, password)
        
        if result["success"]:
            # Guardar información adicional del dueño
            owner_data = {
                "nombre": nombre,
                "email": email,
                "fecha_registro": datetime.now().isoformat(),
                "rol": "owner"
            }
            
            # Guardar datos del dueño
            owner_result = self.firebase_client.save_owner_data(result["user_id"], owner_data)
            if not owner_result["success"]:
                return owner_result

            # Crear sesión
            session = self.session_manager.crear_sesion(
                user_id=result["user_id"],
                rol="owner"
            )
            
            if session["success"]:
                return {
                    "success": True,
                    "user_id": result["user_id"],
                    "session_id": session["session_id"],
                    "datos_usuario": owner_data
                }
        
        return result

    def login(self, email, password):
            """
            Inicia sesión de un usuario existente
            """
            # Verificar credenciales en Firebase
            result = self.firebase_client.verify_credentials(email, password)
        
            if not result["success"]:
                return {"success": False, "error": "Credenciales inválidas"}

            # Obtener datos del dueño
            owner_data = self.firebase_client.get_owner_data(result["user_id"])
            if not owner_data["success"]:
                return {"success": False, "error": "No se encontró la cuenta"}

            # Verificar que es una cuenta de dueño
            if owner_data["datos"]["rol"] != "owner":
                return {"success": False, "error": "Esta cuenta no es de dueño de tienda"}

            # Crear sesión
            session = self.session_manager.crear_sesion(
                user_id=result["user_id"],
                rol="owner"
            )

            if session["success"]:
                return {
                    "success": True,
                    "user_id": result["user_id"],
                    "session_id": session["session_id"],
                    "datos_usuario": owner_data["datos"]
                }
        
            return {"success": False, "error": "Error al crear la sesión"}

    def logout(self, session_id):
            """
            Cierra la sesión del usuario
            """
            # Verificar que la sesión existe y es válida
            verify = self.verificar_sesion(session_id)
            if not verify["success"]:
                return {"success": False, "error": "Sesión inválida"}

            # Cerrar la sesión
            return self.session_manager.cerrar_sesion(session_id)

    def verificar_sesion(self, session_id):
            """
            Verifica si una sesión es válida y retorna los datos del usuario
            """
            # Verificar la sesión
            result = self.session_manager.verificar_sesion(session_id)
            if not result["success"]:
                return result
        
            # Obtener datos actualizados del dueño
            owner_data = self.firebase_client.get_owner_data(result["user_id"])
            if not owner_data["success"]:
                return {"success": False, "error": "No se encontró la cuenta"}

            return {
                "success": True,
                "user_id": result["user_id"],
                "session_id": session_id,
                "datos_usuario": owner_data["datos"]
            }

    def get_datos_sesion(self, session_id):
        """
        Obtiene los datos completos de la sesión actual
        """
        return self.verificar_sesion(session_id)
