from __future__ import annotations

import hashlib
import io
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import exifread
import numpy as np
from flask import Flask, abort, render_template, request, send_file, url_for
from PIL import Image, ImageChops, ImageEnhance, ImageOps
from werkzeug.utils import secure_filename

from forensic import analyze_image

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "instance" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "tif", "tiff", "bmp", "webp"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


def allowed_file(filename: str) -> bool:
    return bool(re.fullmatch(r"[^/\\]+\.(?:jpg|jpeg|png|tif|tiff|bmp|webp)", filename, re.I))


def load_metadata(image_path: Path, original_name: str) -> dict:
    metadata = {"File name": original_name, "File size": f"{image_path.stat().st_size:,} bytes", "SHA-256": hashlib.sha256(image_path.read_bytes()).hexdigest()}
    with image_path.open("rb") as image_file:
        tags = exifread.process_file(image_file, details=False)
    for key, tag in tags.items():
        value = str(tag)
        if key.startswith("GPS "):
            continue
        metadata[key] = value[:500]
    metadata["GPS metadata"] = "Present (coordinates withheld from this report)" if any(key.startswith("GPS ") for key in tags) else "Not present"
    return metadata


def make_ela(image_path: Path) -> bytes:
    with Image.open(image_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
        recompressed = Image.open(buffer).convert("RGB")
        difference = ImageChops.difference(image, recompressed)
        extrema = difference.getextrema()
        scale = 255.0 / max(1, max(channel[1] for channel in extrema))
        output = ImageEnhance.Brightness(difference).enhance(scale)
        result = io.BytesIO()
        output.save(result, format="PNG")
        return result.getvalue()


@app.get("/")
def index():
    return render_template("index.html", report=None, error=None)


@app.post("/analyze")
def analyze():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename:
        return render_template("index.html", report=None, error="Choose an image file to analyze."), 400
    safe_name = secure_filename(uploaded.filename)
    if not safe_name or not allowed_file(safe_name):
        return render_template("index.html", report=None, error="Unsupported file type. Choose JPG, PNG, TIFF, BMP, or WebP."), 400
    data = uploaded.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        return render_template("index.html", report=None, error="The image exceeds the 20 MB upload limit."), 413
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            if image.width * image.height > 40_000_000:
                raise ValueError("Image dimensions exceed the 40 megapixel limit.")
            image_format = image.format
            image.load()
    except (OSError, Image.DecompressionBombError, ValueError) as exc:
        return render_template("index.html", report=None, error=f"This file could not be read as a supported image: {exc}"), 400

    token = uuid.uuid4().hex
    image_path = UPLOAD_DIR / f"{token}.{(image_format or 'img').lower()}"
    image_path.write_bytes(data)
    try:
        created = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        metadata = load_metadata(image_path, safe_name)
        analysis = analyze_image(image_path)
        report = {
            "name": safe_name,
            "size": f"{len(data):,} bytes",
            "dimensions": f"{image.width} × {image.height}",
            "metadata": metadata,
            "analysis": analysis,
            "token": token,
            "created": created,
        }
        receipt = {
            "receipt_version": 1,
            "tool": "PixelProof",
            "report_generated_utc": created,
            "image": {
                "filename": safe_name,
                "size_bytes": len(data),
                "dimensions": report["dimensions"],
                "sha256": metadata["SHA-256"],
            },
            "metadata": metadata,
            "analysis": {
                "ela": {"summary": analysis["ela_note"]},
                "noise_consistency": analysis["noise"],
                "copy_move_candidates": analysis["copy_move"],
            },
            "interpretation_notice": (
                "These heuristic results are indicators for human review, not proof of "
                "authenticity or manipulation. This receipt is not digitally signed "
                "and does not establish a complete chain of custody."
            ),
        }
        (UPLOAD_DIR / f"{token}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    except Exception:
        image_path.unlink(missing_ok=True)
        raise
    return render_template("index.html", report=report, error=None)


@app.get("/image/<token>/<kind>")
def image_output(token: str, kind: str):
    if not re.fullmatch(r"[a-f0-9]{32}", token):
        abort(404)
    matches = [
        path
        for path in UPLOAD_DIR.glob(f"{token}.*")
        if path.suffix.lower().lstrip(".") in ALLOWED_EXTENSIONS
    ]
    if not matches:
        abort(404)
    path = matches[0]
    if kind == "original":
        return send_file(path, as_attachment=False)
    if kind == "ela":
        return send_file(io.BytesIO(make_ela(path)), mimetype="image/png", download_name="ela-analysis.png")
    if kind == "noise":
        result = analyze_image(path)["noise_map"]
        return send_file(io.BytesIO(result), mimetype="image/png", download_name="noise-analysis.png")
    if kind == "copymove":
        result = analyze_image(path)["copy_move_map"]
        return send_file(io.BytesIO(result), mimetype="image/png", download_name="copy-move-analysis.png")
    abort(404)


@app.get("/report/<token>/receipt")
def evidence_receipt(token: str):
    if not re.fullmatch(r"[a-f0-9]{32}", token):
        abort(404)
    receipt_path = UPLOAD_DIR / f"{token}.json"
    if not receipt_path.is_file():
        abort(404)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    return render_template("receipt.html", receipt=receipt), 200, {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Disposition": 'attachment; filename="pixelproof-image-analysis-report.html"',
    }


@app.errorhandler(413)
def too_large(_error):
    return render_template("index.html", report=None, error="The image exceeds the 20 MB upload limit."), 413


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
