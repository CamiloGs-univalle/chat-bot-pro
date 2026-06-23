# =============================================================
# PROSERVIS BOT - Capa 4: Detección de Datos Faltantes
# Archivo: backend/services/layer4_faltantes.py
#
# FUNCIÓN: Comparar lo que el usuario YA dijo con lo que el
#          bot NECESITA para completar el flujo.
#          Define el próximo paso de la conversación.
#
# REGLAS DE ORO:
#   ✅ Si el usuario YA dijo ciudad    → NO preguntar ciudad
#   ✅ Si el usuario YA dijo cédula    → NO preguntar cédula
#   ✅ Si el usuario YA dijo mes       → NO preguntar mes
#   ✅ Si el usuario YA adjuntó HV     → NO pedir HV
#   ✅ Si el usuario YA dijo turno     → NO preguntar turno
#
# SALIDA:
#   {
#     "datos_existentes": ["cedula"],
#     "datos_faltantes":  ["mes"],
#     "proximo_paso":     "preguntar_mes",
#     "tiene_todo":       false
#   }
# =============================================================

from typing import Dict, Any, List


# ------------------------------------------------------------------
# MAPA: dato faltante → nombre del próximo paso
# ------------------------------------------------------------------

PASO_SIGUIENTE: Dict[str, str] = {
    "ciudad":       "preguntar_ciudad",
    "cedula":       "preguntar_cedula",
    "mes":          "preguntar_mes",
    "experiencia":  "preguntar_experiencia",
    "turno":        "preguntar_turno",
    "hoja_de_vida": "solicitar_hv",
}


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------

def detectar_faltantes(intencion: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determina qué datos le faltan al bot para completar el flujo.

    Args:
        intencion (str):  Intención activa del usuario.
        variables (dict): Variables acumuladas en la memoria (Capa 3).

    Retorna:
        dict: {
            "datos_existentes": list[str],  ← datos que el usuario ya dio
            "datos_faltantes":  list[str],  ← datos que aún se necesitan
            "proximo_paso":     str|None,   ← qué hacer a continuación
            "tiene_todo":       bool        ← True si el flujo puede cerrarse
        }

    Ejemplos:
        DESPRENDIBLE con cedula ya dada, sin mes:
        → {"datos_faltantes": ["mes"], "proximo_paso": "preguntar_mes", ...}

        RECLUTAMIENTO con todo dado y HV adjuntada:
        → {"datos_faltantes": [], "proximo_paso": None, "tiene_todo": True}
    """
    existentes: List[str] = []
    faltantes:  List[str] = []

    # ------------------------------------------------------------------
    # RECLUTAMIENTO
    # Necesita: ciudad (obligatorio), HV (obligatorio para postular)
    # Opcionales: experiencia, turno (si los dice bien, si no se pide)
    # ------------------------------------------------------------------
    if intencion == "RECLUTAMIENTO":
        if variables.get("ciudad"):
            existentes.append("ciudad")
        else:
            faltantes.append("ciudad")

        if variables.get("experiencia"):
            existentes.append("experiencia")
        # experiencia es opcional; si no la da, se pregunta pero no bloquea

        if variables.get("turno"):
            existentes.append("turno")
        # turno también es opcional

        # HV solo se pide una vez que ya tenemos ciudad
        if variables.get("ciudad") and not variables.get("hv_adjuntada"):
            faltantes.append("hoja_de_vida")
        elif variables.get("hv_adjuntada"):
            existentes.append("hoja_de_vida")

    # ------------------------------------------------------------------
    # DESPRENDIBLE DE PAGO
    # Necesita: cédula (obligatorio), mes (obligatorio)
    # ------------------------------------------------------------------
    elif intencion == "DESPRENDIBLE_PAGO":
        if variables.get("cedula"):
            existentes.append("cedula")
        else:
            faltantes.append("cedula")

        if variables.get("mes"):
            existentes.append("mes")
        else:
            faltantes.append("mes")

    # ------------------------------------------------------------------
    # CERTIFICACIÓN LABORAL
    # Necesita: cédula (obligatorio)
    # ------------------------------------------------------------------
    elif intencion == "CERTIFICACION_LABORAL":
        if variables.get("cedula"):
            existentes.append("cedula")
        else:
            faltantes.append("cedula")

    # ------------------------------------------------------------------
    # Para las demás intenciones no se necesitan datos previos;
    # el bot entrega la guía directamente.
    # ------------------------------------------------------------------

    # Determinar próximo paso
    proximo_paso = None
    if faltantes:
        primer_faltante = faltantes[0]
        proximo_paso = PASO_SIGUIENTE.get(primer_faltante, "preguntar_general")

    return {
        "datos_existentes": existentes,
        "datos_faltantes":  faltantes,
        "proximo_paso":     proximo_paso,
        "tiene_todo":       len(faltantes) == 0,
    }