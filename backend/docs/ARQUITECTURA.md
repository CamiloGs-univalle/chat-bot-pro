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
│ │ └── layer5_respuesta.py # Capa 5: Generar respuesta
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

**Función:** Analizar la estructura del mensaje antes de detectar intención.

**Qué detecta:**
- Saludos (hola, buenos días, buenas tardes, etc.)
- Despedidas (adiós, chao, hasta luego, etc.)
- Preguntas (qué, cómo, cuándo, dónde, por qué, etc.)
- Afirmaciones (sí, claro, correcto, tengo, quiero, etc.)

**Salida:**
```json
{
  "tiene_saludo": true,
  "tiene_despedida": false,
  "tiene_pregunta": true,
  "tiene_afirmacion": false,
  "datos_brutos": ["cartagena", "barrido", "mañana"],
  "texto_limpio": "busco trabajo en cartagena tengo experiencia en barrido",
  "mensaje_original": "hola busco trabajo en cartagena"
}
Capa 1: Detección de Intención (layer1_intencion.py)
Función: Identificar qué quiere hacer el usuario.

Intenciones disponibles:

Intención	Descripción	Palabras clave
HABLAR_CON_HUMANO	Contactar asesor	asesor, humano, persona, agente
RECLUTAMIENTO	Buscar empleo	trabajo, vacante, empleo, postular, HV
INCAPACIDAD	Radicar incapacidad	incapacidad, médico, enfermo, reposo
DESPRENDIBLE_PAGO	Descargar colilla	desprendible, colilla, pago, nómina
PERMISOS	Solicitar permisos	permiso, día libre, familia
CESANTIAS	Retirar cesantías	cesantía, retirar, ahorro
VACACIONES	Solicitar vacaciones	vacaciones, descanso
CERTIFICACION_LABORAL	Descargar certificado	certificación, constancia
ORIENTACION	Ayuda general	ayuda, no entiendo, qué puedo hacer
Salida:

json
{
  "intencion": "RECLUTAMIENTO",
  "confianza": 0.96,
  "modificadores": {
    "saludo": true,
    "despedida": false,
    "pregunta": false,
    "afirmacion": false
  }
}
Capa 2: Extracción de Entidades (layer2_entidades.py)
Función: Extraer datos específicos del mensaje del usuario.

Entidades por intención:

Intención	Entidad	Posibles valores
RECLUTAMIENTO	ciudad	cartagena, bogotá, medellín, cali, barranquilla
RECLUTAMIENTO	experiencia	barrido, disposición final, aseo
RECLUTAMIENTO	turno	mañana, tarde, noche, rotativo
DESPRENDIBLE_PAGO	cédula	números de 7-10 dígitos
DESPRENDIBLE_PAGO	mes	enero, febrero, marzo, ..., diciembre
DESPRENDIBLE_PAGO	año	2023, 2024, 2025, 2026
Correcciones ortográficas automáticas:

cartajena → cartagena

varrido → barrido

disposision → disposicion

manana → mañana

Salida:

json
{
  "ciudad": "cartagena",
  "experiencia": "barrido",
  "turno": "manana",
  "cedula": "1105361400",
  "mes": "mayo",
  "anio": "2026"
}
Capa 3: Memoria Conversacional (layer3_memoria.py)
Función: Acumular todo el contexto de la conversación.

Estructura de memoria:

json
{
  "telefono": "573001112233",
  "nombre": "",
  "tipo_usuario": "desconocido",
  "intencion_actual": "DESPRENDIBLE_PAGO",
  "intencion_anterior": "",
  "ultimo_mensaje_usuario": "necesito mi desprendible",
  "ultimo_mensaje_bot": "Para descargar tu desprendible...",
  "ultima_interaccion": "2026-06-12T10:30:00Z",
  "intentos_fallidos": 0,
  "variables": {
    "ciudad": null,
    "experiencia": null,
    "turno": null,
    "zona": null,
    "vacante_interes": null,
    "tiene_hv": false,
    "hv_adjuntada": false,
    "cedula": "1105361400",
    "mes": "mayo",
    "anio": "2026"
  },
  "estado_flujo": "CAPTURANDO_MES",
  "hv_url": null
}
Acumulación de contexto (ejemplo):

text
Usuario 1: "necesito mi desprendible"     → intencion_actual = "DESPRENDIBLE_PAGO"
Usuario 2: "1105361400"                   → variables.cedula = "1105361400"
Usuario 3: "mayo 2026"                    → variables.mes = "mayo", variables.anio = "2026"
Capa 4: Detección de Faltantes (layer4_faltantes.py)
Función: Comparar lo que el usuario ya dijo con lo que el bot necesita saber.

Datos necesarios por flujo:

Intención	Dato	¿Obligatorio?
RECLUTAMIENTO	ciudad	Sí
RECLUTAMIENTO	experiencia	No (opcional)
RECLUTAMIENTO	turno	No (opcional)
RECLUTAMIENTO	hoja de vida	Sí (para postular)
DESPRENDIBLE_PAGO	cédula	Sí
DESPRENDIBLE_PAGO	mes	Sí
CERTIFICACION_LABORAL	cédula	Sí
Reglas de decisión:

Si el usuario YA DIJO ciudad → NO preguntar ciudad

Si el usuario YA DIJO experiencia → NO preguntar experiencia

Si el usuario YA DIJO turno → NO preguntar turno

Si el usuario YA ADJUNTÓ HV → NO pedir HV

Si el usuario YA DIJO cédula → NO preguntar cédula

Si el usuario YA DIJO mes → NO preguntar mes

Salida:

json
{
  "datos_existentes": ["cedula"],
  "datos_faltantes": ["mes"],
  "proximo_paso": "preguntar_mes",
  "tiene_todo": false
}
Capa 5: Generación de Respuesta (layer5_respuesta.py)
Función: Generar respuesta natural que parezca humana.

Reglas de oro:

✅ NUNCA preguntar algo que el usuario ya dijo

✅ SIEMPRE responder primero, preguntar después

✅ Reconocer explícitamente lo que el usuario aportó

✅ Usar un tono cercano y empático

Ejemplos de respuestas:

Situación	Respuesta
Usuario pide desprendible sin datos	"Para descargar tu desprendible, necesito tu número de cédula."
Usuario envía cédula	"Gracias. ¿De qué mes necesitas el desprendible?"
Usuario envía mes	Guía completa con enlace y pasos
Usuario pide trabajo sin ciudad	"¿En qué ciudad vives?"
Usuario dice ciudad	"¿Tienes experiencia en barrido o disposición final?"
Guía de desprendible (ejemplo):

text
📄 Instrucciones para descargar tu desprendible de mayo 2026:

1️⃣ Ingresa al portal de colaboradores:
🔗 https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx

2️⃣ Inicia sesión con tus credenciales:
• Usuario: 1105361400
• Contraseña: 1400 (los últimos 4 dígitos)

3️⃣ Una vez dentro:
• Busca la sección "DESCARGA DE DOCUMENTOS"
• Haz clic en "VOLANTES DE PAGO"

4️⃣ En la tabla de volantes:
• Localiza la fila del mes mayo 2026
• Haz clic en el enlace de descarga

✅ El PDF se descargará automáticamente.
BASE DE DATOS
Tabla: conversaciones
sql
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
Ejemplo de registro:
json
{
  "telefono": "573001112233",
  "intencion_actual": "DESPRENDIBLE_PAGO",
  "estado_flujo": "CAPTURANDO_MES",
  "variables": {
    "cedula": "1105361400",
    "mes": "mayo",
    "anio": "2026"
  },
  "ultimo_mensaje_usuario": "mayo 2026",
  "ultimo_mensaje_bot": "📄 Instrucciones para descargar..."
}
SORTTIME - ESTRATEGIA DE GUIAS
¿Por qué no integración automática?
SortTime tiene protecciones anti-bot que bloquean el acceso automatizado:

Error 403 al intentar acceder desde código

Validaciones de sesión y tokens ASP.NET

Diseñado solo para uso humano en navegador

Solución implementada:
El bot guía al usuario paso a paso en lugar de intentar acceso automático:

Paso	Acción del bot
1	Solicitar cédula
2	Solicitar mes/año
3	Enviar enlace directo al portal
4	Indicar credenciales (cédula + últimos 4 dígitos)
5	Dar instrucciones por sección
6	Ofrecer ayuda adicional
Flujo completo de guía:
text
Usuario → "necesito mi desprendible"
Bot    → "¿Cuál es tu cédula?"

Usuario → "1105361400"
Bot    → "¿Qué mes necesitas?"

Usuario → "mayo 2026"
Bot    → "📄 Instrucciones paso a paso:
         1. Ingresa a: https://www.sorttime.co/...
         2. Usuario: 1105361400
         3. Contraseña: 1400
         4. Ve a 'DESCARGA DE DOCUMENTOS'
         5. Haz clic en 'VOLANTES DE PAGO'
         6. Descarga el de mayo 2026"
TECNOLOGÍAS UTILIZADAS
Componente	Tecnología	Versión
Backend API	FastAPI (Python)	0.100+
WhatsApp Gateway	Baileys (Node.js)	6.0+
Base de Datos	PostgreSQL	15+
Contenedor	Docker	20.10+
Autenticación	Últimos 4 dígitos de cédula	-
Web Scraping	BeautifulSoup4 (solo para documentación)	4.12+
DIAGRAMA DE FLUJO DE MENSAJES
text
                    ┌─────────────────┐
                    │   USUARIO       │
                    │   WhatsApp      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   WHATSAPP      │
                    │   GATEWAY       │
                    │   (Baileys)     │
                    └────────┬────────┘
                             │ POST /mensaje
                             ▼
                    ┌─────────────────┐
                    │   FASTAPI       │
                    │   main.py       │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                        PROCESSOR.PY                                │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐              │
│  │  CAPA 0    │ -> │  CAPA 1    │ -> │  CAPA 2    │              │
│  │Comprensión │    │ Intención  │    │ Entidades  │              │
│  └────────────┘    └────────────┘    └────────────┘              │
│         │                 │                 │                     │
│         ▼                 ▼                 ▼                     │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐              │
│  │  CAPA 3    │ -> │  CAPA 4    │ -> │  CAPA 5    │              │
│  │  Memoria   │    │ Faltantes  │    │ Respuesta  │              │
│  └────────────┘    └────────────┘    └────────────┘              │
└────────────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐  ┌────────────┐  ┌────────────┐
       │ POSTGRESQL │  │  SORTTIME  │  │  WHATSAPP  │
       │  Memoria   │  │  (Guías)   │  │  Respuesta │
       └────────────┘  └────────────┘  └────────────┘
CONTROL DE VERSIONES
Versión	Fecha	Cambios
1.0	2026-06-11	Documentación inicial
2.0	2026-06-11	Ampliación a 11 flujos
3.0	2026-06-11	Adición de capa de contexto
4.0	2026-06-11	Arquitectura de 4 capas
5.0	2026-06-11	Unificación de RECLUTAMIENTO
6.0	2026-06-11	6 capas + reglas de naturalidad
7.0	2026-06-12	Guías paso a paso + documentación completa