"""Image forensic indicators. These visual heuristics are leads, not proof of editing."""
from __future__ import annotations

import io
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def _encoded_png(array: np.ndarray) -> bytes:
    ok, encoded = cv2.imencode(".png", array)
    if not ok:
        raise ValueError("Could not encode analysis image")
    return encoded.tobytes()


def _noise_analysis(gray: np.ndarray) -> tuple[dict, bytes]:
    blurred = cv2.GaussianBlur(gray, (0, 0), 2.0)
    residual = cv2.absdiff(gray, blurred)
    display = cv2.normalize(residual, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    heatmap = cv2.applyColorMap(display, cv2.COLORMAP_INFERNO)
    tiles = []
    h, w = residual.shape
    for y in range(0, h, max(1, h // 4)):
        for x in range(0, w, max(1, w // 4)):
            tile = residual[y:min(y + max(1, h // 4), h), x:min(x + max(1, w // 4), w)]
            if tile.size:
                tiles.append(float(tile.std()))
    spread = float(np.std(tiles)) if len(tiles) > 1 else 0.0
    return {"residual_mean": round(float(residual.mean()), 2), "regional_spread": round(spread, 2), "interpretation": "Noise varies noticeably across image regions; inspect the heatmap and compare similar textures." if spread > 4 else "No strong regional noise variation was measured by this simple heuristic."}, _encoded_png(heatmap)


def _copy_move_analysis(bgr: np.ndarray) -> tuple[dict, bytes]:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=2500, scaleFactor=1.2, nlevels=8)
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    output = bgr.copy()
    pairs = []
    if descriptors is not None and len(keypoints) >= 2:
        matches = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(descriptors, descriptors, k=2)
        h, w = gray.shape
        minimum_separation = max(18.0, min(h, w) * 0.04)
        for pair in matches:
            if len(pair) != 2:
                continue
            first, second = pair
            if first.queryIdx == first.trainIdx or first.distance >= 0.72 * second.distance:
                continue
            p1 = np.array(keypoints[first.queryIdx].pt)
            p2 = np.array(keypoints[first.trainIdx].pt)
            if np.linalg.norm(p1 - p2) >= minimum_separation:
                pairs.append((p1, p2))
        pairs = pairs[:100]
        for p1, p2 in pairs:
            a, b = tuple(np.round(p1).astype(int)), tuple(np.round(p2).astype(int))
            cv2.circle(output, a, 10, (0, 220, 255), 2)
            cv2.circle(output, b, 10, (0, 80, 255), 2)
            cv2.line(output, a, b, (255, 255, 0), 1)
    count = len(pairs)
    return {"candidate_pairs": count, "interpretation": f"{count} spatially separated similar feature pairs were found. Repeated texture can cause false matches; this is a review aid, not a forgery verdict." if count else "No convincing spatially separated ORB feature pairs were found. This does not rule out copy-move editing."}, _encoded_png(output)


def analyze_image(path: Path) -> dict:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        rgb = np.asarray(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    noise, noise_png = _noise_analysis(gray)
    copy_move, copy_png = _copy_move_analysis(bgr)
    return {
        "noise": noise,
        "copy_move": copy_move,
        "noise_map": noise_png,
        "copy_move_map": copy_png,
        "ela_note": "ELA recompresses the image as JPEG and visualizes pixel differences. Strong differences may arise from editing, but also from image content, format, or prior compression.",
    }
