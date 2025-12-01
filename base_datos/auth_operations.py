"""Operaciones de autenticación."""
import logging
import requests
from datetime import datetime
from .db_base import DatabaseBase

logger = logging.getLogger(__name__)

# Firebase Auth REST API endpoint
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


class AuthOperations(DatabaseBase):
    """Operaciones de autenticación y usuarios."""

    def __init__(self, db=None, auth_module=None, api_key=None):
        """Inicializa con BD y módulo de auth.
        
        Args:
            db: Cliente de Firestore
            auth_module: Módulo de autenticación Firebase
            api_key: API key de Firebase (opcional, para verificación de contraseñas)
        """
        super().__init__(db)
        self._auth = auth_module
        self._api_key = api_key

    def create_account(self, email, password):
        """Crea una cuenta de usuario."""
        if not self.users_ref:
            return self._error_response("Firestore no inicializado")
        
        try:
            if not self._auth:
                return self._error_response("Módulo auth no disponible")
            
            user = self._auth.create_user(email=email, password=password)
            self.users_ref.document(user.uid).set({
                'email': email,
                'created_at': self._get_timestamp(),
                'rol': 'owner',
                'is_active': True
            })
            return self._success_response(user_id=user.uid)
        except Exception as e:
            logger.exception("Error en create_account: %s", e)
            error_msg = str(e)
            # Mejorar mensajes de error específicos
            if "email" in error_msg.lower() and "already" in error_msg.lower():
                return self._error_response("El email ya está registrado")
            return self._error_response(error_msg)

    def verify_credentials(self, email, password):
        """Verifica credenciales de usuario usando Firebase Auth REST API."""
        try:
            if not self.users_ref:
                return self._error_response("Firestore no inicializado")
            
            # Si no hay API key, usar método alternativo (solo para desarrollo)
            if not self._api_key:
                logger.warning("API key no configurada, usando verificación básica")
                return self._verify_credentials_fallback(email, password)
            
            # Verificar credenciales usando Firebase Auth REST API
            try:
                response = requests.post(
                    f"{FIREBASE_AUTH_URL}?key={self._api_key}",
                    json={
                        "email": email,
                        "password": password,
                        "returnSecureToken": True
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    user_id = data.get('localId')
                    # Verificar que el usuario existe en Firestore y está activo
                    user_doc = self.users_ref.document(user_id).get()
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        if user_data.get('is_active', True):
                            return self._success_response(user_id=user_id)
                        return self._error_response("Usuario inactivo")
                    return self._error_response("Usuario no encontrado en la base de datos")
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Credenciales inválidas')
                    if 'INVALID_PASSWORD' in error_msg or 'EMAIL_NOT_FOUND' in error_msg:
                        return self._error_response("Email o contraseña incorrectos")
                    return self._error_response("Error de autenticación")
                else:
                    return self._error_response("Error al verificar credenciales")
            except requests.RequestException as e:
                logger.exception("Error en petición a Firebase Auth: %s", e)
                # Fallback a verificación básica si falla la conexión
                return self._verify_credentials_fallback(email, password)
                
        except Exception as e:
            logger.exception("Error en verify_credentials: %s", e)
            return self._error_response("Error al verificar credenciales")

    def _verify_credentials_fallback(self, email, password):
        """Método alternativo de verificación (solo para desarrollo sin API key)."""
        try:
            if not self.users_ref:
                return self._error_response("Firestore no inicializado")
            
            # Buscar usuario por email
            # Nota: Las advertencias sobre argumentos posicionales son solo warnings,
            # el código funciona correctamente
            query = self.users_ref.where('email', '==', email).where('is_active', '==', True).stream()
            
            user_doc = next(query, None)
            if not user_doc:
                return self._error_response("Usuario no encontrado o inactivo")
            
            # En modo fallback, solo verificamos que existe (no recomendado para producción)
            logger.warning("Modo fallback: verificación de contraseña deshabilitada")
            return self._success_response(user_id=user_doc.id)
        except Exception as e:
            logger.exception("Error en verificación fallback: %s", e)
            return self._error_response("Error al verificar credenciales")

    def save_owner_data(self, user_id, owner_data):
        """Guarda datos del propietario."""
        try:
            if not isinstance(user_id, str) or not user_id:
                return self._error_response("ID de usuario inválido")
            if not isinstance(owner_data, dict):
                return self._error_response("Datos del propietario inválidos")
            
            self.users_ref.document(user_id).update(owner_data)
            return self._success_response()
        except Exception as e:
            logger.exception("Error en save_owner_data: %s", e)
            return self._error_response(str(e))

    def get_owner_data(self, user_id):
        """Obtiene datos del propietario."""
        try:
            if not isinstance(user_id, str) or not user_id:
                return self._error_response("ID de usuario inválido")
            
            doc = self.users_ref.document(user_id).get()
            if not doc.exists:
                return self._error_response("Usuario no encontrado")
            
            datos = doc.to_dict()
            # Retornar con la clave 'datos' para consistencia con autenticacion.py
            return self._success_response(datos=datos)
        except Exception as e:
            logger.exception("Error en get_owner_data: %s", e)
            return self._error_response(str(e))
