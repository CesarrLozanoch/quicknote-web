import os
import sqlite3
from datetime import datetime

from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    db = get_db()
    if query:
        notes = db.execute(
            "SELECT * FROM notes WHERE content LIKE ? ORDER BY id DESC",
            (f"%{query}%",),
        ).fetchall()
    else:
        notes = db.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    return render_template("index.html", notes=notes, query=query)


@app.route("/add", methods=["POST"])
def add_note():
    content = request.form.get("content", "").strip()
    if content:
        created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        db = get_db()
        db.execute(
            "INSERT INTO notes (content, created_at) VALUES (?, ?)",
            (content, created_at),
        )
        db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
