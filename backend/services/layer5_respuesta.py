# =============================================================
# PROSERVIS BOT - Capa 5: Generación de Respuesta
# Archivo: backend/services/layer5_respuesta.py
#
# FUNCIÓN: Generar la respuesta final que el usuario recibirá
#          en WhatsApp. Usa el contexto acumulado para:
#            - Responder con empatía y naturalidad
#            - NUNCA preguntar algo que el usuario ya dijo
#            - Dar guías paso a paso para los portales
#            - Derivar a humano cuando es necesario
#
# REGLAS DE ORO:
#   ✅ NUNCA preguntar lo que el usuario ya dijo
#   ✅ Responder primero, preguntar después
#   ✅ Reconocer explícitamente lo que el usuario aportó
#   ✅ Tono cercano y empático (no robótico)
#
# PORTAL SORTTIME (credenciales):
#   URL:        https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx
#   Usuario:    cédula del colaborador
#   Contraseña: últimos 4 dígitos de la cédula
# =============================================================

from typing import Dict, Any, Optional

# URL fija del portal SortTime de Proservis
SORTTIME_URL = "https://www.sorttime.co/Sorttime2/Oficina/PSV/Inicio.aspx"


# ------------------------------------------------------------------
# HELPER: Texto del menú general de opciones
# ------------------------------------------------------------------

def _menu_opciones(saludo: str = "") -> str:
    return (
        f"{saludo}Tranquilo, te explico. Puedo ayudarte con:\n\n"
        "📄 *Desprendible de pago* → \"necesito mi desprendible\"\n"
        "🏥 *Incapacidad médica*   → \"tengo una incapacidad\"\n"
        "📋 *Permisos*             → \"necesito un permiso\"\n"
        "💰 *Cesantías*            → \"retirar mis cesantías\"\n"
        "🌴 *Vacaciones*           → \"pedir vacaciones\"\n"
        "📜 *Certificado laboral*  → \"necesito mi certificado\"\n"
        "💼 *Buscar empleo*        → \"quiero trabajo\"\n"
        "👤 *Hablar con asesor*    → \"hablar con humano\"\n\n"
        "Solo escríbeme lo que necesitas, como si le hablaras a un compañero. "
        "¿Con cuál te ayudo?"
    )


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------

def generar_respuesta(
    intencion: Optional[str],
    variables: Dict[str, Any],
    faltantes_info: Dict[str, Any],
    comprension: Dict[str, Any]
) -> str:
    """
    Genera la respuesta final del bot para el usuario.

    Args:
        intencion     (str|None): Intención detectada por Capa 1.
        variables     (dict):     Variables acumuladas en la memoria.
        faltantes_info(dict):     Resultado de la Capa 4.
        comprension   (dict):     Resultado de la Capa 0.

    Retorna:
        str: Mensaje de WhatsApp formateado con emojis y pasos.
    """
    saludo = "¡Hola! " if comprension.get("tiene_saludo") else ""

    # ---- Despedida ----
    if intencion is None or comprension.get("tiene_despedida"):
        return "¡Hasta luego! Fue un gusto ayudarte. 👋"

    # ---- Orientación / fallback ----
    if intencion == "ORIENTACION":
        return _menu_opciones(saludo)

    # ---- Hablar con humano ----
    if intencion == "HABLAR_CON_HUMANO":
        return (
            "👤 Enseguida te conecto con un asesor.\n\n"
            "⏰ Horario de atención: lunes a viernes, 8:00 am – 5:00 pm.\n\n"
            "Si estás fuera de horario, déjame tu mensaje y te responderemos "
            "en cuanto abramos. ¿Hay algo más en que pueda ayudarte?"
        )

    # ==================================================================
    # RECLUTAMIENTO
    # ==================================================================
    if intencion == "RECLUTAMIENTO":
        ciudad     = variables.get("ciudad")
        experiencia= variables.get("experiencia")
        turno      = variables.get("turno")
        hv_adj     = variables.get("hv_adjuntada", False)

        # Perfil completo + HV adjuntada → proceso iniciado
        if ciudad and hv_adj:
            exp_texto   = f", experiencia en *{experiencia}*" if experiencia else ""
            turno_texto = f", turno *{turno}*" if turno else ""
            return (
                f"✅ ¡Listo! Tu hoja de vida ha sido recibida.\n\n"
                f"📋 *Resumen de tu perfil:*\n"
                f"• Ciudad: *{ciudad}*{exp_texto}{turno_texto}\n\n"
                "Nuestro equipo de psicología revisará tu perfil. "
                "Si cumples los requisitos, te llamarán en máximo *3 días hábiles* "
                "al número de tu HV.\n\n"
                "¿Necesitas algo más?"
            )

        # Perfil completo → pedir HV
        if ciudad and experiencia and turno:
            return (
                f"👍 ¡Excelente perfil!\n\n"
                f"📋 *Resumen:*\n"
                f"• Ciudad: *{ciudad}*\n"
                f"• Experiencia: *{experiencia}*\n"
                f"• Turno: *{turno}*\n\n"
                "Adjúntame tu hoja de vida en *PDF* para postularte. 📎"
            )

        # Tiene ciudad y experiencia → pedir turno
        if ciudad and experiencia:
            return (
                f"Perfecto. Vives en *{ciudad}* y tienes experiencia en *{experiencia}*.\n\n"
                "¿Qué turno prefieres?\n"
                "🕕 Mañana (6am – 2pm)\n"
                "🕑 Tarde (2pm – 10pm)\n"
                "🌙 Noche (10pm – 6am)\n"
                "🔄 Rotativo"
            )

        # Tiene ciudad → pedir experiencia
        if ciudad:
            return (
                f"{saludo}En *{ciudad}* tenemos vacantes activas.\n\n"
                "¿Tienes experiencia en *barrido* o *disposición final*?\n"
                "(Si no tienes experiencia, dímelo igual 😊)"
            )

        # No tiene nada → pedir ciudad
        return (
            f"{saludo}¡Con gusto te ayudo a buscar empleo en Proservis!\n\n"
            "Actualmente tenemos vacantes para operarios de barrido y "
            "disposición final.\n\n"
            "¿En qué *ciudad* vives?"
        )

    # ==================================================================
    # DESPRENDIBLE DE PAGO
    # ==================================================================
    if intencion == "DESPRENDIBLE_PAGO":
        cedula = variables.get("cedula")
        mes    = variables.get("mes")
        anio   = variables.get("anio", "2026")

        # Tiene todo → dar guía completa
        if cedula and mes:
            contrasena = cedula[-4:]
            return (
                f"{saludo}📄 *Instrucciones para descargar tu desprendible de {mes} {anio}:*\n\n"
                f"1️⃣ Ingresa al portal de colaboradores:\n"
                f"🔗 {SORTTIME_URL}\n\n"
                f"2️⃣ Inicia sesión:\n"
                f"• Usuario: *{cedula}*\n"
                f"• Contraseña: *{contrasena}* (últimos 4 dígitos)\n\n"
                f"3️⃣ Busca la sección *\"DESCARGA DE DOCUMENTOS\"*\n\n"
                f"4️⃣ Haz clic en *\"VOLANTES DE PAGO\"*\n\n"
                f"5️⃣ Localiza la fila de *{mes} {anio}* y haz clic para descargar\n\n"
                f"✅ El PDF se descargará automáticamente.\n\n"
                "¿Lograste descargarlo? ¿Necesitas ayuda con algún paso?"
            )

        # Tiene cédula → pedir mes
        if cedula:
            return (
                f"{saludo}Gracias. ¿De qué mes necesitas el desprendible?\n\n"
                "Ejemplo: *mayo 2026*, *el más reciente*, *enero*"
            )

        # No tiene nada → pedir cédula
        return (
            f"{saludo}Para descargar tu desprendible de pago, necesito dos datos:\n\n"
            "1️⃣ Tu número de *cédula*\n"
            "2️⃣ El *mes* que necesitas\n\n"
            "¿Me das tu cédula?"
        )

    # ==================================================================
    # CERTIFICACIÓN LABORAL
    # ==================================================================
    if intencion == "CERTIFICACION_LABORAL":
        cedula = variables.get("cedula")

        if cedula:
            contrasena = cedula[-4:]
            return (
                f"{saludo}📜 *Instrucciones para descargar tu certificación laboral:*\n\n"
                f"1️⃣ Ingresa al portal de colaboradores:\n"
                f"🔗 {SORTTIME_URL}\n\n"
                f"2️⃣ Inicia sesión:\n"
                f"• Usuario: *{cedula}*\n"
                f"• Contraseña: *{contrasena}*\n\n"
                f"3️⃣ Ve a la sección *\"DESCARGA DE DOCUMENTOS\"*\n\n"
                f"4️⃣ Haz clic en *\"CERTIFICADO LABORAL\"*\n\n"
                f"✅ El PDF se descargará automáticamente.\n\n"
                "¿Necesitas ayuda con algo más?"
            )

        return (
            f"{saludo}Para descargar tu certificado laboral, necesito tu número de *cédula*.\n\n"
            "¿Me la das?"
        )

    # ==================================================================
    # INCAPACIDAD MÉDICA
    # ==================================================================
    if intencion == "INCAPACIDAD":
        return (
            f"{saludo}Lo siento, espero que te recuperes pronto. 🙏\n\n"
            "🏥 *Para radicar tu incapacidad médica:*\n\n"
            "1️⃣ *Adjunta el certificado médico* en PDF (o foto clara)\n\n"
            "2️⃣ Tienes *2 días hábiles* desde la fecha de expedición\n\n"
            "3️⃣ Nosotros lo enviamos al área de *Talento Humano*\n\n"
            "4️⃣ Recibirás confirmación en *24 horas hábiles*\n\n"
            "📎 Por favor, adjunta el documento aquí.\n\n"
            "¿Ya lo tienes listo?"
        )

    # ==================================================================
    # VACACIONES
    # ==================================================================
    if intencion == "VACACIONES":
        return (
            f"{saludo}🌴 *Para solicitar vacaciones:*\n\n"
            f"1️⃣ Ingresa al portal: {SORTTIME_URL}\n\n"
            "2️⃣ Ve a la sección *\"Solicitudes\"*\n\n"
            "3️⃣ Selecciona *\"Solicitud de Vacaciones\"*\n\n"
            "4️⃣ Completa:\n"
            "• Fecha de inicio deseada\n"
            "• Cantidad de días (máximo los acumulados)\n"
            "• Motivo (opcional)\n\n"
            "⏰ Tiempo de respuesta: *máximo 3 días hábiles*\n\n"
            "¿Necesitas saber cuántos días tienes acumulados?"
        )

    # ==================================================================
    # PERMISOS
    # ==================================================================
    if intencion == "PERMISOS":
        return (
            f"{saludo}📋 *Tipos de permiso disponibles:*\n\n"
            "📌 *Día de familia* – Atención de familiar directo\n"
            "📌 *Permiso remunerado* – Horas o días pagos\n"
            "📌 *Permiso no remunerado* – Sin descuento de nómina\n"
            "📌 *Calamidad doméstica* – Emergencia en el hogar\n\n"
            "*Proceso general:*\n"
            "1️⃣ Habla primero con tu jefe directo\n"
            "2️⃣ Ingresa al portal y crea la solicitud\n"
            "3️⃣ Adjunta justificación si aplica\n"
            "4️⃣ Espera aprobación (generalmente 24 horas)\n\n"
            "¿Cuál de estos necesitas?"
        )

    # ==================================================================
    # CESANTÍAS
    # ==================================================================
    if intencion == "CESANTIAS":
        return (
            f"{saludo}💰 *Para retirar tus cesantías, dime:*\n\n"
            "1️⃣ ¿Eres colaborador activo o ya no trabajas con nosotros?\n"
            "2️⃣ ¿Para qué es el retiro?\n"
            "   • Compra o mejora de vivienda\n"
            "   • Educación (tuya o de tus hijos)\n"
            "   • Desempleo\n\n"
            "Con esa información te indico el proceso exacto. ¿Cuál es tu situación?"
        )

    # ---- Fallback genérico ----
    return f"{saludo}¿En qué puedo ayudarte? {_menu_opciones()}"


# ------------------------------------------------------------------
# HELPER: Determinar el estado del flujo para guardarlo en BD
# ------------------------------------------------------------------

def determinar_estado(faltantes_info: Dict[str, Any]) -> str:
    """
    Retorna el código de estado del flujo según lo que falta.

    Args:
        faltantes_info (dict): Resultado de la Capa 4.

    Retorna:
        str: Código de estado, ej. "CAPTURANDO_CEDULA".
    """
    faltantes = faltantes_info.get("datos_faltantes", [])

    if not faltantes:
        return "COMPLETADO"

    mapa = {
        "cedula":       "CAPTURANDO_CEDULA",
        "mes":          "CAPTURANDO_MES",
        "ciudad":       "CAPTURANDO_CIUDAD",
        "experiencia":  "CAPTURANDO_EXPERIENCIA",
        "turno":        "CAPTURANDO_TURNO",
        "hoja_de_vida": "ESPERANDO_HV",
    }

    return mapa.get(faltantes[0], "EN_PROCESO")