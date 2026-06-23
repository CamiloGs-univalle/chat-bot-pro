# =============================================================
# PROSERVIS BOT - Script de Pruebas sin WhatsApp
# Archivo: backend/test_bot.py
#
# Permite probar el bot directamente desde la terminal,
# sin necesidad de tener el gateway de WhatsApp activo.
#
# USO:
#   cd backend
#   python test_bot.py
# =============================================================

from services.processor import procesar_mensaje
from database.conversation_repository import eliminar_conversacion

TELEFONO_PRUEBA = "573215799447"


def probar(mensaje: str) -> str:
    """Envía un mensaje al bot y muestra la respuesta."""
    respuesta, metadata = procesar_mensaje(TELEFONO_PRUEBA, mensaje)
    print(f"\n👤  Usuario: {mensaje}")
    print(f"🤖  Bot [{metadata.get('intencion')}]: {respuesta}")
    print("-" * 60)
    return respuesta


def limpiar():
    """Resetea la conversación de prueba."""
    eliminar_conversacion(TELEFONO_PRUEBA)
    print("🗑️  Historial de prueba borrado.\n")


if __name__ == "__main__":
    print("=" * 60)
    print("PROSERVIS BOT - Pruebas de Conversación")
    print("=" * 60)

    # ------ PRUEBA 1: Flujo de desprendible ------
    print("\n--- PRUEBA 1: Desprendible de pago ---")
    limpiar()
    probar("hola necesito mi desprendible")
    probar("1105361400")
    probar("mayo 2026")

    # ------ PRUEBA 2: Flujo de reclutamiento ------
    print("\n--- PRUEBA 2: Reclutamiento ---")
    limpiar()
    probar("quiero trabajo")
    probar("Cartagena")
    probar("barrido")
    probar("mañana")

    # ------ PRUEBA 3: Certificado laboral ------
    print("\n--- PRUEBA 3: Certificado laboral ---")
    limpiar()
    probar("necesito mi certificado laboral")
    probar("1105361400")

    # ------ PRUEBA 4: Orientación ------
    print("\n--- PRUEBA 4: Orientación ---")
    limpiar()
    probar("hola")
    probar("ayuda")

    # ------ PRUEBA 5: Incapacidad ------
    print("\n--- PRUEBA 5: Incapacidad ---")
    limpiar()
    probar("me dieron una incapacidad médica de 3 días")

    # ------ PRUEBA 6: Despedida ------
    print("\n--- PRUEBA 6: Despedida ---")
    limpiar()
    probar("muchas gracias, adiós")

    print("\n✅ Pruebas completadas.")