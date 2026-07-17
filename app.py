import os
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, url_for

load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "No se encontro la variable de entorno DATABASE_URL. "
        "Define un archivo .env en local (mira .env.example) o configurala en Render."
    )


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    db = get_db()
    with db.cursor() as cur:
        if query:
            cur.execute(
                "SELECT * FROM notes WHERE content ILIKE %s ORDER BY id DESC",
                (f"%{query}%",),
            )
        else:
            cur.execute("SELECT * FROM notes ORDER BY id DESC")
        notes = cur.fetchall()
    return render_template("index.html", notes=notes, query=query)


@app.route("/add", methods=["POST"])
def add_note():
    content = request.form.get("content", "").strip()
    if content:
        created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (content, created_at) VALUES (%s, %s)",
                (content, created_at),
            )
        db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
