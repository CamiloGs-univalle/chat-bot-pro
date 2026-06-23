bash
cat > docs/FLUJOS_BOT.md << 'EOF'
# FLUJOS DEL BOT PROSERVIS - DOCUMENTACIÓN COMPLETA

## Versión: 7.0
## Última actualización: 2026-06-12

---

## ARQUITECTURA DEL SISTEMA - 6 CAPAS
┌─────────────────────────────────────────────────────────────┐
│ USUARIO │
│ "hola, busco trabajo en Cartagena" │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 0 - COMPRENSIÓN GLOBAL DEL MENSAJE │
│ ¿Hay saludo? ¿Hay despedida? ¿Hay pregunta? │
│ Salida: { "tiene_saludo": true, "datos_brutos": [...] } │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 1 - DETECCIÓN DE INTENCIÓN │
│ ¿Qué quiere hacer el usuario? │
│ Salida: { "intencion": "RECLUTAMIENTO", "confianza": 0.96 } │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 2 - EXTRACCIÓN DE ENTIDADES │
│ Extraer datos específicos: ciudad, experiencia, cédula, mes │
│ Salida: { "ciudad": "cartagena", "experiencia": "barrido" } │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 3 - MEMORIA CONVERSACIONAL │
│ Acumular histórico y recordar datos del usuario │
│ Salida: { "variables": { "ciudad": "cartagena" } } │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 4 - DETECCIÓN DE FALTANTES │
│ ¿Qué falta para ayudar al usuario? │
│ Salida: { "faltantes": ["cedula", "mes"] } │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 5 - GENERACIÓN DE RESPUESTA │
│ Responder de forma natural y dar guías paso a paso │
│ Salida: "¡Hola! Para descargar tu desprendible..." │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ RESPUESTA AL USUARIO │
│ El usuario recibe instrucciones claras en WhatsApp │
└─────────────────────────────────────────────────────────────┘

text

---

## INTENCIONES DISPONIBLES

| Intención | Descripción | Datos que pide |
|-----------|-------------|----------------|
| **RECLUTAMIENTO** | Buscar empleo, postularse | ciudad, experiencia, turno, HV |
| **DESPRENDIBLE_PAGO** | Descargar colilla de pago | cédula, mes, año |
| **CERTIFICACION_LABORAL** | Descargar certificado | cédula |
| **INCAPACIDAD** | Radicar incapacidad médica | documento PDF |
| **VACACIONES** | Solicitar vacaciones | (guía directa) |
| **PERMISOS** | Solicitar permisos | (guía directa) |
| **CESANTIAS** | Retirar cesantías | (guía directa) |
| **HABLAR_CON_HUMANO** | Contactar asesor | (contacto directo) |
| **ORIENTACION** | Ayuda general | (menú de opciones) |

---

## FLUJO: DESPRENDIBLE DE PAGO (con guía)

### Interacción 1: Usuario pide desprendible
**Usuario:** `"necesito mi desprendible"`

**Bot:**
¡Hola! 📄 Para descargar tu desprendible de pago:

1️⃣ Dame tu número de cédula
2️⃣ Luego dime qué mes necesitas

Ejemplo: '1105361400' y luego 'mayo 2026'

text

### Interacción 2: Usuario envía cédula
**Usuario:** `"1105361400"`

**Bot:**
Gracias. ¿De qué mes necesitas el desprendible?

📌 Ejemplo: mayo 2026, o 'el más reciente'

text

### Interacción 3: Usuario envía mes
**Usuario:** `"mayo 2026"`

**Bot:**
📄 Instrucciones para descargar tu desprendible de mayo 2026:

1️⃣ Ingresa al portal de colaboradores:
🔗 https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx

2️⃣ Inicia sesión con tus credenciales:
• Usuario: 1105361400
• Contraseña: 1400 (los últimos 4 dígitos)

3️⃣ Una vez dentro, verás la pantalla principal:
• Busca la sección "DESCARGA DE DOCUMENTOS"
• Haz clic en "VOLANTES DE PAGO"

4️⃣ En la tabla de volantes:
• Localiza la fila del mes mayo 2026
• Haz clic en el enlace o botón de descarga

✅ El PDF se descargará automáticamente.

¿Necesitas ayuda con algún paso?

text

---

## FLUJO: CERTIFICADO LABORAL

### Interacción 1
**Usuario:** `"necesito mi certificado laboral"`

**Bot:**
📜 Instrucciones para descargar tu certificación laboral:

1️⃣ Ingresa al portal de colaboradores:
🔗 https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx

2️⃣ Inicia sesión con tus credenciales:
• Usuario: [cédula del usuario]
• Contraseña: [últimos 4 dígitos]

3️⃣ En la sección "DESCARGA DE DOCUMENTOS":
• Haz clic en "CERTIFICADO LABORAL"

✅ El PDF se descargará automáticamente.

¿Necesitas ayuda con algo más?

text

---

## FLUJO: RADICAR INCAPACIDAD

### Interacción
**Usuario:** `"tengo una incapacidad médica"`

**Bot:**
🏥 Instrucciones para radicar una incapacidad médica:

1️⃣ Documento requerido:
• Escaneo o foto clara del certificado médico (PDF)

2️⃣ Plazo:
• Tienes 2 días hábiles desde la fecha de expedición

3️⃣ Cómo enviarlo:
• Adjunta el PDF en este chat

4️⃣ Proceso:
• Recibiremos tu documento
• Lo enviaremos al área de Talento Humano
• Recibirás confirmación en 24 horas

📎 Por favor, adjunta tu certificado médico en PDF.

¿Tienes el documento listo para enviar?

text

---

## FLUJO: VACACIONES

### Interacción
**Usuario:** `"quiero pedir vacaciones"`

**Bot:**
🌴 Para solicitar vacaciones:

1️⃣ Ingresa al portal de colaboradores:
🔗 https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx

2️⃣ Una vez dentro:
• Ve a la sección de solicitudes
• Selecciona "Solicitud de Vacaciones"

3️⃣ Datos necesarios:
• Fecha de inicio deseada
• Cantidad de días (máximo los días acumulados)
• Motivo (opcional)

4️⃣ Tiempo de respuesta:
• Recibirás respuesta en máximo 3 días hábiles

¿Quieres que te ayude con otro trámite?

text

---

## FLUJO: RECLUTAMIENTO (Búsqueda de empleo)

### Interacción 1
**Usuario:** `"quiero trabajo"`

**Bot:**
¡Hola! Con gusto te ayudo a buscar empleo.
¿En qué ciudad vives?

text

### Interacción 2
**Usuario:** `"Cartagena"`

**Bot:**
¿Tienes experiencia en barrido o disposición final?

text

### Interacción 3
**Usuario:** `"barrido"`

**Bot:**
Perfecto. ¿Qué turno prefieres? (mañana, tarde o noche)

text

### Interacción 4
**Usuario:** `"mañana"`

**Bot:**
👍 ¡Excelente perfil! Vives en Cartagena, experiencia en barrido, disponibilidad mañana.
Adjúntame tu hoja de vida en PDF para postularte.

text

---

## TABLA DE CONVERSACIONES

```sql
CREATE TABLE conversaciones (
    telefono VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100),
    tipo_usuario VARCHAR(20) DEFAULT 'desconocido',
    intencion_actual VARCHAR(50),
    intencion_anterior VARCHAR(50),
    estado_flujo VARCHAR(50) DEFAULT 'INICIADO',
    ultimo_mensaje_usuario TEXT,
    ultimo_mensaje_bot TEXT,
    ultima_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    intentos_fallidos INT DEFAULT 0,
    variables JSON,
    hv_adjuntada BOOLEAN DEFAULT FALSE,
    hv_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
REGLAS DE CONVERSACIÓN NATURAL
Regla	❌ Incorrecto	✅ Correcto
No preguntar lo ya dicho	"¿En qué ciudad vives?" (después de que dijo Cartagena)	"Perfecto. ¿Tienes experiencia en barrido?"
Responder primero, preguntar después	"¿Qué turno prefieres?"	"Perfecto. ¿Qué turno prefieres?"
Reconocer información	(ignorar lo que dijo)	"Veo que vives en Cartagena..."
Saludos no son intenciones	Detectar "SALUDO" como principal	Usar modificador saludo=true
CONTROL DE VERSIONES
Versión	Fecha	Cambios
1.0	2026-06-11	Documentación inicial
2.0	2026-06-11	Ampliación a 11 flujos
3.0	2026-06-11	Adición de capa de contexto
4.0	2026-06-11	Arquitectura de 4 capas
5.0	2026-06-11	Unificación de RECLUTAMIENTO
6.0	2026-06-11	6 capas + reglas de naturalidad
7.0	2026-06-12	Guías paso a paso para SortTime
EOF		
text

---

## ACTUALIZAR `docs/ARQUITECTURA.md`

```bash
cat > docs/ARQUITECTURA.md << 'EOF'
# ARQUITECTURA DEL SISTEMA - VERSIÓN 7.0

## VISIÓN GENERAL
┌─────────────────────────────────────────────────────────────────┐
│ WHATSAPP GATEWAY │
│ (Node.js + Baileys) - Conexión con WhatsApp Web │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ FASTAPI (Python) │
│ main.py:8000 │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ PROCESADOR DE MENSAJES │
│ services/processor.py │
└─────────────────────────────────────────────────────────────────┘
│
┌───────────────────────┼───────────────────────┐
▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ CAPA 0 │ │ CAPA 1 │ │ CAPA 2 │
│ Comprensión │──────▶│ Intención │──────▶│ Entidades │
│ Global │ │ │ │ │
└───────────────┘ └───────────────┘ └───────────────┘
│ │ │
▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ CAPA 3 │ │ CAPA 4 │ │ CAPA 5 │
│ Memoria │──────▶│ Faltantes │──────▶│ Respuesta │
│ │ │ │ │ │
└───────────────┘ └───────────────┘ └───────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ POSTGRESQL (Docker) │
│ Base de datos: whatsapp_bot │
│ Tabla: conversaciones │
└─────────────────────────────────────────────────────────────────┘

text

---

## ESTRUCTURA DE CARPETAS
proservis-bot/
│
├── backend/
│ ├── main.py # Servidor FastAPI
│ ├── database/
│ │ ├── connection.py # Conexión a PostgreSQL
│ │ └── conversation_repository.py # CRUD conversaciones
│ │
│ ├── services/
│ │ ├── processor.py # Orquestador de 6 capas
│ │ ├── layer0_comprension.py # Capa 0: Comprensión global
│ │ ├── layer1_intencion.py # Capa 1: Detectar intención
│ │ ├── layer2_entidades.py # Capa 2: Extraer datos
│ │ ├── layer3_memoria.py # Capa 3: Memoria
│ │ ├── layer4_faltantes.py # Capa 4: Detectar faltantes
│ │ ├── layer5_respuesta.py # Capa 5: Generar respuesta
│ │ └── sorttime_integration.py # (Deprecado - guías en su lugar)
│ │
│ └── docs/ # Documentación
│
└── whatsapp-gateway/
├── index.js # Gateway WhatsApp (Baileys)
└── sessions/ # Sesiones autenticadas

text

---

## CAPAS DEL PROCESAMIENTO

### Capa 0: Comprensión Global (`layer0_comprension.py`)
- Detecta saludos, despedidas, preguntas
- Extrae datos brutos del mensaje
- Limpia el texto para análisis posterior

### Capa 1: Detección de Intención (`layer1_intencion.py`)
- Identifica qué quiere hacer el usuario
- Retorna: `RECLUTAMIENTO`, `DESPRENDIBLE_PAGO`, `INCAPACIDAD`, etc.
- Asigna nivel de confianza

### Capa 2: Extracción de Entidades (`layer2_entidades.py`)
- Extrae ciudad, experiencia, turno, cédula, mes, año
- Corrige errores ortográficos comunes
- Normaliza valores

### Capa 3: Memoria Conversacional (`layer3_memoria.py`)
- Carga historial del usuario desde PostgreSQL
- Acumula variables de conversación
- Mantiene intención anterior

### Capa 4: Detección de Faltantes (`layer4_faltantes.py`)
- Compara lo que el usuario dijo vs lo que se necesita
- Define próximo paso a preguntar

### Capa 5: Generación de Respuesta (`layer5_respuesta.py`)
- Genera respuestas naturales
- NUNCA pregunta lo ya dicho
- Da guías paso a paso para SortTime

---

## BASE DE DATOS

### Tabla: `conversaciones`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| telefono | VARCHAR(20) | PRIMARY KEY |
| nombre | VARCHAR(100) | Nombre del usuario |
| tipo_usuario | VARCHAR(20) | interno/externo/desconocido |
| intencion_actual | VARCHAR(50) | Última intención detectada |
| intencion_anterior | VARCHAR(50) | Intención previa |
| estado_flujo | VARCHAR(50) | Estado actual del flujo |
| ultimo_mensaje_usuario | TEXT | Último mensaje del usuario |
| ultimo_mensaje_bot | TEXT | Última respuesta del bot |
| variables | JSON | Datos acumulados (ciudad, cédula, etc.) |
| hv_adjuntada | BOOLEAN | ¿Ya adjuntó hoja de vida? |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Última actualización |

---

## SORTTIME - ESTRATEGIA DE GUIAS

**Por qué no integración automática:**
SortTime tiene protecciones anti-bot que bloquean el acceso automatizado (error 403). Por razones de seguridad, la plataforma solo permite acceso mediante navegador humano.

**Solución implementada:**
El bot proporciona guías paso a paso con:
- Enlace directo al portal
- Credenciales (cédula + últimos 4 dígitos)
- Instrucciones claras por sección
- Capturas de referencia (cuando disponibles)

**Flujo de guía para desprendibles:**
1. Pedir cédula
2. Pedir mes/año
3. Enviar instrucciones completas con enlace y pasos

---

## TECNOLOGÍAS UTILIZADAS

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Backend | FastAPI (Python) | 0.100+ |
| WhatsApp Gateway | Baileys (Node.js) | 6.0+ |
| Base de Datos | PostgreSQL | 15+ |
| Contenedor | Docker | 20.10+ |
| Autenticación | Últimos 4 dígitos de cédula | - |

---

## INSTALACIÓN Y EJECUCIÓN

### 1. Iniciar PostgreSQL
```bash
docker start whatsapp_postgres
2. Iniciar Backend
bash
cd backend
source .venv/Scripts/activate  # Windows
uvicorn main:app --reload --port 8000
3. Iniciar Gateway WhatsApp
bash
cd whatsapp-gateway
node index.js
# Escanear QR con WhatsApp
4. Probar
Enviar mensaje al número del bot:

text
hola necesito trabajo
EOF

text

---

## ACTUALIZAR `docs/INSTALACION.md`

```bash
cat > docs/INSTALACION.md << 'EOF'
# GUÍA DE INSTALACIÓN - PROSERVIS BOT

## REQUISITOS PREVIOS

| Requisito | Versión | Verificar |
|-----------|---------|-----------|
| Windows 10/11 | - | `winver` |
| Docker Desktop | 20.10+ | `docker --version` |
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Git | 2.x | `git --version` |
| WhatsApp | App móvil | Para escanear QR |

---

## INSTALACIÓN PASO A PASO

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio> proservis-bot
cd proservis-bot
2. Crear entorno virtual de Python
bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
3. Instalar dependencias de Python
bash
cd backend
pip install --upgrade pip
pip install fastapi uvicorn psycopg2-binary pyyaml
pip install requests beautifulsoup4 lxml
4. Instalar dependencias de Node.js
bash
cd ../whatsapp-gateway
npm install @whiskeysockets/baileys axios qrcode-terminal
5. Configurar PostgreSQL con Docker
Crear archivo docker-compose.yml en la raíz:

yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: whatsapp_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: whatsapp_bot
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
Iniciar el contenedor:

bash
docker-compose up -d
6. Crear la tabla de conversaciones
Conectar a PostgreSQL:

bash
docker exec -it whatsapp_postgres psql -U postgres -d whatsapp_bot
Ejecutar SQL:

sql
CREATE TABLE IF NOT EXISTS conversaciones (
    telefono VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100),
    tipo_usuario VARCHAR(20) DEFAULT 'desconocido',
    intencion_actual VARCHAR(50),
    intencion_anterior VARCHAR(50),
    estado_flujo VARCHAR(50) DEFAULT 'INICIADO',
    ultimo_mensaje_usuario TEXT,
    ultimo_mensaje_bot TEXT,
    ultima_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    intentos_fallidos INT DEFAULT 0,
    variables JSON,
    hv_adjuntada BOOLEAN DEFAULT FALSE,
    hv_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Salir: \q

7. Configurar conexión a base de datos
Editar backend/database/connection.py:

python
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="whatsapp_bot",
        user="postgres",
        password="postgres123"  # Misma que en docker-compose
    )
EJECUCIÓN DEL BOT
Terminal 1 - Backend FastAPI
bash
cd backend
source .venv/Scripts/activate  # Windows
uvicorn main:app --reload --port 8000
Esperar ver:

text
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
Terminal 2 - Gateway WhatsApp
bash
cd whatsapp-gateway
node index.js
Esperar ver QR y escanear con WhatsApp:

text
ESCANEA ESTE QR:
█████████████████████████████
Terminal 3 - Verificar (opcional)
bash
curl http://localhost:8000/
# Debe responder: {"mensaje":"Proservis Bot v6.0 - 6 Capas","estado":"funcionando"}
VERIFICACIÓN DE FUNCIONAMIENTO
Prueba 1: Enviar mensaje desde WhatsApp
text
hola necesito trabajo
Respuesta esperada:

text
¡Hola! Con gusto te ayudo a buscar empleo. ¿En qué ciudad vives?
Prueba 2: Flujo de reclutamiento
text
Cartagena
→ Debe preguntar por experiencia

Prueba 3: Flujo de desprendible (guía)
text
necesito mi desprendible
→ Debe pedir cédula

SOLUCIÓN DE PROBLEMAS COMUNES
Error: psycopg2.OperationalError: password authentication failed
Solución: Verificar que password en connection.py coincida con POSTGRES_PASSWORD del contenedor.

Error: ModuleNotFoundError: No module named '...'
Solución: Activar entorno virtual e instalar dependencias:

bash
.venv\Scripts\activate
pip install <modulo-faltante>
Error: Gateway no conecta a FastAPI
Solución: Verificar que FastAPI esté corriendo en puerto 8000:

bash
curl http://localhost:8000/
Error: QR no aparece en terminal
Solución: Eliminar carpeta sessions y reintentar:

bash
cd whatsapp-gateway
rm -rf sessions
node index.js
Error: SortTime no permite acceso automático
Explicación: SortTime tiene protecciones anti-bot. El bot no accede automáticamente, sino que guía al usuario para que descargue manualmente. Esto es por diseño y seguridad.

ESTRUCTURA FINAL DEL PROYECTO
text
proservis-bot/
│
├── backend/
│   ├── main.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── conversation_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   ├── layer0_comprension.py
│   │   ├── layer1_intencion.py
│   │   ├── layer2_entidades.py
│   │   ├── layer3_memoria.py
│   │   ├── layer4_faltantes.py
│   │   └── layer5_respuesta.py
│   └── docs/
│       ├── ARQUITECTURA.md
│       ├── FLUJOS_BOT.md
│       └── INSTALACION.md
│
├── whatsapp-gateway/
│   ├── index.js
│   └── sessions/
│
├── docker-compose.yml
└── .venv/
PRÓXIMOS PASOS
Personalizar respuestas: Editar services/layer5_respuesta.py

Agregar intenciones: Modificar layer1_intencion.py

Agregar entidades: Modificar layer2_entidades.py

Cambiar guías: Editar las respuestas en layer5_respuesta.py

CONTACTO Y SOPORTE
Para soporte técnico, contactar al área de desarrollo.

Versión: 7.0
Última actualización: 2026-06-12