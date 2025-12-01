# ⚠️ Configuración de Firebase

## IMPORTANTE: Seguridad

**NUNCA subas el archivo `serviceAccountKey.json` a un repositorio público.**

Este archivo contiene credenciales privadas de Firebase que dan acceso completo a tu proyecto.

## ¿Cómo obtener las credenciales?

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Configuración del proyecto** (ícono de engranaje)
4. Pestaña **Cuentas de servicio**
5. Haz clic en **Generar nueva clave privada**
6. Se descargará un archivo JSON
7. Renómbralo a `serviceAccountKey.json` y colócalo en esta carpeta

## ¿Cómo usar el archivo de ejemplo?

1. Copia `serviceAccountKey.json.example` a `serviceAccountKey.json`
2. Reemplaza los valores con tus credenciales reales
3. **NO** subas `serviceAccountKey.json` a Git (ya está en .gitignore)

## API Key de Firebase (Opcional pero recomendado)

Para verificación segura de contraseñas, puedes configurar la API key de Firebase:

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Configuración del proyecto** (ícono de engranaje)
4. Pestaña **General**
5. Busca la sección **Tus aplicaciones web** y copia la **API Key**

Luego configura la variable de entorno:
```bash
# Windows PowerShell
$env:FIREBASE_API_KEY="tu-api-key-aqui"

# Linux/Mac
export FIREBASE_API_KEY="tu-api-key-aqui"
```

**Nota:** Sin la API key, la aplicación funcionará en modo fallback (solo para desarrollo) donde la verificación de contraseña está deshabilitada por seguridad.

## ¿Qué pasa si no tengo credenciales?

No pasa nada. La aplicación funciona en **modo degradado**:
- Puedes usar todas las funcionalidades
- Los datos se mantienen mientras la app esté abierta
- Al cerrar la app, los datos se pierden (no hay persistencia real)
- **Importante:** Sin API key, la verificación de contraseñas está deshabilitada (solo para desarrollo)

Para desarrollo y pruebas, el modo degradado es perfectamente funcional.

