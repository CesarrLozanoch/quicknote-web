import os
import uuid
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Un poco mas que MAX_FILE_SIZE para dejar margen al resto del formulario.
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE + (1 * 1024 * 1024)

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


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(413)
def file_too_large(_error):
    flash("El archivo adjunto no puede superar los 5MB.")
    return redirect(url_for("index"))


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


MAX_CONTENT_CHARS = 1000


@app.route("/add", methods=["POST"])
def add_note():
    content = request.form.get("content", "").strip()

    if not content:
        return redirect(url_for("index"))

    if len(content) > MAX_CONTENT_CHARS:
        flash(f"La nota no puede superar los {MAX_CONTENT_CHARS} caracteres.")
        return redirect(url_for("index"))

    attachment_filename = None
    attachment_original_name = None

    file = request.files.get("attachment")
    if file and file.filename:
        if not allowed_file(file.filename):
            flash("Solo se permiten imágenes (jpg, png, gif, webp) o archivos PDF.")
            return redirect(url_for("index"))

        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_FILE_SIZE:
            flash("El archivo adjunto no puede superar los 5MB.")
            return redirect(url_for("index"))

        extension = file.filename.rsplit(".", 1)[1].lower()
        attachment_filename = f"{uuid.uuid4().hex}.{extension}"
        attachment_original_name = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, attachment_filename))

    created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO notes (content, created_at, attachment_filename, attachment_original_name)
            VALUES (%s, %s, %s, %s)
            """,
            (content, created_at, attachment_filename, attachment_original_name),
        )
    db.commit()
    return redirect(url_for("index"))


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT attachment_filename FROM notes WHERE id = %s", (note_id,))
        note = cur.fetchone()
        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    db.commit()

    if note and note["attachment_filename"]:
        file_path = os.path.join(UPLOAD_FOLDER, note["attachment_filename"])
        if os.path.exists(file_path):
            os.remove(file_path)

    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
