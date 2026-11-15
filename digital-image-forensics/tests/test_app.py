from __future__ import annotations

import hashlib
import io
import re

from PIL import Image

import app as pixelproof


def test_valid_jpeg_upload_renders_metadata_and_all_analysis_sections(client, jpeg_bytes):
    response = client.post(
        "/analyze",
        data={"image": (io.BytesIO(jpeg_bytes), "evidence-sample.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "evidence-sample.jpg" in page
    assert "240 × 180" in page
    assert hashlib.sha256(jpeg_bytes).hexdigest() in page
    assert "Image metadata" in page
    assert "Error Level Analysis" in page
    assert "Noise consistency" in page
    assert "Copy-move candidates" in page
    assert "Regional spread" in page
    assert "Candidate pairs" in page


def test_missing_file_returns_clear_error(client):
    response = client.post("/analyze", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"Choose an image file to analyze" in response.data


def test_unsupported_extension_returns_clear_error(client):
    response = client.post(
        "/analyze",
        data={"image": (io.BytesIO(b"not an image"), "notes.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert b"Unsupported file type" in response.data


def test_corrupt_image_with_supported_extension_returns_clear_error(client):
    response = client.post(
        "/analyze",
        data={"image": (io.BytesIO(b"not really jpeg"), "broken.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert b"could not be read as a supported image" in response.data


def test_upload_larger_than_20_megabytes_is_rejected(client):
    oversized = b"x" * (pixelproof.MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/analyze",
        data={"image": (io.BytesIO(oversized), "large.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 413
    assert b"20 MB upload limit" in response.data


def test_image_over_40_megapixels_is_rejected(client, monkeypatch):
    class OversizedImage:
        width = 8001
        height = 5000
        format = "JPEG"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def verify(self):
            pass

        def load(self):
            pass

    monkeypatch.setattr(pixelproof.Image, "open", lambda *_args, **_kwargs: OversizedImage())
    response = client.post(
        "/analyze",
        data={"image": (io.BytesIO(b"image placeholder"), "large-dimensions.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert b"40 megapixel limit" in response.data


def test_analysis_image_endpoints_return_decodable_pngs(client, jpeg_bytes):
    upload = client.post(
        "/analyze",
        data={"image": (io.BytesIO(jpeg_bytes), "analysis.jpg")},
        content_type="multipart/form-data",
    )
    assert upload.status_code == 200
    page = upload.get_data(as_text=True)
    token_match = re.search(r"/image/([a-f0-9]{32})/original", page)
    assert token_match, "Expected report to link to the uploaded original"
    token = token_match.group(1)

    for kind in ("ela", "noise", "copymove"):
        response = client.get(f"/image/{token}/{kind}")
        assert response.status_code == 200
        assert response.mimetype == "image/png"
        with Image.open(io.BytesIO(response.data)) as result:
            assert result.format == "PNG"
            assert result.width > 0 and result.height > 0


def test_evidence_report_download_contains_integrity_and_analysis_details(client, jpeg_bytes):
    upload = client.post(
        "/analyze",
        data={"image": (io.BytesIO(jpeg_bytes), "receipt-sample.jpg")},
        content_type="multipart/form-data",
    )
    token_match = re.search(r"/report/([a-f0-9]{32})/receipt", upload.get_data(as_text=True))
    assert token_match, "Expected report to offer an evidence receipt download"

    response = client.get(f"/report/{token_match.group(1)}/receipt")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert "attachment" in response.headers["Content-Disposition"]
    page = response.get_data(as_text=True)
    assert "Image analysis report" in page
    assert "receipt-sample.jpg" in page
    assert hashlib.sha256(jpeg_bytes).hexdigest() in page
    assert "Error Level Analysis" in page
    assert "Noise consistency" in page
    assert "Copy-move feature candidates" in page
    assert "Image metadata" in page
    assert "GPS metadata" in page
    assert "Not present" in page
    assert "not digitally signed" in page
