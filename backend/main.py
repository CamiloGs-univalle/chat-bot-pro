# =============================================================
# PROSERVIS BOT - Servidor FastAPI
# Archivo: backend/main.py
#
# Punto de entrada de la API. Recibe los mensajes del Gateway
# de WhatsApp (index.js) y retorna la respuesta generada por
# el orquestador de 6 capas.
#
# ENDPOINTS:
#   POST /mensaje            → Procesar mensaje entrante
#   GET  /                   → Health check
#   GET  /conversacion/{tel} → Ver estado de un usuario (debug)
#   DELETE /conversacion/{tel} → Borrar historial (debug)
#
# INICIO:
#   uvicorn main:app --reload --port 8000
# =============================================================

import re
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.processor import procesar_mensaje


# ------------------------------------------------------------------
# APP
# ------------------------------------------------------------------

app = FastAPI(
    title       = "Proservis Bot API",
    description = "API del bot de WhatsApp de Proservis Temporales - 6 Capas",
    version     = "7.0",
)


# ------------------------------------------------------------------
# MODELOS DE DATOS (Pydantic)
# ------------------------------------------------------------------

class WhatsAppMessage(BaseModel):
    """Cuerpo del POST /mensaje enviado por el gateway de Node.js"""
    telefono: str   # Número del usuario, ej. "573001112233"
    mensaje:  str   # Texto del mensaje


class WhatsAppResponse(BaseModel):
    """Respuesta enviada de vuelta al gateway"""
    respuesta: str           # Texto que se enviará al usuario
    intencion: Optional[str] = None  # Para logs/monitoreo


# ------------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------------

def limpiar_telefono(telefono: str) -> str:
    """
    Normaliza el número de teléfono que llega desde Baileys.

    Baileys puede enviar el teléfono en formatos distintos:
      - "573001112233@s.whatsapp.net"  → "573001112233"
      - "+57 300 111 2233"             → "573001112233"

    Args:
        telefono (str): Número en cualquier formato.

    Retorna:
        str: Solo los dígitos del número.
    """
    # Quitar todo lo que va después del @
    if "@" in telefono:
        telefono = telefono.split("@")[0]

    # Extraer solo dígitos
    numeros = re.findall(r"\d+", telefono)
    return "".join(numeros) if numeros else telefono


# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------

@app.post("/mensaje", response_model=WhatsAppResponse)
async def recibir_mensaje(data: WhatsAppMessage):
    """
    Endpoint principal. Recibe un mensaje de WhatsApp y retorna
    la respuesta generada por el bot.

    El gateway de Node.js llama a este endpoint con:
        POST http://127.0.0.1:8000/mensaje
        Body: { "telefono": "573001112233", "mensaje": "hola" }

    Retorna:
        { "respuesta": "¡Hola! ¿En qué puedo ayudarte?", "intencion": "ORIENTACION" }
    """
    try:
        telefono = limpiar_telefono(data.telefono)

        # Imprimir en consola para monitoreo en tiempo real
        print(f"\n📩  [{telefono}] → {data.mensaje[:80]}")

        respuesta, metadata = procesar_mensaje(telefono, data.mensaje)

        print(f"🤖  [{metadata.get('intencion')}] ← {respuesta[:80]}...")

        return WhatsAppResponse(
            respuesta = respuesta,
            intencion = metadata.get("intencion"),
        )

    except Exception as e:
        # Log del error completo para debug
        import traceback
        print(f"\n❌ Error procesando mensaje de {data.telefono}:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    """Health check. Confirma que el servidor está funcionando."""
    return {
        "mensaje": "Proservis Bot v7.0 – 6 Capas",
        "estado":  "funcionando",
    }


@app.get("/conversacion/{telefono}")
async def ver_conversacion(telefono: str):
    """
    Retorna el estado completo de la conversación de un usuario.
    Útil para debug y soporte.

    Ejemplo:
        GET http://127.0.0.1:8000/conversacion/573001112233
    """
    from services.layer3_memoria import cargar_memoria
    return cargar_memoria(limpiar_telefono(telefono))


@app.delete("/conversacion/{telefono}")
async def borrar_conversacion(telefono: str):
    """
    Elimina el historial de un usuario. Útil para reiniciar
    flujos durante pruebas.

    Ejemplo:
        DELETE http://127.0.0.1:8000/conversacion/573001112233
    """
    from database.conversation_repository import eliminar_conversacion
    eliminar_conversacion(limpiar_telefono(telefono))
    return {"mensaje": f"Conversación de {telefono} eliminada."}


# ------------------------------------------------------------------
# EJECUCIÓN DIRECTA
# ------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        app,
        host   = "0.0.0.0",
        port   = 8000,
        reload = True,
    )