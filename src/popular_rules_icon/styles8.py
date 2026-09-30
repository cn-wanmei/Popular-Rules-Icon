"""Eight visual styles from a square source raster."""
from __future__ import annotations
from io import BytesIO
from typing import Callable
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

StyleFn = Callable[[Image.Image, int], Image.Image]
STYLES = (
    "source_original", "glassmorphism", "soft_3d", "neo_skeuomorphism",
    "minimalist", "duotone_line", "mbe", "y2k",
)

def _sq(img: Image.Image, size: int) -> Image.Image:
    img = img.convert("RGBA")
    img = ImageOps.contain(img, (size, size), method=Image.Resampling.LANCZOS)
    c = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c.paste(img, ((size - img.width)//2, (size - img.height)//2), img)
    return c

def style_source_original(img, size): return _sq(img, size)

def style_glassmorphism(img, size):
    base = _sq(img, size)
    blur = base.filter(ImageFilter.GaussianBlur(radius=max(1, size//48)))
    panel = Image.new("RGBA", (size, size), (255, 255, 255, 90))
    out = Image.alpha_composite(Image.alpha_composite(blur, panel), base)
    d = ImageDraw.Draw(out)
    m = max(2, size//64)
    d.rounded_rectangle([m, m, size-m-1, size-m-1], radius=size//8, outline=(255,255,255,140), width=m)
    return out

def style_soft_3d(img, size):
    base = _sq(img, size)
    s = base.split()[-1].point(lambda a: int(a*0.35))
    sh = Image.merge("RGBA", (Image.new("L",(size,size),0),)*3 + (s,))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=size//18))
    canvas = Image.new("RGBA", (size, size), (0,0,0,0))
    off = max(2, size//32)
    canvas.paste(sh, (off, off), sh)
    return ImageEnhance.Contrast(Image.alpha_composite(canvas, base)).enhance(1.05)

def style_neo_skeuomorphism(img, size):
    base = _sq(img, size)
    plate = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(plate)
    m = size//16
    d.rounded_rectangle([m,m,size-m,size-m], radius=size//6, fill=(230,230,235,255))
    d.arc([m,m,size-m,size//2], 200, 340, fill=(255,255,255,180), width=max(2,size//64))
    icon = ImageOps.contain(base, (int(size*0.72), int(size*0.72)), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", (size, size), (0,0,0,0))
    layer.paste(icon, ((size-icon.width)//2, (size-icon.height)//2), icon)
    return Image.alpha_composite(plate, layer)

def style_minimalist(img, size):
    base = _sq(img, size)
    g = ImageEnhance.Color(base).enhance(0.85)
    bg = Image.new("RGBA", (size, size), (250,250,250,255))
    return Image.alpha_composite(bg, g)

def style_duotone_line(img, size):
    base = _sq(img, size)
    gray = base.convert("L")
    tinted = ImageOps.colorize(gray, black="#0b1f3a", white="#5ec8ff").convert("RGBA")
    tinted.putalpha(base.split()[-1])
    edges = base.split()[-1].filter(ImageFilter.FIND_EDGES)
    outline = Image.merge("RGBA", (Image.new("L",(size,size),20),)*3 + (edges,))
    return Image.alpha_composite(tinted, outline)

def style_mbe(img, size):
    base = _sq(img, size)
    bg = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(bg)
    m = size//12
    d.rounded_rectangle([m,m,size-m,size-m], radius=size//5, fill=(255,214,102,255))
    icon = ImageOps.contain(base, (int(size*0.62), int(size*0.62)), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", (size, size), (0,0,0,0))
    layer.paste(icon, ((size-icon.width)//2, (size-icon.height)//2), icon)
    return Image.alpha_composite(bg, layer)

def style_y2k(img, size):
    base = _sq(img, size)
    e = ImageEnhance.Contrast(ImageEnhance.Color(base).enhance(1.4)).enhance(1.15)
    r,g,b,a = e.split()
    shifted = Image.merge("RGBA", (b,g,r,a))
    shifted = Image.blend(e, shifted, 0.25)
    glow = shifted.filter(ImageFilter.GaussianBlur(radius=size//40))
    return Image.alpha_composite(glow, shifted)

RENDERERS = {
    "source_original": style_source_original,
    "glassmorphism": style_glassmorphism,
    "soft_3d": style_soft_3d,
    "neo_skeuomorphism": style_neo_skeuomorphism,
    "minimalist": style_minimalist,
    "duotone_line": style_duotone_line,
    "mbe": style_mbe,
    "y2k": style_y2k,
}

def render_all_styles(src_bytes: bytes, sizes=(128, 256)) -> dict[str, bytes]:
    img = Image.open(BytesIO(src_bytes))
    out = {}
    for name, fn in RENDERERS.items():
        for size in sizes:
            rgba = fn(img, size)
            buf = BytesIO()
            rgba.convert("RGBA").save(buf, format="PNG", optimize=True)
            out[f"{name}:{size}:png"] = buf.getvalue()
    return out
