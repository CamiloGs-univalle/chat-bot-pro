# backend/services/intent_engine.py
import re
from typing import Dict, List, Optional, Any

# ========== CAPA 0: COMPRENSIÓN GLOBAL ==========
def comprension_global(mensaje: str) -> Dict[str, Any]:
    """
    Analiza la estructura del mensaje antes de detectar intención
    """
    mensaje_lower = mensaje.lower()
    
    # Detectar saludos
    saludos = ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'holi', 'buenas', 'saludos']
    tiene_saludo = any(s in mensaje_lower for s in saludos)
    
    # Detectar despedidas
    despedidas = ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye']
    tiene_despedida = any(d in mensaje_lower for d in despedidas)
    
    # Detectar si es pregunta
    tiene_pregunta = '?' in mensaje or any(p in mensaje_lower for p in 
                      ['qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'para qué', 'me ayudas', 'puedes'])
    
    # Extraer datos brutos (palabras clave)
    palabras_clave = ['cartagena', 'bogotá', 'medellín', 'cali', 'barranquilla',
                      'barrido', 'disposición', 'aseo', 'mañana', 'tarde', 'noche',
                      'mayo', 'junio', 'julio', 'agosto', 'cesantías', 'vacaciones',
                      'incapacidad', 'permiso', 'desprendible', 'colilla']
    
    datos_brutos = [p for p in palabras_clave if p in mensaje_lower]
    
    # Limpiar texto (remover saludos para análisis posterior)
    texto_limpio = mensaje_lower
    for s in saludos:
        texto_limpio = texto_limpio.replace(s, '').strip()
    
    return {
        "tiene_saludo": tiene_saludo,
        "tiene_despedida": tiene_despedida,
        "tiene_pregunta": tiene_pregunta,
        "datos_brutos": datos_brutos,
        "texto_limpio": texto_limpio
    }


# ========== CAPA 1: DETECCIÓN DE INTENCIÓN ==========
def detectar_intencion(mensaje: str, comprension: Dict = None) -> str:
    """
    Detecta qué quiere hacer el usuario
    """
    if comprension is None:
        comprension = comprension_global(mensaje)
    
    # Si es despedida, intención vacía
    if comprension.get("tiene_despedida"):
        return "DESPEDIDA"
    
    mensaje_lower = comprension.get("texto_limpio", mensaje.lower())
    
    # Matriz de intenciones (orden de prioridad)
    intenciones = [
        ("HABLAR_CON_HUMANO", ['asesor', 'humano', 'persona', 'hablar con alguien', 'agente', 'operador']),
        ("RECLUTAMIENTO", ['trabajo', 'vacante', 'empleo', 'postular', 'hoja de vida', 'hv', 'busco trabajo', 'quiero trabajar']),
        ("INCAPACIDAD", ['incapacidad', 'incapacitado', 'medico', 'enfermo', 'licencia médica', 'enfermedad']),
        ("DESPRENDIBLE_PAGO", ['desprendible', 'colilla', 'pago', 'nomina', 'salario', 'sueldo', 'pago de nómina']),
        ("PERMISOS", ['permiso', 'día libre', 'familia', 'permiso remunerado', 'día de familia']),
        ("CESANTIAS", ['cesantía', 'cesantias', 'retirar cesantías', 'ahorro']),
        ("VACACIONES", ['vacaciones', 'descanso', 'vacacion']),
        ("CERTIFICACION_LABORAL", ['certificación', 'constancia', 'certificado laboral']),
    ]
    
    for intencion, palabras in intenciones:
        if any(p in mensaje_lower for p in palabras):
            return intencion
    
    # Si no se detecta nada específico
    if comprension.get("tiene_pregunta") or "ayuda" in mensaje_lower or "no entiendo" in mensaje_lower:
        return "ORIENTACION"
    
    return "ORIENTACION"


# ========== CAPA 2: EXTRACCIÓN DE ENTIDADES ==========
def extraer_entidades(mensaje: str, intencion: str) -> Dict[str, Any]:
    """
    Extrae datos específicos del mensaje
    """
    entidades = {}
    mensaje_lower = mensaje.lower()
    
    # Ciudades
    ciudades = {
        'cartagena': 'cartagena',
        'bogotá': 'bogota', 'bogota': 'bogota',
        'medellín': 'medellin', 'medellin': 'medellin',
        'cali': 'cali',
        'barranquilla': 'barranquilla'
    }
    for ciudad_key, ciudad_val in ciudades.items():
        if ciudad_key in mensaje_lower:
            entidades['ciudad'] = ciudad_val
            break
    
    # Experiencia
    if 'barrido' in mensaje_lower:
        entidades['experiencia'] = 'barrido'
    elif 'disposición' in mensaje_lower or 'disposicion' in mensaje_lower:
        entidades['experiencia'] = 'disposicion_final'
    elif 'aseo' in mensaje_lower:
        entidades['experiencia'] = 'aseo'
    
    # Turno
    if 'mañana' in mensaje_lower:
        entidades['turno'] = 'manana'
    elif 'tarde' in mensaje_lower:
        entidades['turno'] = 'tarde'
    elif 'noche' in mensaje_lower:
        entidades['turno'] = 'noche'
    
    # Mes (para desprendibles)
    meses = {
        'enero': 'enero', 'febrero': 'febrero', 'marzo': 'marzo',
        'abril': 'abril', 'mayo': 'mayo', 'junio': 'junio',
        'julio': 'julio', 'agosto': 'agosto', 'septiembre': 'septiembre',
        'octubre': 'octubre', 'noviembre': 'noviembre', 'diciembre': 'diciembre'
    }
    for mes_key, mes_val in meses.items():
        if mes_key in mensaje_lower:
            entidades['mes'] = mes_val
            break
    
    # Año
    anio_match = re.search(r'20[2-3][0-9]', mensaje_lower)
    if anio_match:
        entidades['anio'] = anio_match.group()
    
    # Cédula (para autenticación en SortTime)
    cedula_match = re.search(r'\b(\d{7,10})\b', mensaje_lower)
    if cedula_match:
        cedula = cedula_match.group(1)
        if len(cedula) >= 7 and len(cedula) <= 10:
            entidades['cedula'] = cedula
    
    return entidades


# ========== CAPA 4: DETECCIÓN DE FALTANTES ==========
def detectar_faltantes(intencion: str, variables: Dict) -> List[str]:
    """
    Detecta qué información falta para completar la solicitud
    """
    faltantes = []
    
    if intencion == "RECLUTAMIENTO":
        if not variables.get('ciudad'):
            faltantes.append('ciudad')
        if not variables.get('hv_adjuntada') and not variables.get('tiene_hv'):
            if 'ciudad' not in faltantes:
                faltantes.append('hoja_de_vida')
    
    elif intencion == "DESPRENDIBLE_PAGO":
        if not variables.get('cedula'):
            faltantes.append('cedula')
        if not variables.get('mes'):
            faltantes.append('mes')
    
    elif intencion == "INCAPACIDAD":
        if not variables.get('tiene_pdf'):
            faltantes.append('documento')
    
    return faltantes


# ========== CAPA 5: GENERAR RESPUESTA ==========
def generar_respuesta(intencion: str, variables: Dict, faltantes: List, comprension: Dict) -> str:
    """
    Genera respuesta natural según el contexto
    """
    tiene_saludo = comprension.get('tiene_saludo', False)
    saludo_inicial = "¡Hola! " if tiene_saludo else ""
    
    # Caso especial: despedida
    if intencion == "DESPEDIDA":
        return "¡Hasta luego! Fue un gusto ayudarte. Si necesitas algo más, aquí estoy. 👋"
    
    # Caso: orientación
    if intencion == "ORIENTACION":
        return f"""{saludo_inicial}Tranquilo, te explico con calma. Puedo ayudarte con:

📄 Desprendible de pago (tu colilla)
🏥 Radicar incapacidades médicas
📋 Solicitar permisos (día de familia, remunerados)
💰 Retiro de cesantías
🌴 Vacaciones
📜 Certificación laboral
💼 Buscar empleo (vacantes y hoja de vida)

¿Con cuál de estas opciones te ayudo?"""
    
    # Caso: reclutamiento
    if intencion == "RECLUTAMIENTO":
        ciudad = variables.get('ciudad')
        experiencia = variables.get('experiencia')
        turno = variables.get('turno')
        
        if ciudad and experiencia and turno:
            exp_text = "barrido" if experiencia == 'barrido' else experiencia
            return f"👍 ¡Excelente perfil! Vives en {ciudad}, tienes experiencia en {exp_text} y disponibilidad en {turno}. Para postularte, solo necesito que me adjuntes tu hoja de vida en PDF. ¿Puedes enviármela?"
        
        if ciudad and experiencia:
            exp_text = "barrido" if experiencia == 'barrido' else experiencia
            return f"👍 Perfecto. Veo que vives en {ciudad} y tienes experiencia en {exp_text}. ¿Qué turno prefieres? (mañana, tarde o noche)"
        
        if ciudad:
            return f"{saludo_inicial}Con gusto te ayudo a buscar empleo. Actualmente tenemos vacantes para operarios de barrido y disposición final. ¿Tienes experiencia en alguno de estos?"
        
        return f"{saludo_inicial}Con gusto te ayudo a buscar empleo. ¿En qué ciudad vives?"
    
    # Caso: desprendible de pago con integración SortTime
    if intencion == "DESPRENDIBLE_PAGO":
        cedula = variables.get('cedula')
        mes = variables.get('mes')
        anio = variables.get('anio')
        
        # Paso 1: Si no hay cédula, pedirla
        if not cedula:
            return f"{saludo_inicial}Para descargar tu desprendible, necesito que me digas tu número de cédula."
        
        # Paso 2: Si no hay mes, pedirlo
        if cedula and not mes:
            return f"{saludo_inicial}Gracias. ¿De qué mes necesitas el desprendible? (ejemplo: mayo 2025)"
        
        # Paso 3: Tenemos cédula y mes, intentar obtener de SortTime
        if cedula and mes:
            try:
                from services.sorttime_integration import SortTimeAPI
                
                if not anio:
                    anio = "2025"
                
                success, msg, enlace = SortTimeAPI.obtener_enlace_desprendible(cedula, mes, anio)
                
                if success and enlace:
                    return f"""{saludo_inicial}✅ {msg}

Aquí tienes tu desprendible de {mes} {anio}:
{enlace}

¿Necesitas algo más?"""
                else:
                    return f"""{saludo_inicial}❌ {msg}

Posibles causas:
• La cédula no está registrada en SortTime
• No hay desprendible para {mes} {anio}
• El colaborador no está activo

¿Quieres hablar con un asesor humano?"""
                    
            except ImportError:
                return f"{saludo_inicial}Claro que sí. Para desprendibles, necesito tu cédula y el mes. Dime tu cédula primero."
            except Exception as e:
                return f"{saludo_inicial}Hubo un error conectando con SortTime. Por favor intenta más tarde o escribe 'hablar con humano'."
        
        return f"{saludo_inicial}Claro que sí. ¿Cuál es tu número de cédula?"
    
    # Caso: incapacidad
    if intencion == "INCAPACIDAD":
        return f"{saludo_inicial}Entiendo. Para radicar tu incapacidad médica, recuerda que tienes 2 días hábiles desde su expedición. Por favor adjunta el documento en PDF para procesarlo."
    
    # Caso: hablar con humano
    if intencion == "HABLAR_CON_HUMANO":
        return "Claro, con gusto te conecto con un asesor humano. Por favor espera un momento, un asesor se comunicará contigo pronto. ⏰ Horario: lunes a viernes 8am a 5pm"
    
    # Respuesta por defecto
    return f"{saludo_inicial}¿En qué puedo ayudarte? Puedo ayudarte con desprendibles, incapacidades, permisos, cesantías, vacaciones o búsqueda de empleo."


def determinar_estado(faltantes: List[str]) -> str:
    """
    Determina el estado del flujo según qué falta
    """
    if not faltantes:
        return "COMPLETADO"
    elif 'ciudad' in faltantes:
        return "CAPTURANDO_CIUDAD"
    elif 'cedula' in faltantes:
        return "CAPTURANDO_CEDULA"
    elif 'mes' in faltantes:
        return "CAPTURANDO_MES"
    elif 'hoja_de_vida' in faltantes:
        return "ESPERANDO_HV"
    else:
        return "EN_PROCESO"