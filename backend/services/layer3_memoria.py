# =============================================================
# PROSERVIS BOT - Capa 3: Memoria Conversacional
# Archivo: backend/services/layer3_memoria.py
#
# FUNCIÓN: Cargar y actualizar el contexto acumulado de la
#          conversación de un usuario desde PostgreSQL.
#
# La memoria contiene TODO lo que el usuario ha dicho en
# conversaciones previas, para que el bot NUNCA repita
# preguntas ya respondidas.
#
# ESTRUCTURA DE MEMORIA:
#   {
#     "telefono":              "573001112233",
#     "intencion_actual":      "DESPRENDIBLE_PAGO",
#     "intencion_anterior":    "",
#     "estado_flujo":          "CAPTURANDO_MES",
#     "ultimo_mensaje_usuario":"necesito mi desprendible",
#     "ultimo_mensaje_bot":    "¿Cuál es tu cédula?",
#     "variables": {
#       "ciudad":       null,
#       "experiencia":  null,
#       "turno":        null,
#       "cedula":       "1105361400",
#       "mes":          null,
#       "anio":         null,
#       "tiene_hv":     false,
#       "hv_adjuntada": false
#     }
#   }
# =============================================================

import json
from typing import Dict, Any
from datetime import datetime
from database.conversation_repository import obtener_conversacion


# ------------------------------------------------------------------
# ESTRUCTURA VACÍA DE VARIABLES
# ------------------------------------------------------------------

def _variables_vacias() -> Dict[str, Any]:
    """Retorna un diccionario de variables con todos los valores nulos."""
    return {
        "ciudad":       None,
        "experiencia":  None,
        "turno":        None,
        "zona":         None,
        "vacante_interes": None,
        "tiene_hv":     False,
        "hv_adjuntada": False,
        "cedula":       None,
        "mes":          None,
        "anio":         None,
    }


# ------------------------------------------------------------------
# CARGAR MEMORIA DESDE LA BASE DE DATOS
# ------------------------------------------------------------------

def cargar_memoria(telefono: str) -> Dict[str, Any]:
    """
    Carga la memoria conversacional de un usuario desde PostgreSQL.

    Si el usuario es nuevo (sin historial), retorna una memoria
    vacía con valores por defecto.

    Args:
        telefono (str): Número del usuario, ej. "573001112233"

    Retorna:
        dict: Objeto de memoria completo listo para usar.
    """
    # Memoria vacía por defecto (usuario nuevo)
    memoria: Dict[str, Any] = {
        "telefono":              telefono,
        "nombre":                "",
        "tipo_usuario":          "desconocido",
        "intencion_actual":      "",
        "intencion_anterior":    "",
        "ultimo_mensaje_usuario":"",
        "ultimo_mensaje_bot":    "",
        "intentos_fallidos":     0,
        "variables":             _variables_vacias(),
        "estado_flujo":          "INICIADO",
        "hv_url":                None,
    }

    # Intentar cargar historial existente
    conversacion = obtener_conversacion(telefono)

    if conversacion:
        telefono_db, intencion, estado, variables_json = conversacion

        # Parsear variables JSON (puede venir como string o dict)
        if variables_json:
            variables_existentes = (
                json.loads(variables_json)
                if isinstance(variables_json, str)
                else variables_json
            )
            # Mezclar variables existentes sobre la base vacía
            memoria["variables"].update(variables_existentes)

        memoria["intencion_actual"] = intencion or ""
        memoria["estado_flujo"]     = estado or "INICIADO"

    return memoria


# ------------------------------------------------------------------
# ACTUALIZAR MEMORIA CON NUEVOS DATOS
# ------------------------------------------------------------------

def actualizar_memoria(
    memoria: Dict[str, Any],
    nuevas_entidades: Dict[str, Any],
    intencion: str,
    mensaje_usuario: str,
    respuesta_bot: str
) -> Dict[str, Any]:
    """
    Actualiza la memoria con los datos de la interacción actual.

    REGLA CLAVE: solo sobreescribe una variable si el nuevo valor
    NO es None/False. Esto garantiza que los datos anteriores del
    usuario nunca se pierdan.

    Args:
        memoria          (dict): Memoria cargada por cargar_memoria()
        nuevas_entidades (dict): Entidades extraídas en este turno
        intencion        (str):  Intención detectada en este turno
        mensaje_usuario  (str):  Mensaje enviado por el usuario
        respuesta_bot    (str):  Respuesta generada por el bot

    Retorna:
        dict: Memoria actualizada.
    """
    # Preservar la intención anterior antes de actualizar
    if memoria.get("intencion_actual"):
        memoria["intencion_anterior"] = memoria["intencion_actual"]

    # Acumular entidades: solo actualizar si el nuevo valor tiene contenido
    for clave, valor in nuevas_entidades.items():
        if valor is not None and valor is not False:
            memoria["variables"][clave] = valor

    # Actualizar campos de control
    memoria["intencion_actual"]       = intencion
    memoria["ultimo_mensaje_usuario"] = mensaje_usuario
    memoria["ultimo_mensaje_bot"]     = respuesta_bot
    memoria["ultima_interaccion"]     = datetime.now().isoformat()

    return memoria


# ------------------------------------------------------------------
# OBTENER RESUMEN DEL ESTADO ACTUAL
# ------------------------------------------------------------------

def obtener_estado_actual(memoria: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retorna un resumen de qué datos ya tiene el bot del usuario.

    Útil para debug y para que la Capa 4 sepa qué preguntar.

    Args:
        memoria (dict): Objeto de memoria.

    Retorna:
        dict: {
            "estado_actual":   dict,      ← variables actuales
            "datos_existentes": list[str] ← claves con valor
        }
    """
    variables = memoria.get("variables", {})
    existentes = [
        clave for clave, valor in variables.items()
        if valor and valor is not None
    ]
    return {
        "estado_actual":    variables,
        "datos_existentes": existentes,
    }