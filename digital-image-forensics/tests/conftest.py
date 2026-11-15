from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

import app as pixelproof


@pytest.fixture

def client(tmp_path, monkeypatch):
    """Provide an isolated Flask test client and upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(pixelproof, "UPLOAD_DIR", upload_dir)
    pixelproof.app.config.update(TESTING=True)
    with pixelproof.app.test_client() as test_client:
        yield test_client


@pytest.fixture

def jpeg_bytes():
    """Create a deterministic textured JPEG with no external image files."""
    rng = np.random.default_rng(2026)
    pixels = rng.integers(0, 256, size=(180, 240, 3), dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(pixels).save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()
