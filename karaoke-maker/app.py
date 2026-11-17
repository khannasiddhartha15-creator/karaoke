"""Flask server: upload a song, get back a karaoke track."""
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from processor import OUTPUT_DIR, demucs_available, make_karaoke

BASE = Path(__file__).parent
UPLOAD_DIR = BASE / "uploads"
ALLOWED = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB


@app.get("/")
def index():
    return render_template("index.html", ai_ready=demucs_available())


@app.post("/api/karaoke")
def karaoke():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(error="No file received."), 400
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED:
        return jsonify(error=f"Unsupported format. Use: {', '.join(sorted(ALLOWED))}"), 400

    job_id = uuid.uuid4().hex[:10]
    saved = UPLOAD_DIR / f"{job_id}{ext}"
    file.save(saved)
    try:
        out, used = make_karaoke(saved, job_id, request.form.get("method", "auto"))
    except Exception as e:  # show a readable error to the user
        return jsonify(error=str(e)), 500
    finally:
        saved.unlink(missing_ok=True)

    return jsonify(url=f"/files/{job_id}/{out.name}", method=used,
                   name=Path(file.filename).stem + "_karaoke.mp3")


@app.get("/files/<job_id>/<name>")
def files(job_id, name):
    return send_from_directory(OUTPUT_DIR / job_id, name)


if __name__ == "__main__":
    app.run(debug=True)
