# Capa 2: Extracción de Entidades
import re
from typing import Dict, Any

# Correcciones ortográficas comunes
CORRECCIONES = {
    'cartajena': 'cartagena',
    'cartagenaa': 'cartagena',  
    'varrido': 'barrido',
    'barido': 'barrido',
    'disposision': 'disposicion',
    'esperiencia': 'experiencia',
    'manana': 'mañana',
    'tare': 'tarde',
    'nochee': 'noche',
    'desprendible': 'desprendible',
    'colilla': 'colilla'
}


def corregir_ortografia(texto: str) -> str:
    """Corrige errores ortográficos comunes"""
    resultado = texto
    for error, correccion in CORRECCIONES.items():
        resultado = resultado.replace(error, correccion)
    return resultado


def extraer_entidades(mensaje: str, intencion: str) -> Dict[str, Any]:
    """
    CAPA 2: Extrae datos específicos del mensaje
    """
    entidades = {}
    mensaje_lower = corregir_ortografia(mensaje.lower())
    
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
    
    # Cédula
    cedula_match = re.search(r'\b(\d{7,10})\b', mensaje_lower)
    if cedula_match:
        cedula = cedula_match.group(1)
        if len(cedula) >= 7 and len(cedula) <= 10:
            entidades['cedula'] = cedula
    
    return entidades


def extraer_entidades_globales(mensaje: str) -> Dict[str, Any]:
    """
    Extrae entidades que aplican a cualquier intención
    """
    entidades = {}
    mensaje_lower = corregir_ortografia(mensaje.lower())
    
    # Buscar fechas (años)
    anio_match = re.search(r'20[2-3][0-9]', mensaje_lower)
    if anio_match:
        entidades['anio'] = anio_match.group()
    
    # Buscar números (teléfonos, documentos)
    numeros = re.findall(r'\b\d+\b', mensaje_lower)
    if numeros:
        for num in numeros:
            if len(num) >= 7 and len(num) <= 10:
                entidades['cedula'] = num
                break
    
    return entidades
