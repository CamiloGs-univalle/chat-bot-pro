# =============================================================
# PROSERVIS BOT - Capa 1: Detección de Intención
# Archivo: backend/services/layer1_intencion.py
#
# FUNCIÓN: Identificar qué quiere hacer el usuario a partir
#          del texto limpio entregado por la Capa 0.
#
# INTENCIONES DISPONIBLES:
#   HABLAR_CON_HUMANO    → Contactar asesor
#   RECLUTAMIENTO        → Buscar empleo / postularse
#   INCAPACIDAD          → Radicar incapacidad médica
#   DESPRENDIBLE_PAGO    → Descargar colilla / volante de pago
#   PERMISOS             → Solicitar permiso laboral
#   CESANTIAS            → Retirar cesantías
#   VACACIONES           → Solicitar vacaciones
#   CERTIFICACION_LABORAL→ Descargar certificado laboral
#   ORIENTACION          → Ayuda general (fallback)
#
# SALIDA:
#   {
#     "intencion":   str,
#     "confianza":   float (0.0 - 1.0),
#     "modificadores": { "saludo": bool, "despedida": bool }
#   }
# =============================================================

from typing import Dict, Optional
from .layer0_comprension import comprension_global


# ------------------------------------------------------------------
# MAPA DE INTENCIONES → PALABRAS CLAVE
# El orden importa: las intenciones más específicas van primero
# para evitar falsos positivos en categorías genéricas.
# ------------------------------------------------------------------

INTENCIONES = [
    (
        "HABLAR_CON_HUMANO",
        ["asesor", "humano", "persona", "hablar con alguien",
         "agente", "operador", "representante", "atención humana",
         "me pueden llamar", "quiero que me llamen"]
    ),
    (
        "RECLUTAMIENTO",
        ["trabajo", "vacante", "empleo", "postular", "hoja de vida",
         "hv", "busco trabajo", "quiero trabajar", "estoy desempleado",
         "me contratan", "oferta de trabajo", "proceso de selección"]
    ),
    (
        "INCAPACIDAD",
        ["incapacidad", "incapacitado", "medico", "médico", "enfermo",
         "licencia médica", "enfermedad", "reposo", "radicar incapacidad",
         "certificado médico"]
    ),
    (
        "DESPRENDIBLE_PAGO",
        ["desprendible", "colilla", "volante de pago", "nomina", "nómina",
         "salario", "sueldo", "mi pago", "comprobante de pago"]
    ),
    (
        "PERMISOS",
        ["permiso", "día libre", "día de familia", "permiso remunerado",
         "calamidad", "calamidad doméstica", "no puedo ir", "ausentarme"]
    ),
    (
        "CESANTIAS",
        ["cesantía", "cesantias", "retirar cesantías", "mis ahorros",
         "fondo de cesantías", "retirar mis cesantías"]
    ),
    (
        "VACACIONES",
        ["vacaciones", "descanso", "vacacion", "días de vacaciones",
         "solicitar vacaciones", "pedir vacaciones"]
    ),
    (
        "CERTIFICACION_LABORAL",
        ["certificación", "constancia", "certificado laboral",
         "constancia laboral", "carta laboral", "certificado de trabajo"]
    ),
]


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------

def detectar_intencion(mensaje: str, comprension: Optional[Dict] = None) -> Dict:
    """
    Detecta la intención principal del mensaje del usuario.

    Args:
        mensaje     (str):  Texto recibido.
        comprension (dict): Resultado de layer0 (opcional; se calcula
                            internamente si no se provee).

    Retorna:
        dict: {
            "intencion":    str,    ← nombre de la intención detectada
            "confianza":    float,  ← nivel de certeza 0.0-1.0
            "modificadores":dict    ← contexto del mensaje
        }

    Ejemplos:
        "quiero trabajo en cartagena"  → RECLUTAMIENTO (0.96)
        "necesito mi desprendible"     → DESPRENDIBLE_PAGO (0.96)
        "me dieron incapacidad"        → INCAPACIDAD (0.96)
        "chao"                         → None (despedida)
        "hola"                         → ORIENTACION (0.0) con saludo=True
    """
    # Calcular comprensión si no viene del orquestador
    if comprension is None:
        comprension = comprension_global(mensaje)

    # Si es solo despedida, no hay intención que procesar
    if comprension.get("tiene_despedida"):
        return {
            "intencion": None,
            "confianza": 1.0,
            "modificadores": {
                "saludo":    comprension.get("tiene_saludo", False),
                "despedida": True,
            },
        }

    texto = comprension.get("texto_limpio", mensaje.lower())

    mejor_intencion = "ORIENTACION"
    mejor_confianza = 0.0

    for intencion, palabras_clave in INTENCIONES:
        coincidencias = sum(1 for p in palabras_clave if p in texto)
        if coincidencias > 0:
            # La confianza base es 0.85; sube con más coincidencias
            confianza = min(0.99, 0.85 + (coincidencias / max(len(palabras_clave), 1)) * 0.14)
            if confianza > mejor_confianza:
                mejor_confianza = confianza
                mejor_intencion = intencion

    return {
        "intencion": mejor_intencion,
        "confianza": mejor_confianza,
        "modificadores": {
            "saludo":    comprension.get("tiene_saludo", False),
            "despedida": comprension.get("tiene_despedida", False),
        },
    }