uvicorn main:app --reload --port 8000# GUÍA DE INSTALACIÓN - PROSERVIS BOT

## VERSIÓN: 7.0
## ÚLTIMA ACTUALIZACIÓN: 2026-06-12

---

## REQUISITOS PREVIOS

| Requisito | Versión | Cómo verificar |
|-----------|---------|----------------|
| Windows 10/11 | - | `winver` |
| Docker Desktop | 20.10+ | `docker --version` |
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Git | 2.x | `git --version` |
| WhatsApp | App móvil | Para escanear QR |

### Instalación rápida de requisitos (Windows)

**Si no tienes Docker:**
```bash
# Descargar Docker Desktop desde:
https://www.docker.com/products/docker-desktop/
Si no tienes Python:

bash
# Descargar Python 3.11+ desde:
https://www.python.org/downloads/
# IMPORTANTE: Marcar "Add Python to PATH" durante la instalación
Si no tienes Node.js:

bash
# Descargar Node.js 18+ desde:
https://nodejs.org/
INSTALACIÓN PASO A PASO
1. Clonar o crear el proyecto
bash
# Crear carpeta principal
mkdir ~/Desktop/proservis-bot
cd ~/Desktop/proservis-bot
2. Crear estructura de carpetas
bash
# Crear carpetas del backend
mkdir -p backend/database
mkdir -p backend/services
mkdir -p backend/docs

# Crear carpeta del gateway
mkdir whatsapp-gateway
3. Crear entorno virtual de Python
bash
cd backend

# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
Verás (.venv) al inicio de la línea.

4. Instalar dependencias de Python
bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install fastapi uvicorn psycopg2-binary pyyaml
pip install requests beautifulsoup4 lxml
5. Instalar dependencias de Node.js
bash
cd ../whatsapp-gateway
npm init -y
npm install @whiskeysockets/baileys axios qrcode-terminal
CONFIGURACIÓN DE POSTGRESQL CON DOCKER
6. Crear archivo docker-compose.yml en la raíz del proyecto
bash
cd ~/Desktop/proservis-bot
Crea el archivo docker-compose.yml:

yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: whatsapp_postgres
    restart: always
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
7. Iniciar PostgreSQL
bash
docker-compose up -d
Verificar que el contenedor esté corriendo:

bash
docker ps
Deberías ver:

text
CONTAINER ID   IMAGE         NAMES
xxxxxxx        postgres:15   whatsapp_postgres
8. Crear la tabla de conversaciones
Conectar a PostgreSQL:

bash
docker exec -it whatsapp_postgres psql -U postgres -d whatsapp_bot
Ejecutar el siguiente SQL:

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
Salir de PostgreSQL:

sql
\q
CREAR ARCHIVOS DEL BACKEND
9. Crear backend/database/connection.py
bash
cd ~/Desktop/proservis-bot/backend
Crea database/connection.py:

python
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="whatsapp_bot",
        user="postgres",
        password="postgres123"
    )

print("CONNECTION.PY CARGADO")
10. Crear backend/database/conversation_repository.py
python
from database.connection import get_connection
import json

def guardar_conversacion(
    telefono,
    intencion,
    estado,
    variables,
    mensaje_usuario,
    mensaje_bot
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversaciones(
            telefono,
            intencion_actual,
            estado_flujo,
            variables,
            ultimo_mensaje_usuario,
            ultimo_mensaje_bot
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (telefono)
        DO UPDATE SET
            intencion_actual = EXCLUDED.intencion_actual,
            estado_flujo = EXCLUDED.estado_flujo,
            variables = EXCLUDED.variables,
            ultimo_mensaje_usuario = EXCLUDED.ultimo_mensaje_usuario,
            ultimo_mensaje_bot = EXCLUDED.ultimo_mensaje_bot,
            updated_at = CURRENT_TIMESTAMP
    """, (
        telefono,
        intencion,
        estado,
        json.dumps(variables),
        mensaje_usuario,
        mensaje_bot
    ))

    conn.commit()
    cursor.close()
    conn.close()

def obtener_conversacion(telefono):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            telefono,
            intencion_actual,
            estado_flujo,
            variables
        FROM conversaciones
        WHERE telefono = %s
    """, (telefono,))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return resultado
11. Crear archivo __init__.py en database
bash
touch database/__init__.py
12. Crear las 6 capas en services/
Crear services/layer0_comprension.py:

python
# Capa 0: Comprensión Global del Mensaje
from typing import Dict, List, Any

SALUDOS = ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'holi', 'buenas', 'saludos', 'que tal']
DESPEDIDAS = ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye', 'hasta pronto']

def comprension_global(mensaje: str) -> Dict[str, Any]:
    mensaje_lower = mensaje.lower()
    
    tiene_saludo = any(s in mensaje_lower for s in SALUDOS)
    tiene_despedida = any(d in mensaje_lower for d in DESPEDIDAS)
    
    tiene_pregunta = (
        "?" in mensaje or 
        any(p in mensaje_lower for p in [
            "qué", "cómo", "cuándo", "dónde", "por qué", 
            "para qué", "me ayudas", "puedes", "podrías"
        ])
    )
    
    tiene_afirmacion = any(a in mensaje_lower for a in [
        "si", "sí", "claro", "correcto", "exacto", "tengo", "quiero", "necesito"
    ])
    
    palabras_clave = [
        'cartagena', 'bogotá', 'medellín', 'cali', 'barranquilla',
        'barrido', 'disposición', 'aseo', 'mañana', 'tarde', 'noche',
        'mayo', 'junio', 'julio', 'agosto', 'cesantías', 'vacaciones',
        'incapacidad', 'permiso', 'desprendible', 'colilla'
    ]
    
    datos_brutos = [p for p in palabras_clave if p in mensaje_lower]
    
    texto_limpio = mensaje_lower
    for s in SALUDOS:
        texto_limpio = texto_limpio.replace(s, '').strip()
    
    return {
        "tiene_saludo": tiene_saludo,
        "tiene_despedida": tiene_despedida,
        "tiene_pregunta": tiene_pregunta,
        "tiene_afirmacion": tiene_afirmacion,
        "datos_brutos": datos_brutos,
        "texto_limpio": texto_limpio,
        "mensaje_original": mensaje
    }

def obtener_saludo_inicial(comprension: Dict) -> str:
    if comprension.get("tiene_saludo"):
        return "¡Hola! "
    return ""
Crear services/layer1_intencion.py:

python
from typing import Dict, Optional
from .layer0_comprension import comprension_global

INTENCIONES = [
    ("HABLAR_CON_HUMANO", ['asesor', 'humano', 'persona', 'hablar con alguien', 'agente', 'operador']),
    ("RECLUTAMIENTO", ['trabajo', 'vacante', 'empleo', 'postular', 'hoja de vida', 'hv', 'busco trabajo', 'quiero trabajar']),
    ("INCAPACIDAD", ['incapacidad', 'incapacitado', 'medico', 'enfermo', 'licencia médica', 'enfermedad']),
    ("DESPRENDIBLE_PAGO", ['desprendible', 'colilla', 'pago', 'nomina', 'salario', 'sueldo']),
    ("PERMISOS", ['permiso', 'día libre', 'familia', 'permiso remunerado']),
    ("CESANTIAS", ['cesantía', 'cesantias', 'retirar cesantías', 'ahorro']),
    ("VACACIONES", ['vacaciones', 'descanso', 'vacacion']),
    ("CERTIFICACION_LABORAL", ['certificación', 'constancia', 'certificado laboral']),
]

def detectar_intencion(mensaje: str, comprension: Optional[Dict] = None) -> Dict:
    if comprension is None:
        comprension = comprension_global(mensaje)
    
    if comprension.get("tiene_despedida"):
        return {
            "intencion": None,
            "confianza": 1.0,
            "modificadores": {"saludo": comprension.get("tiene_saludo", False), "despedida": True}
        }
    
    mensaje_lower = comprension.get("texto_limpio", mensaje.lower())
    
    mejor_intencion = "ORIENTACION"
    mejor_confianza = 0.0
    
    for intencion, palabras in INTENCIONES:
        coincidencias = sum(1 for p in palabras if p in mensaje_lower)
        if coincidencias > 0:
            confianza = min(0.99, 0.85 + (coincidencias / max(len(palabras), 1)) * 0.14)
            if confianza > mejor_confianza:
                mejor_confianza = confianza
                mejor_intencion = intencion
    
    return {
        "intencion": mejor_intencion,
        "confianza": mejor_confianza,
        "modificadores": {
            "saludo": comprension.get("tiene_saludo", False),
            "despedida": comprension.get("tiene_despedida", False),
        }
    }
Crear services/layer2_entidades.py:

python
import re
from typing import Dict, Any

CORRECCIONES = {
    'cartajena': 'cartagena', 'varrido': 'barrido', 'disposision': 'disposicion',
    'esperiencia': 'experiencia', 'manana': 'mañana', 'tare': 'tarde'
}

def corregir_ortografia(texto: str) -> str:
    resultado = texto
    for error, correccion in CORRECCIONES.items():
        resultado = resultado.replace(error, correccion)
    return resultado

def extraer_entidades(mensaje: str, intencion: str) -> Dict[str, Any]:
    entidades = {}
    mensaje_lower = corregir_ortografia(mensaje.lower())
    
    # Ciudades
    ciudades = {'cartagena': 'cartagena', 'bogotá': 'bogota', 'medellín': 'medellin',
                'cali': 'cali', 'barranquilla': 'barranquilla'}
    for ciudad_key, ciudad_val in ciudades.items():
        if ciudad_key in mensaje_lower:
            entidades['ciudad'] = ciudad_val
            break
    
    # Experiencia
    if 'barrido' in mensaje_lower:
        entidades['experiencia'] = 'barrido'
    elif 'disposición' in mensaje_lower:
        entidades['experiencia'] = 'disposicion_final'
    
    # Turno
    if 'mañana' in mensaje_lower:
        entidades['turno'] = 'manana'
    elif 'tarde' in mensaje_lower:
        entidades['turno'] = 'tarde'
    elif 'noche' in mensaje_lower:
        entidades['turno'] = 'noche'
    
    # Mes
    meses = {'enero': 'enero', 'febrero': 'febrero', 'marzo': 'marzo', 'abril': 'abril',
             'mayo': 'mayo', 'junio': 'junio', 'julio': 'julio', 'agosto': 'agosto',
             'septiembre': 'septiembre', 'octubre': 'octubre', 'noviembre': 'noviembre', 'diciembre': 'diciembre'}
    for mes_key, mes_val in meses.items():
        if mes_key in mensaje_lower:
            entidades['mes'] = mes_val
            break
    
    # Año
    anio_match = re.search(r'20[2-3][0-9]', mensaje_lower)
    if anio_match:
        entidades['anio'] = anio_match.group()
    
    # Cédula
    cedula_match = re.search(r'\b(\d{7,10})\b', mensaje_lower)
    if cedula_match:
        cedula = cedula_match.group(1)
        if len(cedula) >= 7 and len(cedula) <= 10:
            entidades['cedula'] = cedula
    
    return entidades

def extraer_entidades_globales(mensaje: str) -> Dict[str, Any]:
    entidades = {}
    mensaje_lower = corregir_ortografia(mensaje.lower())
    
    anio_match = re.search(r'20[2-3][0-9]', mensaje_lower)
    if anio_match:
        entidades['anio'] = anio_match.group()
    
    numeros = re.findall(r'\b\d+\b', mensaje_lower)
    for num in numeros:
        if len(num) >= 7 and len(num) <= 10:
            entidades['cedula'] = num
            break
    
    return entidades
Crear services/layer3_memoria.py:

python
import json
from typing import Dict, Any
from datetime import datetime
from database.conversation_repository import obtener_conversacion

def cargar_memoria(telefono: str) -> Dict[str, Any]:
    conversacion = obtener_conversacion(telefono)
    
    memoria = {
        "telefono": telefono,
        "nombre": "",
        "tipo_usuario": "desconocido",
        "intencion_actual": "",
        "intencion_anterior": "",
        "ultimo_mensaje_usuario": "",
        "ultimo_mensaje_bot": "",
        "intentos_fallidos": 0,
        "variables": {
            "ciudad": None, "experiencia": None, "turno": None, "zona": None,
            "vacante_interes": None, "tiene_hv": False, "hv_adjuntada": False,
            "cedula": None, "mes": None, "anio": None
        },
        "estado_flujo": "INICIADO",
        "hv_url": None
    }
    
    if conversacion:
        telefono_db, intencion, estado, variables_json = conversacion
        if variables_json:
            variables = json.loads(variables_json) if isinstance(variables_json, str) else variables_json
            memoria["variables"].update(variables)
        memoria["intencion_actual"] = intencion or ""
        memoria["estado_flujo"] = estado or "INICIADO"
    
    return memoria

def actualizar_memoria(memoria: Dict, nuevas_entidades: Dict, intencion: str,
                       mensaje_usuario: str, respuesta_bot: str) -> Dict:
    if memoria.get("intencion_actual"):
        memoria["intencion_anterior"] = memoria["intencion_actual"]
    
    for key, value in nuevas_entidades.items():
        if value is not None:
            memoria["variables"][key] = value
    
    memoria["intencion_actual"] = intencion
    memoria["ultimo_mensaje_usuario"] = mensaje_usuario
    memoria["ultimo_mensaje_bot"] = respuesta_bot
    memoria["ultima_interaccion"] = datetime.now().isoformat()
    
    return memoria

def obtener_estado_actual(memoria: Dict) -> Dict:
    variables = memoria.get("variables", {})
    existentes = [k for k, v in variables.items() if v and v is not None]
    return {"estado_actual": variables, "datos_existentes": existentes}
Crear services/layer4_faltantes.py:

python
from typing import Dict, List

def detectar_faltantes(intencion: str, variables: Dict[str, any]) -> Dict:
    existentes = []
    faltantes = []
    
    if intencion == "RECLUTAMIENTO":
        if variables.get('ciudad'):
            existentes.append('ciudad')
        else:
            faltantes.append('ciudad')
        
        if variables.get('ciudad') and not variables.get('hv_adjuntada'):
            faltantes.append('hoja_de_vida')
    
    elif intencion == "DESPRENDIBLE_PAGO":
        if variables.get('cedula'):
            existentes.append('cedula')
        else:
            faltantes.append('cedula')
        
        if variables.get('mes'):
            existentes.append('mes')
        else:
            faltantes.append('mes')
    
    elif intencion == "CERTIFICACION_LABORAL":
        if variables.get('cedula'):
            existentes.append('cedula')
        else:
            faltantes.append('cedula')
    
    proximo_paso = None
    if faltantes:
        primer_faltante = faltantes[0]
        paso_mapping = {
            "ciudad": "preguntar_ciudad", "cedula": "preguntar_cedula",
            "mes": "preguntar_mes", "hoja_de_vida": "solicitar_hv"
        }
        proximo_paso = paso_mapping.get(primer_faltante, "preguntar_general")
    
    return {
        "datos_existentes": existentes,
        "datos_faltantes": faltantes,
        "proximo_paso": proximo_paso,
        "tiene_todo": len(faltantes) == 0
    }
Crear services/layer5_respuesta.py:

python
from typing import Dict, List, Any

def generar_respuesta(intencion: str, variables: Dict, faltantes_info: Dict, comprension: Dict) -> str:
    tiene_saludo = comprension.get("tiene_saludo", False)
    saludo = "¡Hola! " if tiene_saludo else ""
    
    if intencion is None or comprension.get("tiene_despedida"):
        return "¡Hasta luego! Fue un gusto ayudarte. 👋"
    
    if intencion == "ORIENTACION":
        return f"""{saludo}Tranquilo, te explico. Puedo ayudarte con:

📄 Desprendible de pago
🏥 Incapacidad médica
📋 Permisos
💰 Cesantías
🌴 Vacaciones
📜 Certificación laboral
💼 Buscar empleo

¿Con cuál te ayudo?"""
    
    if intencion == "RECLUTAMIENTO":
        ciudad = variables.get('ciudad')
        experiencia = variables.get('experiencia')
        turno = variables.get('turno')
        
        if ciudad and experiencia and turno:
            return f"👍 ¡Excelente perfil! Vives en {ciudad}, experiencia en {experiencia}, disponibilidad {turno}. Adjúntame tu hoja de vida en PDF."
        if ciudad and experiencia:
            return f"👍 Perfecto. Vives en {ciudad} y tienes experiencia en {experiencia}. ¿Qué turno prefieres?"
        if ciudad:
            return f"{saludo}¿Tienes experiencia en barrido o disposición final?"
        return f"{saludo}¿En qué ciudad vives?"
    
    if intencion == "DESPRENDIBLE_PAGO":
        cedula = variables.get('cedula')
        mes = variables.get('mes')
        anio = variables.get('anio', '2026')
        
        if not cedula:
            return f"{saludo}Para descargar tu desprendible, necesito tu número de cédula."
        if cedula and not mes:
            return f"{saludo}Gracias. ¿De qué mes necesitas el desprendible?"
        if cedula and mes:
            return f"""{saludo}📄 Instrucciones para descargar tu desprendible de {mes} {anio}:

1️⃣ Ingresa al portal: https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx

2️⃣ Inicia sesión:
• Usuario: {cedula}
• Contraseña: {cedula[-4:]}

3️⃣ Ve a "DESCARGA DE DOCUMENTOS" → "VOLANTES DE PAGO"

4️⃣ Descarga el de {mes} {anio}

¿Necesitas ayuda?"""
        return f"{saludo}¿Cuál es tu cédula?"
    
    if intencion == "INCAPACIDAD":
        return f"""{saludo}🏥 Instrucciones para radicar incapacidad:

1️⃣ Adjunta el certificado médico en PDF
2️⃣ Tienes 2 días hábiles desde su expedición
3️⃣ Recibirás confirmación en 24 horas

¿Adjuntas el documento?"""
    
    if intencion == "CERTIFICACION_LABORAL":
        cedula = variables.get('cedula')
        if not cedula:
            return f"{saludo}Para descargar tu certificado, necesito tu cédula."
        return f"""{saludo}📜 Instrucciones:

1️⃣ Ingresa a: https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx
2️⃣ Usuario: {cedula}, Contraseña: {cedula[-4:]}
3️⃣ Ve a "DESCARGA DE DOCUMENTOS" → "CERTIFICADO LABORAL"

¿Necesitas ayuda con algo más?"""
    
    if intencion == "VACACIONES":
        return f"""{saludo}🌴 Para solicitar vacaciones:

1️⃣ Ingresa al portal con tu cédula
2️⃣ Ve a la sección de solicitudes
3️⃣ Selecciona fecha y días
4️⃣ Recibirás respuesta en 3 días hábiles

¿Quieres que te ayude con otro trámite?"""
    
    if intencion == "HABLAR_CON_HUMANO":
        return "👤 Te conecto con un asesor. ⏰ Horario: lunes a viernes 8am a 5pm"
    
    return f"{saludo}¿En qué puedo ayudarte?"

def determinar_estado(faltantes_info: Dict) -> str:
    faltantes = faltantes_info.get("datos_faltantes", [])
    if not faltantes:
        return "COMPLETADO"
    elif "cedula" in faltantes:
        return "CAPTURANDO_CEDULA"
    elif "mes" in faltantes:
        return "CAPTURANDO_MES"
    else:
        return "EN_PROCESO"
Crear services/processor.py (orquestador):

python
from typing import Dict, Any, Tuple
from .layer0_comprension import comprension_global
from .layer1_intencion import detectar_intencion
from .layer2_entidades import extraer_entidades, extraer_entidades_globales
from .layer3_memoria import cargar_memoria, actualizar_memoria
from .layer4_faltantes import detectar_faltantes
from .layer5_respuesta import generar_respuesta, determinar_estado
from database.conversation_repository import guardar_conversacion

def procesar_mensaje(telefono: str, mensaje: str) -> Tuple[str, Dict[str, Any]]:
    comprension = comprension_global(mensaje)
    memoria = cargar_memoria(telefono)
    intencion_anterior = memoria.get("intencion_actual")
    
    deteccion = detectar_intencion(mensaje, comprension)
    intencion = deteccion.get("intencion")
    
    # Mantener intención anterior si el mensaje actual es una respuesta
    if intencion == "ORIENTACION" and intencion_anterior and intencion_anterior != "ORIENTACION":
        es_respuesta = mensaje.isdigit() or any(m in mensaje.lower() for m in 
            ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
             'septiembre', 'octubre', 'noviembre', 'diciembre'])
        if es_respuesta:
            intencion = intencion_anterior
            deteccion["intencion"] = intencion
    
    entidades_globales = extraer_entidades_globales(mensaje)
    entidades_intencion = extraer_entidades(mensaje, intencion) if intencion else {}
    entidades = {**entidades_globales, **entidades_intencion}
    
    variables_actualizadas = {**memoria.get("variables", {}), **entidades}
    faltantes_info = detectar_faltantes(intencion, variables_actualizadas)
    
    respuesta = generar_respuesta(intencion, variables_actualizadas, faltantes_info, comprension)
    
    nueva_memoria = actualizar_memoria(memoria, entidades, intencion or "ORIENTACION", mensaje, respuesta)
    
    guardar_conversacion(
        telefono=telefono,
        intencion=intencion or "ORIENTACION",
        estado=determinar_estado(faltantes_info),
        variables=nueva_memoria.get("variables", {}),
        mensaje_usuario=mensaje,
        mensaje_bot=respuesta
    )
    
    metadata = {"intencion": intencion, "confianza": deteccion.get("confianza")}
    return respuesta, metadata
Crear services/__init__.py:

bash
touch services/__init__.py
13. Crear backend/main.py
python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import re

from services.processor import procesar_mensaje

app = FastAPI(title="Proservis Bot API", version="7.0")

class WhatsAppMessage(BaseModel):
    telefono: str
    mensaje: str

class WhatsAppResponse(BaseModel):
    respuesta: str
    intencion: Optional[str] = None

def limpiar_telefono(telefono: str) -> str:
    if '@' in telefono:
        telefono = telefono.split('@')[0]
    numeros = re.findall(r'\d+', telefono)
    if numeros:
        telefono = numeros[0]
    return telefono

@app.post("/mensaje")
async def mensaje_handler(data: WhatsAppMessage):
    try:
        telefono_limpio = limpiar_telefono(data.telefono)
        respuesta, metadata = procesar_mensaje(telefono_limpio, data.mensaje)
        print(f"📩 {telefono_limpio}: {data.mensaje[:50]}...")
        print(f"🤖 {metadata.get('intencion')}: {respuesta[:100]}...")
        return WhatsAppResponse(respuesta=respuesta, intencion=metadata.get("intencion"))
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"mensaje": "Proservis Bot v7.0", "estado": "funcionando"}

@app.get("/conversacion/{telefono}")
async def ver_conversacion(telefono: str):
    from services.layer3_memoria import cargar_memoria
    return cargar_memoria(limpiar_telefono(telefono))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
14. Crear archivo de prueba test_conversacion.py
python
from database.conversation_repository import guardar_conversacion, obtener_conversacion

guardar_conversacion(
    telefono="573001112233",
    intencion="RECLUTAMIENTO",
    estado="CAPTURANDO_CIUDAD",
    variables={"ciudad": "cartagena"},
    mensaje_usuario="quiero trabajo",
    mensaje_bot="¿En qué ciudad vives?"
)

resultado = obtener_conversacion("573001112233")
print(resultado)
CREAR ARCHIVOS DEL GATEWAY DE WHATSAPP
15. Crear whatsapp-gateway/index.js
javascript
const axios = require("axios");
const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason
} = require("@whiskeysockets/baileys");
const qrcode = require("qrcode-terminal");

async function iniciarBot() {
    const { state, saveCreds } = await useMultiFileAuthState("sessions");
    const sock = makeWASocket({ auth: state, printQRInTerminal: false });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", async (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log("\n📱 ESCANEA ESTE QR:\n");
            qrcode.generate(qr, { small: true });
        }
        if (connection === "open") {
            console.log("✅ WhatsApp conectado correctamente");
        }
        if (connection === "close") {
            console.log("❌ Conexión cerrada");
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            if (shouldReconnect) iniciarBot();
        }
    });

    sock.ev.on("messages.upsert", async ({ messages }) => {
        const msg = messages[0];
        if (!msg.message) return;
        if (msg.key.fromMe) return;

        const texto = msg.message.conversation || msg.message.extendedTextMessage?.text;
        if (!texto) return;

        console.log("📩 Mensaje recibido:", texto);

        try {
            const telefono = msg.key.remoteJid.replace("@s.whatsapp.net", "");
            const respuesta = await axios.post("http://127.0.0.1:8000/mensaje", {
                telefono: telefono,
                mensaje: texto
            });
            await sock.sendMessage(msg.key.remoteJid, { text: respuesta.data.respuesta });
        } catch (error) {
            console.error("❌ Error:", error.message);
        }
    });
}

iniciarBot();
EJECUCIÓN DEL BOT
Terminal 1 - Iniciar PostgreSQL (si no está corriendo)
bash
cd ~/Desktop/proservis-bot
docker-compose up -d
Terminal 2 - Iniciar Backend FastAPI
bash
cd ~/Desktop/proservis-bot/backend
.venv\Scripts\activate  # Windows
uvicorn main:app --reload --port 8000
Esperar ver:

text
INFO: Uvicorn running on http://127.0.0.1:8000
CONNECTION.PY CARGADO
INFO: Application startup complete.
Terminal 3 - Iniciar Gateway WhatsApp
bash
cd ~/Desktop/proservis-bot/whatsapp-gateway
node index.js
Aparecerá un código QR. Escanéalo con WhatsApp:

Abre WhatsApp en tu teléfono

Ve a "Dispositivos vinculados"

Toca "Vincular un dispositivo"

Escanea el QR

VERIFICACIÓN DE FUNCIONAMIENTO
Prueba 1: Enviar mensaje desde WhatsApp
Envía: "hola necesito trabajo"

Respuesta esperada:

text
¡Hola! ¿En qué ciudad vives?
Prueba 2: Continuar conversación
Envía: "Cartagena"

Respuesta esperada:

text
¿Tienes experiencia en barrido o disposición final?
Prueba 3: Verificar en PostgreSQL
bash
docker exec -it whatsapp_postgres psql -U postgres -d whatsapp_bot -c "SELECT telefono, intencion_actual, variables FROM conversaciones;"
SOLUCIÓN DE PROBLEMAS COMUNES
Error: psycopg2.OperationalError: password authentication failed
Solución: Verificar que la contraseña en database/connection.py coincida con POSTGRES_PASSWORD en docker-compose.yml.

Error: ModuleNotFoundError: No module named '...'
Solución: Activar entorno virtual e instalar:

bash
.venv\Scripts\activate
pip install <modulo-faltante>
Error: Gateway no conecta a FastAPI
Solución: Verificar que FastAPI esté corriendo:

bash
curl http://localhost:8000/
Error: QR no aparece
Solución: Eliminar carpeta sessions:

bash
cd whatsapp-gateway
rm -rf sessions
node index.js
Error: Puerto 8000 ya está en uso
Solución: Cambiar puerto o cerrar proceso:

bash
# Buscar proceso en puerto 8000
netstat -ano | findstr :8000
# Matar proceso (cambiar PID)
taskkill /PID <PID> /F
ESTRUCTURA FINAL DEL PROYECTO
text
proservis-bot/
│
├── backend/
│   ├── main.py
│   ├── test_conversacion.py
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
│   ├── package.json
│   └── sessions/
│
├── docker-compose.yml
└── .venv/
CONTACTO Y SOPORTE
Para soporte técnico, contactar al área de desarrollo.

Versión: 7.0
Última actualización: 2026-06-12