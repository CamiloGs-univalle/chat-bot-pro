# =============================================================
# PROSERVIS BOT - Capa 0: Comprensión Global del Mensaje
# Archivo: backend/services/layer0_comprension.py
#
# FUNCIÓN: Analizar la estructura del mensaje ANTES de intentar
#          detectar la intención. Identifica saludos, despedidas,
#          preguntas, afirmaciones y extrae datos brutos.
#
# SALIDA:
#   {
#     "tiene_saludo":    bool,
#     "tiene_despedida": bool,
#     "tiene_pregunta":  bool,
#     "tiene_afirmacion":bool,
#     "datos_brutos":    list[str],  ← palabras clave encontradas
#     "texto_limpio":    str,        ← mensaje sin el saludo
#     "mensaje_original":str
#   }
# =============================================================

from typing import Dict, Any, List


# ------------------------------------------------------------------
# LISTAS DE PALABRAS CLAVE
# ------------------------------------------------------------------

SALUDOS: List[str] = [
    "hola", "buenos días", "buenas tardes", "buenas noches",
    "holi", "buenas", "saludos", "que tal", "buen día",
    "hey", "ey", "buen dia"
]

DESPEDIDAS: List[str] = [
    "adiós", "adios", "chao", "chau", "hasta luego",
    "nos vemos", "bye", "hasta pronto", "hasta mañana",
    "hasta manana", "gracias y chao", "muchas gracias bye"
]

PALABRAS_PREGUNTA: List[str] = [
    "qué", "que", "cómo", "como", "cuándo", "cuando",
    "dónde", "donde", "por qué", "para qué", "cuánto",
    "cuántos", "me ayudas", "puedes", "podrías", "podrias",
    "tienes", "hay"
]

PALABRAS_AFIRMACION: List[str] = [
    "si", "sí", "claro", "correcto", "exacto", "tengo",
    "quiero", "necesito", "ok", "okay", "dale", "listo",
    "perfecto", "de acuerdo", "entendido"
]

# Palabras que se deben extraer como datos relevantes
PALABRAS_RELEVANTES: List[str] = [
    # Ciudades
    "cartagena", "bogotá", "bogota", "medellín", "medellin",
    "cali", "barranquilla",
    # Experiencias
    "barrido", "disposición", "disposicion", "aseo",
    # Turnos
    "mañana", "manana", "tarde", "noche", "rotativo",
    # Meses
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    # Trámites
    "cesantías", "cesantias", "vacaciones", "incapacidad",
    "permiso", "desprendible", "colilla", "certificado", "constancia",
]


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------

def comprension_global(mensaje: str) -> Dict[str, Any]:
    """
    Analiza la estructura básica del mensaje del usuario.

    Args:
        mensaje (str): Texto recibido por WhatsApp.

    Retorna:
        dict: Diccionario con flags booleanos y datos extraídos.

    Ejemplo:
        >>> comprension_global("hola busco trabajo en cartagena")
        {
            "tiene_saludo": True,
            "tiene_despedida": False,
            "tiene_pregunta": False,
            "tiene_afirmacion": False,
            "datos_brutos": ["cartagena"],
            "texto_limpio": "busco trabajo en cartagena",
            "mensaje_original": "hola busco trabajo en cartagena"
        }
    """
    mensaje_lower = mensaje.lower().strip()

    # ---- Detectar saludo ----
    tiene_saludo = any(s in mensaje_lower for s in SALUDOS)

    # ---- Detectar despedida ----
    tiene_despedida = any(d in mensaje_lower for d in DESPEDIDAS)

    # ---- Detectar pregunta ----
    tiene_pregunta = (
        "?" in mensaje
        or any(p in mensaje_lower for p in PALABRAS_PREGUNTA)
    )

    # ---- Detectar afirmación ----
    tiene_afirmacion = any(a in mensaje_lower for a in PALABRAS_AFIRMACION)

    # ---- Extraer palabras clave relevantes ----
    datos_brutos = [p for p in PALABRAS_RELEVANTES if p in mensaje_lower]

    # ---- Limpiar el texto (quitar el saludo para análisis posterior) ----
    texto_limpio = mensaje_lower
    for saludo in SALUDOS:
        texto_limpio = texto_limpio.replace(saludo, "").strip()

    return {
        "tiene_saludo":     tiene_saludo,
        "tiene_despedida":  tiene_despedida,
        "tiene_pregunta":   tiene_pregunta,
        "tiene_afirmacion": tiene_afirmacion,
        "datos_brutos":     datos_brutos,
        "texto_limpio":     texto_limpio,
        "mensaje_original": mensaje,
    }


# ------------------------------------------------------------------
# HELPER: Prefijo de saludo para la respuesta
# ------------------------------------------------------------------

def obtener_saludo_inicial(comprension: Dict) -> str:
    """
    Retorna "¡Hola! " si el usuario saludó, cadena vacía si no.
    Se usa en layer5_respuesta para personalizar la respuesta.
    """
    return "¡Hola! " if comprension.get("tiene_saludo") else ""