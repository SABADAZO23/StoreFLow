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

## Notas finales

Este proyecto fue hecho para aprender POO y manejo de bases de datos. Si encuentras algún bug o quieres mejorar algo, siéntete libre de hacerlo. El código es tuyo para usar como quieras.

**Importante:** Si compartes este proyecto, recuerda quitar el archivo `configuracion/serviceAccountKey.json` si lo tienes. No quieres que tus credenciales de Firebase anden por ahí 


