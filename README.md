# 🏪 APP Gestión de Tiendas

¡Hola! 👋

Esta es una aplicación para gestionar tiendas que hice para un proyecto de POO. Básicamente te permite manejar tiendas, empleados y productos desde una interfaz gráfica bonita o desde la consola (o ambas a la vez, porque sí, funciona así de cool 😎).

## ¿Qué hace esto?

Bueno, básicamente puedes:
- **Crear tu cuenta** de dueño de tienda (con validaciones de seguridad y todo eso)
- **Registrar tiendas** y elegir cuál está activa en cada momento
- **Gestionar empleados** - agregar, editar, eliminar (solo si eres el dueño, obvio)
- **Manejar productos** - crear, listar, actualizar y borrar según tus permisos

Todo esto funciona tanto desde la ventana gráfica como desde la consola, y están sincronizados. Si haces algo en uno, se refleja en el otro. ✨

## ¿Cómo lo uso?

### Paso 1: Instalar dependencias
Si es la primera vez que lo usas, abre una terminal en la carpeta del proyecto y ejecuta:
```powershell
pip install -r requirements.txt
```
(Si ya lo hiciste antes, puedes saltarte este paso)

### Paso 2: Ejecutar
Simplemente corre:
```powershell
python main.py
```

Y listo! Se abrirán **dos cosas a la vez**:
- Una ventana gráfica grande y bonita (1690x1900, para que veas todo cómodo)
- Un menú en la consola (por si prefieres el modo texto)

### Paso 3: Crear tu cuenta
Desde cualquiera de las dos interfaces:
1. Haz clic en "Registrar" (o opción 1 en la consola)
2. Llena el formulario:
   - Email válido
   - Tu nombre completo
   - Una contraseña segura (mínimo 8 caracteres, con mayúscula, minúscula, número y carácter especial - tipo `MiPass123!`)

### Paso 4: Iniciar sesión
Una vez que tengas tu cuenta, inicia sesión desde cualquiera de las dos interfaces.

### Paso 5: 
Ya dentro, puedes:
- Crear tiendas desde la interfaz gráfica o desde el menú de consola
- Seleccionar una tienda como "activa" (importante para algunas operaciones)
- Agregar empleados y productos
- Ver todo lo que tienes registrado

## Tips útiles 💡

- **¿No ves tiendas?** Asegúrate de seleccionar una tienda activa primero. Algunas acciones requieren que tengas una tienda seleccionada.
- **¿Quieres usar Firebase?** Pon tu archivo `serviceAccountKey.json` en la carpeta `configuracion/`. Si no lo tienes, no pasa nada - la app funciona igual, solo que sin persistencia real (los datos se mantienen mientras la app esté abierta).
- **Las ventanas emergentes** salen centradas y son grandes (150% más grandes que antes) para que se vean bien en la ventana principal.
- **Todo está sincronizado** - si haces algo en la consola, se refleja en la UI y viceversa.

## Características chéveres 🎨

- ✅ Interfaz gráfica completa con todas las funcionalidades de la consola
- ✅ Ventanas emergentes centradas y grandes (para que no tengas que forzar la vista)
- ✅ Validaciones de seguridad en contraseñas y emails
- ✅ Sistema de permisos por roles (owner, manager, seller, viewer)
- ✅ Modo degradado si no tienes Firebase configurado
- ✅ Sincronización en tiempo real entre UI y consola

## Estructura del proyecto

```
APP_GEStionmenumediofuncional/
├── main.py                 # Punto de entrada principal
├── gestionar_tienda.py    # Lógica de negocio y CLI
├── autenticacion/         # Módulo de autenticación
├── base_datos/            # Clientes de Firebase
├── ui/                    # Interfaz gráfica (Tkinter)
├── tests/                 # Tests de integración
└── tools/                 # Herramientas útiles
```

## ¿Problemas?

Si algo no funciona:
- **"No module named 'tkinter'"** → Reinstala Python desde python.org (tkinter viene incluido)
- **"Firestore no inicializado"** → Es normal si no tienes Firebase. La app funciona igual.
- **"No puedo iniciar sesión"** → Asegúrate de haber creado una cuenta primero.

## Casos de uso

1) Gestión de tiendas
- Cómo: Implementado en `StoreFlow/ui/views_stores.py` (listas, detalles, seleccionar tienda activa, crear/editar). El modelo de tiendas se persiste mediante los clientes en `base_datos/`.
- Por qué: Permite al tendero ver dónde están ubicadas sus sucursales, editar datos de contacto y seleccionar la tienda en la que opera actualmente.

2) Administración de productos (CRUD)
- Cómo: Implementado en `StoreFlow/ui/views_products.py` y los diálogos relacionados (`dialogs_*`). Las operaciones de persistencia pasan por los clientes en `base_datos/` (Firestore o fallback en memoria).
- Por qué: Necesario para llevar el catálogo — agregar, actualizar precios, cambiar stock y eliminar productos.

3) Registro y gestión de ventas
- Cómo: Implementado en `StoreFlow/ui/views_sales.py` con diálogo para registrar ventas y funciones para listar/eliminar ventas. Las operaciones de I/O se ejecutan en hilos en segundo plano para evitar bloquear la UI.
- Por qué: Permite al tendero registrar cada transacción y mantener un historial de ventas vinculadas a productos y tiendas.

4) Enriquecimiento de historial de ventas (product_name persistente)
- Cómo: Al registrar ventas se guarda `product_name` además de `product_id`; si faltaba, las vistas y el proceso de métricas intentan enriquecerlo cruzando con la lista de productos.
- Por qué: Garantiza que las ventas antiguas sigan siendo legibles aunque cambie el catálogo (mejor UX para revisar ventas previas).

5) Visualización de métricas comerciales
- Cómo: Implementado en `StoreFlow/ui/views_metrics.py`. Calcula ingresos totales, cantidad de ventas, promedio por venta y top productos usando utilidades de servicio (`calculate_revenue`, `get_top_products`, etc.). Si no hay datos muestra un modo demo con instrucciones.
- Por qué: Da al tendero una vista rápida de la salud del negocio y productos más vendidos — útil para decisiones de reposición y precio.

6) Autenticación y sesiones
- Cómo: Módulos en `autenticacion/` (`autenticacion.py`, `seguridad.py`, `sessionmanager.py`) proporcionan login, roles y gestión de sesión; el backend puede usar credenciales de Firebase cuando estén disponibles.
- Por qué: Control de acceso y separación de permisos (ej.: sólo administradores pueden modificar productos o personal).

7) Persistencia con fallback (resiliencia)
- Cómo: `base_datos/firebase_client.py` implementa un cliente para Firestore con manejo explícito de errores; el proyecto incluye un cliente fallback/in-memory que se usa cuando la conexión a Firebase falla.
- Por qué: Permite que la aplicación siga funcionando en modo local/offline sin perder la capacidad de probar y operar (útil en comercios con conectividad poco fiable).

8) Usabilidad y rendimiento (no se cuelga)
- Cómo: Operaciones de red y disco se ejecutan en hilos (`threading.Thread`) y las actualizaciones UI se realizan con `after` del mainloop; además la barra lateral es scrollable y los diálogos informan de estado.
- Por qué: Evita que la interfaz se congele durante cargas largas y mejora la experiencia de usuario en operaciones habituales.

9) Empaquetado / distribución
- Cómo: Scripts y configuración para PyInstaller están incluidos (build scripts). Se informó de un build local `dist/TiendaHub.exe` como ejemplo de empaquetado.
- Por qué: Facilita la entrega del sistema al tendero sin requerir que instale Python y dependencias.

Limitaciones y puntos pendientes
- Firebase: El validador (`tools/validate_service_account.py`) reportó `invalid_scope` al intentar refrescar credenciales. Esto sugiere que la `serviceAccountKey.json` puede no corresponder al proyecto correcto o tener roles/scope incorrectos. Consecuencia: funciones en la nube pueden fallar hasta corregir este punto.
- Repositorio remoto: El remoto `https://github.com/SABADAZO23/StoreFlow1.git` fue añadido pero en remoto sólo está `.gitignore`; se recomienda empujar el resto del código (asegurarse de no incluir secretos).
- Splashscreen: No hay splashscreen implementado (pedido del tendero). Es fácil de añadir si se desea.
- CI / Issues: No hay workflow CI ni issues creados automáticamente. Se puede automatizar creación de issues y pipeline.





