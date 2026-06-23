# =============================================================
# PROSERVIS BOT - Conexión a PostgreSQL
# Archivo: backend/database/connection.py
#
# Proporciona la función get_connection() que abre y retorna
# una conexión a la base de datos. Se usa en el repositorio.
# =============================================================

import psycopg2


def get_connection():
    """
    Abre y retorna una conexión a PostgreSQL.

    Retorna:
        psycopg2.connection: Objeto de conexión activo.

    Uso:
        conn = get_connection()
        cursor = conn.cursor()
        ...
        conn.close()
    """
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="whatsapp_bot",
        user="postgres",
        password="postgres123"   # Debe coincidir con POSTGRES_PASSWORD en docker-compose.yml
    )


# ----------- Verificación rápida al importar el módulo -----------
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conexión a PostgreSQL exitosa.")
        conn.close()
    except Exception as e:
        print(f"❌ Error al conectar: {e}")