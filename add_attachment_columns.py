"""Agrega las columnas de adjuntos a la tabla 'notes' en PostgreSQL.

Es seguro ejecutarlo varias veces: usa ADD COLUMN IF NOT EXISTS,
asi que no borra ni modifica las notas ya existentes.

Uso:
    python add_attachment_columns.py
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
                    "ALTER TABLE notes ADD COLUMN IF NOT EXISTS attachment_filename TEXT"
                )
                cur.execute(
                    "ALTER TABLE notes ADD COLUMN IF NOT EXISTS attachment_original_name TEXT"
                )
        print("Columnas de adjuntos agregadas (o ya existian). Las notas existentes no se tocaron.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
