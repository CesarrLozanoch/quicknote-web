"""Crea la tabla 'notes' en la base de datos PostgreSQL apuntada por DATABASE_URL.

Uso:
    python create_table.py
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "No se encontro la variable de entorno DATABASE_URL. "
        "Define un archivo .env (mira .env.example) o exportala en tu shell."
    )


def main():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
        print("Tabla 'notes' creada (o ya existia).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
