import logging
from autenticacion.autenticacion import Autenticacion
from gestionar_tienda import GestorTiendasCLI, GestorTiendasService
from base_datos.firebase_client import FirebaseClient
from getpass import getpass
import os
import threading
from ui.app import run_app

# Configurar logging básico para la aplicación (INFO para ver mensajes de usuario)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def inicializar_firebase_client():
    """Crea un FirebaseClient inicializado desde service account (si existe).

    Retorna una instancia de FirebaseClient (puede estar en modo degradado si no hay credenciales).
    """
    service_account_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "configuracion",
        "serviceAccountKey.json"
    )
    # Obtener API key de variable de entorno (opcional)
    api_key = os.environ.get('FIREBASE_API_KEY')
    # La fábrica maneja la ausencia del archivo y devuelve un cliente sin db si hace falta
    return FirebaseClient.from_service_account(service_account_path, api_key=api_key)

def menu_principal(auth: Autenticacion, fb_client: FirebaseClient, servicio_tiendas: GestorTiendasService):
    session_id = None

    while True:
        logger.info("\n=== Menú Principal ===")
        logger.info("1. Registrar")
        logger.info("2. Iniciar sesión")
        logger.info("3. Ver datos de sesión")
        logger.info("4. Cerrar sesión")
        logger.info("5. Gestión de Tiendas")
        logger.info("6. Salir")

        opcion = input("Seleccione una opción (1-6): ")

        if opcion == "1":
            logger.info("\n--- Registro ---")
            email = input("Email: ")
            nombre = input("Nombre completo: ")
            mostrar = input("¿Desea mostrar la contraseña mientras la escribe? (s/n): ").lower()
            password = input("Contraseña: ") if mostrar == "s" else getpass("Contraseña (oculta): ")

            result = auth.registrar_cuenta(email, password, nombre)
            if result["success"]:
                logger.info("Cuenta creada. ID: %s", result['user_id'])
                session_id = result["session_id"]
            else:
                logger.error("Error: %s", result['error'])

        elif opcion == "2":
            logger.info("\n--- Login ---")
            email = input("Email: ")
            mostrar = input("¿Desea mostrar la contraseña mientras la escribe? (s/n): ").lower()
            password = input("Contraseña: ") if mostrar == "s" else getpass("Contraseña (oculta): ")

            result = auth.login(email, password)
            if result["success"]:
                logger.info("Login exitoso. Bienvenido %s", result['datos_usuario']['nombre'])
                session_id = result["session_id"]

                # Reusar el servicio de tiendas compartido y actualizar el usuario actual
                try:
                    servicio_tiendas.set_current_user(result["user_id"])
                except Exception:
                    pass
                tiendas_cli = GestorTiendasCLI(servicio_tiendas)
                tiendas_cli.menu()
            else:
                logger.error("Error: %s", result['error'])

        elif opcion == "3":
            if not session_id:
                logger.warning("No hay sesión activa.")
            else:
                datos = auth.get_datos_sesion(session_id)
                if datos["success"]:
                    user_data = datos['datos_usuario']
                    logger.info("Usuario: %s | Email: %s | Rol: %s", user_data.get('nombre'), user_data.get('email'), user_data.get('rol'))
                    logger.info("User ID: %s", datos['user_id'])
                else:
                    logger.error("Error: %s", datos['error'])

        elif opcion == "4":
            if not session_id:
                logger.warning("No hay sesión activa.")
            else:
                result = auth.logout(session_id)
                if result["success"]:
                    logger.info("Sesión cerrada correctamente.")
                    session_id = None
                    # clear shared service current user so UI updates
                    try:
                        servicio_tiendas.set_current_user(None)
                    except Exception:
                        pass
                else:
                    logger.error("Error: %s", result['error'])

        elif opcion == "5":
            if not session_id:
                logger.error("Debe iniciar sesión primero para acceder a la gestión de tiendas.")
            else:
                # Verificar la sesión primero
                datos_sesion = auth.get_datos_sesion(session_id)
                if datos_sesion["success"]:
                    # Reusar el servicio compartido
                    try:
                        servicio_tiendas.set_current_user(datos_sesion["user_id"])
                    except Exception:
                        pass
                    tiendas_cli = GestorTiendasCLI(servicio_tiendas)
                    tiendas_cli.menu()
                else:
                    logger.error("Sesión inválida. Por favor, inicie sesión nuevamente.")

        elif opcion == "6":
            logger.info("Hasta luego")
            break
            
        else:
            logger.error("Opción no válida: %s", opcion)

        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    # Inicializar el cliente Firebase y pasarlo a los servicios que lo necesiten
    fb_client = inicializar_firebase_client()
    # Inyectamos el cliente en Autenticacion para que use la misma instancia
    auth = Autenticacion(firebase_client=fb_client)
    # Crear el servicio de tiendas compartido y lanzar el menú principal en un hilo separado
    servicio_tiendas = GestorTiendasService(fb_client)
    # Lanzar el menú principal en un hilo separado y la interfaz gráfica en el hilo principal.
    # El hilo del menú será daemon para que al cerrar la UI el proceso finalice.
    menu_thread = threading.Thread(target=menu_principal, args=(auth, fb_client, servicio_tiendas), daemon=True)
    menu_thread.start()

    # Arrancar la UI en el hilo principal usando el mismo servicio compartido y auth
    try:
        run_app(service=servicio_tiendas, auth=auth)
    except Exception:
        # Si la UI falla por cualquier razón, mantenemos el hilo del menú para que siga funcionando
        menu_thread.join()