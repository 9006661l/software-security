"""
Tiny sample web app for Week 1 threat modeling.
You will NOT exploit this in Week 1 — you will draw a data-flow diagram
and apply STRIDE to its components (web client, app, SQLite DB, /upload).
"""
from flask import Flask, request, jsonify, send_from_directory
import sqlite3, os, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
DB = "notes.db"
UPLOAD_DIR = "uploads"
ALLOWED = {".png",".jpg", ".pdf", ".txt"}
app.config["MAX_CONTENT_LENGTH"]=2*1024*1024
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    con.commit(); con.close()

@app.route("/notes", methods=["GET", "POST"])
def notes():
    con = sqlite3.connect(DB)
    if request.method == "POST":
        owner = request.json.get("owner", "anon")
        body = request.json.get("body", "")
        con.execute("INSERT INTO notes (owner, body) VALUES (?, ?)", (owner, body))
        con.commit()
    rows = con.execute("SELECT id, owner, body FROM notes").fetchall()
    con.close()
    return jsonify(rows)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    ext = os.path.splitext(secure_filename(f.filename))[1].lower()
    if ext not in ALLOWED:
    	return {"error": "type not allowed"}, 400
    stored = uuid.uuid4().hex + ext
    path = os.path.realpath(os.path.join(UPLOAD_DIR, stored))
    if not path.startswith(os.path.realpath(UPLOAD_DIR) + os.sep):
    	return {"error": "bad path"}, 400
    f.save(path)
    return {"saved": stored}
@app.route("/files/<name>")
def files(name):
    return send_from_directory(UPLOAD_DIR, name)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
