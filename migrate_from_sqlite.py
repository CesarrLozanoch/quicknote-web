"""Migra las notas de notes.db (SQLite) a la tabla 'notes' en PostgreSQL.

Es seguro ejecutarlo varias veces: las notas que ya existan en Postgres
(mismo id) no se duplican.

Uso:
    python migrate_from_sqlite.py
"""

import os
import sqlite3

import psycopg2
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "notes.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "No se encontro la variable de entorno DATABASE_URL. "
        "Define un archivo .env (mira .env.example) o exportala en tu shell."
    )


def main():
    if not os.path.exists(SQLITE_PATH):
        print(f"No se encontro {SQLITE_PATH}. No hay nada que migrar.")
        return

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    rows = sqlite_conn.execute("SELECT id, content, created_at FROM notes ORDER BY id").fetchall()
    sqlite_conn.close()

    if not rows:
        print("notes.db no tiene notas. No hay nada que migrar.")
        return

    pg_conn = psycopg2.connect(DATABASE_URL)
    try:
        with pg_conn:
            with pg_conn.cursor() as cur:
                for row in rows:
                    cur.execute(
                        """
                        INSERT INTO notes (id, content, created_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (row["id"], row["content"], row["created_at"]),
                    )
                # Reajusta el contador SERIAL para que la siguiente nota
                # nueva no choque con los ids que acabamos de insertar.
                cur.execute(
                    "SELECT setval('notes_id_seq', COALESCE((SELECT MAX(id) FROM notes), 1))"
                )
        print(f"Migradas {len(rows)} notas de SQLite a PostgreSQL.")
    finally:
        pg_conn.close()


if __name__ == "__main__":
    main()
