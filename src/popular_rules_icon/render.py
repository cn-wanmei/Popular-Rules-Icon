"""Build-time raster delivery helpers (no decorative styles yet)."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image

from .hashutil import variant_hash
from . import POLICY_VERSION, RENDERER_VERSION


def load_image(data: bytes) -> Image.Image:
    img = Image.open(BytesIO(data))
    img.load()
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    return img


def native_px(img: Image.Image) -> int:
    return min(img.size)


def fit_square_png(data: bytes, size: int, *, max_upscale: float = 1.0) -> tuple[bytes, int]:
    """Return PNG bytes and native_px. Never upscale beyond max_upscale * native."""
    img = load_image(data)
    nat = native_px(img)
    target = size
    max_side = int(nat * max_upscale) if nat > 0 else size
    if target > max_side:
        target = max(max_side, 1)
    # letterbox to square canvas with transparency
    img = img.convert("RGBA")
    w, h = img.size
    scale = min(target / w, target / h, 1.0) if max_upscale <= 1.0 else min(target / w, target / h)
    # allow upscale only within max_upscale
    max_dim = max(w, h)
    allowed = max_dim * max_upscale
    out_side = min(size, int(allowed)) if max_upscale <= 1.0 else size
    out_side = max(out_side, 1)
    scale = min(out_side / w, out_side / h)
    nw, nh = max(int(w * scale), 1), max(int(h * scale), 1)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (out_side, out_side), (0, 0, 0, 0))
    canvas.paste(resized, ((out_side - nw) // 2, (out_side - nh) // 2), resized)
    buf = BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), nat


def delivery_variant_key(style: str, size: int, fmt: str = "png") -> str:
    return f"{style}:{size}:{fmt}"


def make_source_original_png(
    object_hash: str,
    source_bytes: bytes,
    *,
    size: int = 256,
    max_upscale: float = 1.0,
) -> tuple[str, bytes, int]:
    png, nat = fit_square_png(source_bytes, size, max_upscale=max_upscale)
    vh = variant_hash(
        object_hash,
        renderer_version=RENDERER_VERSION,
        style="source_original",
        size=size,
        fmt="png",
        policy_version=POLICY_VERSION,
    )
    return vh, png, nat
