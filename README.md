# Bot People - Sistema de Automatización de Onboarding

Automatización del proceso de onboarding de nuevos empleados con integración a PeopleForce, Slack, Google Drive y Google Sheets.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/juliana3/bot-slack)

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura de Directorios](#estructura-de-directorios)
- [Tareas Automatizadas](#tareas-automatizadas)
- [Endpoints de la API](#endpoints-de-la-api)
- [Solución de Problemas](#solución-de-problemas)
- [Contribuir](#contribuir)

## Descripción

**Bot People** es un sistema integral de automatización basado en Python diseñado para optimizar el proceso de incorporación de nuevos empleados. Se integra con PeopleForce para gestión de RRHH, Slack para notificaciones, Google Drive para almacenamiento de documentos y Google Sheets para seguimiento de datos. El sistema incluye un formulario web para recolección de datos, procesamiento automático de documentos y tareas de limpieza programadas.

## Características

- **Formulario Web:** Interfaz amigable para recolección de datos de nuevos empleados
- **Integración Multiplataforma:**
  - API de PeopleForce para gestión de RRHH
  - Slack para notificaciones en tiempo real
  - Google Drive para almacenamiento de documentos
  - Google Sheets para seguimiento de datos
- **Flujos de Trabajo Automatizados:**
  - Carga automática de DNI a Google Drive
  - Persistencia de datos en base PostgreSQL
  - Reprocesamiento automático de errores
  - Tareas de limpieza programadas
- **Despliegue con Docker:** Completamente containerizado con Docker Compose
- **Manejo Robusto de Errores:** Logging completo y gestión de errores
- **Sistema de Autorización:** Flujo de aprobación basado en Google Sheets

## Instalación

### Requisitos Previos

- Docker y Docker Compose instalados
- Archivo de credenciales de Google Cloud
- Espacio de trabajo de Slack con bot configurado
- Acceso a la API de PeopleForce

### Despliegue con Docker (Recomendado)

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/juliana3/bot-slack.git
   cd bot-slack
   ```

2. **Configurar variables de entorno:**

   Edita el archivo `.env` con tus credenciales:

   ```bash
   # Base de datos
   DATABASE_URL=postgresql://myuser:mypassword@db:5432/postgres
   
   # Slack
   SLACK_TOKEN=xoxb-tu-token
   SLACK_CHANNEL_ID=C0931DFE125  # CAMBIAR: Este es un canal de prueba, usar el canal de producción
   SIGNING_SECRET=tu-signing-secret
   
   # PeopleForce
   PEOPLEFORCE_URL=https://api.peopleforce.io/api/public/v3/employees
   PEOPLEFORCE_TOKEN=tu-token
   DOCUMENT_FOLDER_ID_PF=12302  # NO CAMBIAR: Específico para Crombie
   
   # Google Drive
   DRIVE_ID=tu-drive-id
   DNI_FOLDER_ID=tu-folder-id
   CREDS_GOOGLE=chatbot-people-466623-1ec1f3039c87.json
   ID_SPREADSHEET=tu-spreadsheet-id
   NO_AUTORIZADOS_FOLDER_ID=tu-folder-id
   
   # Cron
   REPROCESO_URL=http://web:4000/reprocesar_errores
   ```

3. **Colocar archivo de credenciales de Google:**

   Asegúrate de que el archivo JSON de credenciales de Google Cloud esté en el directorio raíz.

4. **Iniciar los servicios:**

   ```bash
   docker-compose up -d --build
   ```

   Esto iniciará:
   - Base de datos PostgreSQL (puerto 5432)
   - Aplicación web Flask (puerto 4000)
   - Servicio cron automatizado para tareas programadas

5. **Verificar el despliegue:**

   ```bash
   docker ps
   docker-compose logs -f
   ```

6. **Acceder a la aplicación:**

   ```
   http://localhost:4000/formulario_ingresante
   ```

### Instalación Manual (Desarrollo)

1. **Crear un entorno virtual:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar PostgreSQL localmente y actualizar el `.env` según corresponda**

4. **Ejecutar la aplicación:**

   ```bash
   python app.py
   ```

## Configuración

### Archivos Requeridos

- `.env` - Configuración de variables de entorno
- `chatbot-people-466623-1ec1f3039c87.json` - Credenciales de Google Cloud
- `init.sql` - Schema de base de datos (se ejecuta automáticamente en el primer inicio)
- `manifiesto_app_slack.json` - Manifiesto de la app de Slack (para configuración del workspace)
- `appScript.js` - Script para Google Sheets Apps Script


### Configuración de la App de Slack

Usa el archivo `manifiesto_app_slack.json` para crear la app de Slack en tu workspace:

1. Ve a https://api.slack.com/apps
2. Haz clic en "Create New App" → "From an app manifest"
3. Pega el contenido de `manifiesto_app_slack.json`
4. Instala la app en tu workspace
5. Copia los tokens a tu archivo `.env`

### Script de Autorización en Google Sheets

Configura el Apps Script en tu Google Sheet para habilitar el flujo de autorización:

1. Abre tu Google Sheet
2. Ve a **Extensiones** → **Apps Script**
4. **IMPORTANTE:** Actualiza la URL en el script para que apunte a tu servidor de producción:

   ```javascript
   // Para desarrollo con ngrok:
   const url = "https://tu-url-ngrok.ngrok-free.app/autorizados";
   
   // Para producción (reemplaza con la URL de tu servidor):
   const url = "https://tu-dominio.com/autorizados";
   // o
   const url = "http://tu-ip-servidor:4000/autorizados";
   ```

5. Guarda y autoriza el script

**Nota:** El código completo del Apps Script está disponible en el archivo `appScript.js` del repositorio.

## Uso

### Comandos de Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web
docker-compose logs -f cron

# Detener todos los servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Reconstruir después de cambios en el código
docker-compose up -d --build

# Reiniciar base de datos (ADVERTENCIA: elimina todos los datos)
docker-compose down -v
docker-compose up -d --build
```

## Estructura de Directorios

```
bot-people/
├── .dockerignore           # Archivo de ignorados de Docker
├── .env                    # Variables de entorno
├── .gitignore              # Archivo de ignorados de Git
├── Dockerfile              # Configuración de imagen Docker
├── docker-compose.yml      # Orquestación de servicios Docker
├── init.sql                # Schema de inicialización de BD
├── README.md               # Este archivo
├── app.py                  # Aplicación principal Flask
├── appScript.js            # Script de Google Sheets (copiar a Apps Script)
├── cron_reproceso.py       # Script de tareas programadas
├── requirements.txt        # Dependencias de Python
├── chatbot-people-*.json   # Credenciales de Google
├── manifiesto_app_slack.json # Manifiesto de app Slack
├── handlers/               # Manejadores de peticiones
│   ├── autorizados_handler.py
│   ├── documento_handler.py
│   ├── ingreso_handler.py
│   └── reproceso_handler.py
├── services/               # Integración de servicios externos
│   ├── db_operations.py
│   ├── drive_utils.py
│   ├── payload_utils.py
│   ├── pdf_utils.py
│   ├── sheets_utils.py
│   └── slack_utils.py
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
│   ├── img/
│   ├── locales/
│   ├── script/
│   └── styles/
└── templates/              # Plantillas HTML
    ├── index.html
    └── agradecimiento.html
```

## Tareas Automatizadas

El sistema incluye tareas cron automatizadas para mantenimiento y recuperación de errores:

- **Reprocesamiento de Errores:** Cada 6 horas - Reintenta operaciones fallidas
- **Limpieza de Base de Datos:** Domingos a las 02:00 - Elimina entradas antiguas no autorizadas
- **Limpieza de Google Sheets:** Domingos a las 02:05 - Elimina filas antiguas no autorizadas
- **Limpieza de Google Drive:** Domingos a las 02:10 - Elimina archivos antiguos no autorizados

## Endpoints de la API

### `GET /formulario_ingresante`
Muestra el formulario de registro de nuevo empleado.

### `POST /agregar_persona`
Procesa el envío del formulario de nuevo empleado. Sube documentos a Drive, guarda en base de datos y notifica por Slack.

### `POST /autorizados`
Maneja actualizaciones de autorización desde Google Sheets. Procesa empleados aprobados y crea cuentas en PeopleForce.

### `GET|POST /reprocesar_errores`
Dispara manualmente el reprocesamiento de errores (también se ejecuta automáticamente vía cron).

### `POST /subir_pdf`
Procesa la carga de documentos PDF desde PeopleForce.

### `GET /gracias`
Página de agradecimiento después del envío del formulario.

## Solución de Problemas

### Aplicación no accesible

```bash
# Verificar si los contenedores están corriendo
docker ps

# Ver logs de Flask
docker-compose logs web
```

### Errores de conexión a base de datos

```bash
# Verificar estado de la base de datos
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db
```

### Las tareas cron no se ejecutan

```bash
# Ver logs del cron
docker-compose logs cron

# Reiniciar servicio cron
docker-compose restart cron
```

### Errores con la API de Google

- Verificar que el archivo de credenciales existe en el directorio raíz
- Revisar permisos del archivo
- Asegurarse que la cuenta de servicio tiene acceso a Drive y Sheets

### Puerto ya en uso

```bash
# Detener servicios en conflicto
docker-compose down

# Encontrar proceso usando el puerto 4000 (Linux/Mac)
lsof -i :4000

# Encontrar proceso usando el puerto 4000 (Windows)
netstat -ano | findstr :4000
```

## Contribuir

¡Las contribuciones son bienvenidas! Por favor sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/caracteristica-increible`)
3. Commitea tus cambios (`git commit -m 'Agregar característica increíble'`)
4. Push a la rama (`git push origin feature/caracteristica-increible`)
5. Abre un Pull Request

## Licencia

Este proyecto es código abierto y está disponible bajo la [Licencia MIT](LICENSE).