"""Perceptual comparison of generated scene images using lightweight image fingerprints.

This module compares image pixels, not prompt text or scene metadata. It uses
Pillow-only difference hashes so the analysis stays CPU-friendly on modest PCs.
"""
from __future__ import annotations

import hashlib
from itertools import combinations
from pathlib import Path
from typing import Any


def _fingerprint(path: Path) -> tuple[int, str]:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - depends on deployment extras
        raise RuntimeError("Pillow is required for scene image similarity analysis") from exc

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as source:
        image = source.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(image.getdata())
    bits = 0
    for row in range(8):
        offset = row * 9
        for column in range(8):
            bits = (bits << 1) | int(pixels[offset + column] > pixels[offset + column + 1])
    return bits, digest


def _hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def analyze_scene_image_similarity(
    images: list[dict[str, Any]],
    *,
    max_hamming_distance: int = 6,
) -> dict[str, Any]:
    """Find exact or perceptually near-duplicate images among scene assets."""
    if not 0 <= max_hamming_distance <= 64:
        raise ValueError("max_hamming_distance must be between 0 and 64")

    fingerprints: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for item in images:
        path = Path(str(item.get("path") or ""))
        scene_index = int(item.get("scene_index", -1))
        if not path.is_file():
            skipped.append({"scene_index": scene_index, "reason": "image_file_missing"})
            continue
        try:
            image_hash, sha256 = _fingerprint(path)
        except Exception as exc:  # noqa: BLE001 - report per-image failures
            skipped.append({"scene_index": scene_index, "reason": str(exc)[:180]})
            continue
        fingerprints.append({
            "scene_index": scene_index,
            "image_hash": image_hash,
            "sha256": sha256,
            "width": None,
            "height": None,
        })

    pairs: list[dict[str, Any]] = []
    for left, right in combinations(fingerprints, 2):
        distance = _hamming_distance(left["image_hash"], right["image_hash"])
        exact = left["sha256"] == right["sha256"]
        if exact or distance <= max_hamming_distance:
            pairs.append({
                "scene_indices": [left["scene_index"], right["scene_index"]],
                "match_type": "exact" if exact else "perceptual_near_duplicate",
                "hamming_distance": distance,
                "similarity_percent": round((64 - distance) / 64 * 100, 1),
            })
    pairs.sort(key=lambda pair: (pair["match_type"] != "exact", pair["hamming_distance"]))
    return {
        "status": "duplicates_found" if pairs else "no_duplicates_detected",
        "method": "sha256_and_difference_hash_64",
        "threshold_hamming_distance": max_hamming_distance,
        "image_count": len(fingerprints),
        "compared_pairs": len(fingerprints) * (len(fingerprints) - 1) // 2,
        "duplicate_pairs": pairs,
        "skipped_images": skipped,
        "limitations": [
            "O hash perceptual detecta semelhança estrutural de pixels, não equivalência semântica.",
            "Imagens diferentes do mesmo assunto podem ser sinalizadas; imagens quase iguais com grandes alterações de composição podem escapar.",
            "A análise não identifica personagens, objetos ou qualidade artística.",
            "Revise visualmente cada par antes de excluir ou substituir uma imagem.",
        ],
    }
