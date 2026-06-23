# =============================================================
# PROSERVIS BOT - Repositorio de Conversaciones
# Archivo: backend/database/conversation_repository.py
#
# Contiene todas las operaciones CRUD sobre la tabla
# `conversaciones` en PostgreSQL.
#
# Funciones disponibles:
#   - guardar_conversacion(...)  → INSERT o UPDATE
#   - obtener_conversacion(tel)  → SELECT por teléfono
#   - eliminar_conversacion(tel) → DELETE por teléfono (debug)
# =============================================================

import json
from database.connection import get_connection


# ------------------------------------------------------------------
# GUARDAR O ACTUALIZAR UNA CONVERSACIÓN
# ------------------------------------------------------------------

def guardar_conversacion(
    telefono: str,
    intencion: str,
    estado: str,
    variables: dict,
    mensaje_usuario: str,
    mensaje_bot: str
) -> None:
    """
    Inserta una conversación nueva o actualiza la existente.

    Usa INSERT ... ON CONFLICT (upsert) para que no falle si
    el teléfono ya existe en la tabla.

    Args:
        telefono      (str):  Número del usuario, ej. "573001112233"
        intencion     (str):  Intención detectada, ej. "RECLUTAMIENTO"
        estado        (str):  Estado del flujo, ej. "CAPTURANDO_CEDULA"
        variables     (dict): Datos acumulados {ciudad, cedula, mes, ...}
        mensaje_usuario (str): Último mensaje enviado por el usuario
        mensaje_bot   (str): Última respuesta enviada por el bot
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversaciones (
            telefono,
            intencion_actual,
            estado_flujo,
            variables,
            ultimo_mensaje_usuario,
            ultimo_mensaje_bot
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (telefono)
        DO UPDATE SET
            intencion_actual        = EXCLUDED.intencion_actual,
            estado_flujo            = EXCLUDED.estado_flujo,
            variables               = EXCLUDED.variables,
            ultimo_mensaje_usuario  = EXCLUDED.ultimo_mensaje_usuario,
            ultimo_mensaje_bot      = EXCLUDED.ultimo_mensaje_bot,
            updated_at              = CURRENT_TIMESTAMP
        """,
        (
            telefono,
            intencion,
            estado,
            json.dumps(variables),   # Guardar como JSON string
            mensaje_usuario,
            mensaje_bot,
        )
    )

    conn.commit()
    cursor.close()
    conn.close()


# ------------------------------------------------------------------
# OBTENER UNA CONVERSACIÓN EXISTENTE
# ------------------------------------------------------------------

def obtener_conversacion(telefono: str):
    """
    Busca la conversación de un usuario por su número de teléfono.

    Args:
        telefono (str): Número del usuario, ej. "573001112233"

    Retorna:
        tuple | None: (telefono, intencion_actual, estado_flujo, variables)
                      o None si el usuario no tiene historial previo.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            telefono,
            intencion_actual,
            estado_flujo,
            variables
        FROM conversaciones
        WHERE telefono = %s
        """,
        (telefono,)
    )

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return resultado   # None si no existe


# ------------------------------------------------------------------
# ELIMINAR UNA CONVERSACIÓN (útil para pruebas / reseteo)
# ------------------------------------------------------------------

def eliminar_conversacion(telefono: str) -> None:
    """
    Elimina el historial completo de un usuario.
    Útil en entornos de desarrollo para reiniciar un flujo.

    Args:
        telefono (str): Número del usuario.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM conversaciones WHERE telefono = %s",
        (telefono,)
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"🗑️  Conversación de {telefono} eliminada.")