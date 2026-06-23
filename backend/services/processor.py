# =============================================================
# PROSERVIS BOT - Orquestador Principal (Processor)
# Archivo: backend/services/processor.py
#
# FUNCIÓN: Coordinar las 6 capas de procesamiento en orden:
#
#   CAPA 0 → Comprensión global del mensaje
#   CAPA 1 → Detección de intención
#   CAPA 2 → Extracción de entidades
#   CAPA 3 → Memoria conversacional
#   CAPA 4 → Detección de datos faltantes
#   CAPA 5 → Generación de respuesta
#
# Este archivo es el único punto de entrada que llama main.py.
# main.py → processor.procesar_mensaje() → respuesta
# =============================================================

from typing import Dict, Any, Tuple

from .layer0_comprension  import comprension_global
from .layer1_intencion    import detectar_intencion
from .layer2_entidades    import extraer_entidades, extraer_entidades_globales
from .layer3_memoria      import cargar_memoria, actualizar_memoria
from .layer4_faltantes    import detectar_faltantes
from .layer5_respuesta    import generar_respuesta, determinar_estado
from database.conversation_repository import guardar_conversacion


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------

def procesar_mensaje(telefono: str, mensaje: str) -> Tuple[str, Dict[str, Any]]:
    """
    Procesa un mensaje de WhatsApp y retorna la respuesta del bot.

    FLUJO COMPLETO:
        1. Capa 0: Analizar estructura del mensaje
        2. Cargar memoria del usuario desde BD
        3. Capa 1: Detectar intención del mensaje actual
        4. Mantener intención anterior si el mensaje es una respuesta
        5. Capa 2: Extraer entidades del mensaje actual
        6. Capa 4: Detectar qué datos aún faltan
        7. Capa 5: Generar respuesta natural
        8. Capa 3: Actualizar y guardar memoria en BD

    Args:
        telefono (str): Número del usuario, ej. "573001112233"
        mensaje  (str): Texto recibido por WhatsApp

    Retorna:
        tuple: (
            respuesta  (str),  ← texto a enviar al usuario
            metadata   (dict)  ← intención, confianza (para logs)
        )
    """

    # ============================================================
    # CAPA 0 – Comprensión global
    # ============================================================
    comprension = comprension_global(mensaje)

    # ============================================================
    # CAPA 3 – Cargar memoria (antes de detectar intención,
    #          para saber cuál era la intención anterior)
    # ============================================================
    memoria = cargar_memoria(telefono)
    intencion_anterior = memoria.get("intencion_actual")

    # ============================================================
    # CAPA 1 – Detectar intención del mensaje actual
    # ============================================================
    deteccion  = detectar_intencion(mensaje, comprension)
    intencion  = deteccion.get("intencion")
    confianza  = deteccion.get("confianza", 0.0)

    # ============================================================
    # MANTENIMIENTO DE CONTEXTO
    # Si el mensaje actual parece ser una RESPUESTA a la pregunta
    # anterior (cédula, mes, número), conservar la intención previa
    # en lugar de reclasificar como ORIENTACION.
    # ============================================================
    if (
        intencion == "ORIENTACION"
        and intencion_anterior
        and intencion_anterior != "ORIENTACION"
    ):
        es_respuesta_simple = _es_respuesta_contextual(mensaje, intencion_anterior)
        if es_respuesta_simple:
            intencion = intencion_anterior
            deteccion["intencion"] = intencion

    # ============================================================
    # CAPA 2 – Extraer entidades (global + específica de intención)
    # ============================================================
    entidades_globales  = extraer_entidades_globales(mensaje)
    entidades_intencion = extraer_entidades(mensaje, intencion) if intencion else {}

    # Las entidades de intención tienen más peso que las globales
    entidades = {**entidades_globales, **entidades_intencion}

    # Mezclar con las variables ya en memoria para tener el estado completo
    variables_actualizadas = {**memoria.get("variables", {}), **entidades}

    # ============================================================
    # CAPA 4 – Detectar qué datos faltan
    # ============================================================
    faltantes_info = detectar_faltantes(intencion, variables_actualizadas)

    # ============================================================
    # CAPA 5 – Generar respuesta
    # ============================================================
    respuesta = generar_respuesta(
        intencion,
        variables_actualizadas,
        faltantes_info,
        comprension
    )

    # ============================================================
    # CAPA 3 – Actualizar memoria y persistir en BD
    # ============================================================
    nueva_memoria = actualizar_memoria(
        memoria,
        entidades,
        intencion or "ORIENTACION",
        mensaje,
        respuesta
    )

    estado_flujo = determinar_estado(faltantes_info)

    guardar_conversacion(
        telefono       = telefono,
        intencion      = intencion or "ORIENTACION",
        estado         = estado_flujo,
        variables      = nueva_memoria.get("variables", {}),
        mensaje_usuario= mensaje,
        mensaje_bot    = respuesta,
    )

    # Metadata para logs del servidor
    metadata = {
        "intencion":          intencion,
        "confianza":          confianza,
        "intencion_anterior": intencion_anterior,
        "estado_flujo":       estado_flujo,
    }

    return respuesta, metadata


# ------------------------------------------------------------------
# HELPER: Detectar si el mensaje es una respuesta contextual
# ------------------------------------------------------------------

def _es_respuesta_contextual(mensaje: str, intencion_anterior: str) -> bool:
    """
    Detecta si el mensaje actual parece ser la respuesta a una
    pregunta del bot (cédula, mes, ciudad, turno) en lugar de
    una nueva intención.

    Args:
        mensaje            (str): Texto del usuario.
        intencion_anterior (str): Última intención conocida.

    Retorna:
        bool: True si el mensaje es probablemente una respuesta simple.
    """
    import re

    msg = mensaje.strip().lower()

    # Respuestas para DESPRENDIBLE: números (cédula) o meses
    if intencion_anterior == "DESPRENDIBLE_PAGO":
        if re.fullmatch(r'\d{7,10}', msg.replace(" ", "")):
            return True  # Cédula
        meses = ["enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        if any(m in msg for m in meses):
            return True  # Mes

    # Respuestas para RECLUTAMIENTO: ciudades, turnos, experiencias
    if intencion_anterior == "RECLUTAMIENTO":
        ciudades  = ["cartagena","bogotá","bogota","medellín","medellin",
                     "cali","barranquilla"]
        turnos    = ["mañana","manana","tarde","noche","rotativo"]
        exp       = ["barrido","disposición","disposicion","aseo","no tengo"]
        if any(c in msg for c in ciudades + turnos + exp):
            return True

    # Respuestas para CERTIFICACION: solo cédula
    if intencion_anterior == "CERTIFICACION_LABORAL":
        if re.search(r'\b\d{7,10}\b', msg):
            return True

    return False