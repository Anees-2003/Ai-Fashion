"""
local_image_gen.py  —  Pillow-only fashion image generator (pure RGB, base64 output)
Returns a data: URI embedded directly in the API response.
No file path, no StaticFiles, no Vite proxy, no external API.
"""
import io
import base64
import uuid
import hashlib
from PIL import Image, ImageDraw


# ── Themed colour palettes per prompt keyword ──────────────────────────────
_PALETTES = {
    "royal blue":  [(15, 30, 90),    (40, 80, 180),   (100, 140, 220)],
    "silk":        [(180, 140, 100), (220, 190, 150),  (240, 220, 200)],
    "ivory":       [(200, 185, 160), (225, 210, 188),  (245, 233, 215)],
    "bridal":      [(210, 170, 175), (230, 195, 200),  (245, 220, 225)],
    "lehenga":     [(160, 40, 80),   (210, 90, 130),   (240, 160, 190)],
    "black":       [(20, 20, 28),    (38, 38, 52),     (62, 62, 82)],
    "red":         [(130, 18, 28),   (195, 48, 58),    (235, 95, 105)],
    "velvet":      [(75, 18, 75),    (115, 38, 115),   (155, 75, 155)],
    "dusty rose":  [(185, 138, 138), (218, 172, 172),  (238, 205, 205)],
    "gold":        [(140, 105, 18),  (192, 155, 38),   (225, 190, 75)],
    "beige":       [(195, 180, 160), (218, 202, 185),  (238, 225, 210)],
    "minimalist":  [(210, 208, 205), (228, 226, 222),  (242, 240, 238)],
    "bohemian":    [(155, 95, 55),   (195, 140, 85),   (228, 185, 135)],
    "floral":      [(120, 185, 130), (90, 155, 120),   (60, 125, 105)],
    "cocktail":    [(55, 18, 75),    (95, 38, 125),    (145, 75, 175)],
    "saree":       [(195, 75, 38),   (225, 115, 58),   (252, 165, 98)],
    "banarasi":    [(145, 75, 18),   (185, 115, 38),   (218, 160, 75)],
    "suit":        [(28, 48, 78),    (48, 78, 118),    (78, 108, 152)],
    "maxi":        [(55, 125, 95),   (85, 160, 125),   (125, 195, 160)],
    "casual":      [(75, 115, 175),  (115, 155, 205),  (165, 195, 232)],
    "formal":      [(28, 42, 68),    (52, 78, 118),    (88, 118, 162)],
    "festive":     [(175, 75, 28),   (218, 125, 48),   (248, 175, 88)],
    "linen":       [(185, 175, 155), (210, 200, 185),  (232, 225, 212)],
}
_PALETTE_LIST = list(_PALETTES.values())


def _pick_palette(prompt: str):
    p = prompt.lower()
    for kw, pal in _PALETTES.items():
        if kw in p:
            return pal
    idx = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % len(_PALETTE_LIST)
    return _PALETTE_LIST[idx]


def _lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _gradient(draw, w, h, top, mid, bot):
    half = h // 2
    for y in range(h):
        if y < half:
            color = _lerp(top, mid, y / half)
        else:
            color = _lerp(mid, bot, (y - half) / half)
        draw.line([(0, y), (w, y)], fill=color)


def _silhouette(draw, w, h, garment, trim):
    cx = w // 2
    neck_y    = int(h * 0.13);  neck_hw   = int(w * 0.11)
    sh_y      = int(h * 0.19);  sh_hw     = int(w * 0.28)
    waist_y   = int(h * 0.47);  waist_hw  = int(w * 0.13)
    hem_y     = int(h * 0.87);  hem_hw    = int(w * 0.39)

    body = [
        (cx - neck_hw,  neck_y),
        (cx - sh_hw,    sh_y),
        (cx - waist_hw, waist_y),
        (cx - hem_hw,   hem_y),
        (cx + hem_hw,   hem_y),
        (cx + waist_hw, waist_y),
        (cx + sh_hw,    sh_y),
        (cx + neck_hw,  neck_y),
    ]
    draw.polygon(body, fill=garment)
    draw.polygon(body, outline=trim, width=2)

    # Highlight on left bodice
    hi = _lerp(garment, (255, 255, 255), 0.28)
    draw.polygon([
        (cx - sh_hw + 8,    sh_y + 12),
        (cx - waist_hw + 5, waist_y),
        (cx - waist_hw + 20, waist_y),
        (cx - sh_hw + 22,   sh_y + 12),
    ], fill=hi)

    # Neckline arc
    draw.arc([cx - neck_hw, neck_y - int(h*0.035),
              cx + neck_hw, neck_y + int(h*0.015)],
             start=200, end=340, fill=trim, width=2)

    # Belt
    by = waist_y - 5
    draw.rectangle([cx - waist_hw - 2, by, cx + waist_hw + 2, by + 8], fill=trim)

    # Hem line
    draw.line([(cx - hem_hw + 6, hem_y - 4), (cx + hem_hw - 6, hem_y - 4)],
              fill=trim, width=2)


def _frame(draw, w, h, color):
    m = 11
    bright = _lerp(color, (255, 255, 255), 0.4)
    draw.rectangle([m, m, w - m, h - m], outline=color, width=1)
    for (x, y, dx, dy) in [(m, m, 1, 1), (w-m, m, -1, 1),
                            (m, h-m, 1, -1), (w-m, h-m, -1, -1)]:
        draw.line([(x, y), (x + dx*22, y)], fill=bright, width=2)
        draw.line([(x, y), (x, y + dy*22)], fill=bright, width=2)


def _label(draw, w, h, prompt, palette):
    bar_h = int(h * 0.11)
    bar_y = h - bar_h
    bar_c = tuple(max(0, c - 45) for c in palette[0])
    draw.rectangle([0, bar_y, w, h], fill=bar_c)
    trim = _lerp(palette[2], (255, 255, 255), 0.25)
    draw.line([(0, bar_y), (w, bar_y)], fill=trim, width=1)

    # Title
    title = "AI Fashion Design"
    tw = len(title) * 7
    draw.text((w // 2 - tw // 2, bar_y + 10), title, fill=trim)

    # Excerpt
    excerpt = (prompt[:30] + "...") if len(prompt) > 30 else prompt
    ew = len(excerpt) * 6
    draw.text((w // 2 - ew // 2, bar_y + 28), excerpt, fill=(215, 210, 200))


def _swatches(draw, w, h, palette):
    sw, gap, m = 14, 5, 13
    total = len(palette) * (sw + gap) - gap
    x0 = w - m - total
    y0 = h - m - sw
    for i, c in enumerate(palette):
        x = x0 + i * (sw + gap)
        draw.ellipse([x, y0, x + sw, y0 + sw],
                     fill=c, outline=_lerp(c, (255, 255, 255), 0.45))


# ── Public API ─────────────────────────────────────────────────────────────

def generate_fashion_image_b64(prompt: str,
                                width: int = 512,
                                height: int = 768) -> str:
    """
    Generate a fashion design image with Pillow and return it as a
    base64 data URI:  data:image/jpeg;base64,<...>

    The caller embeds this string directly in the JSON response as
    `generated_image_url`. The browser renders it with a plain <img src=...>.
    No file I/O, no StaticFiles, no proxy needed.
    """
    palette = _pick_palette(prompt)
    top, mid, bot = palette[0], palette[1], palette[2]
    garment = mid
    trim = _lerp(palette[2], (255, 255, 255), 0.38)

    img = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(img)

    _gradient(draw, width, height, top, mid, bot)

    # Dot texture
    dot = _lerp(top, (255, 255, 255), 0.07)
    for yy in range(0, height, 22):
        for xx in range(0, width, 22):
            draw.point((xx, yy), fill=dot)

    _silhouette(draw, width, height, garment, trim)
    _frame(draw, width, height, _lerp(palette[2], (255, 255, 255), 0.2))
    _label(draw, width, height, prompt, palette)
    _swatches(draw, width, height, palette)

    # Encode to JPEG in memory → base64 data URI
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"
