import io
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple


# Skin tone classification by Lab lightness range
SKIN_TONE_MAP = [
    ("Fair / Light", "#FDDBB4", ["navy", "burgundy", "forest green", "rose gold"], ["Pastel", "Cool Neutrals", "Jewel Tones"]),
    ("Light / Medium", "#E8B88A", ["cobalt blue", "emerald", "deep purple", "crisp white"], ["Warm Neutrals", "Earth Tones", "Bold Colors"]),
    ("Medium / Warm", "#C68642", ["warm orange", "terracotta", "olive", "coral"], ["Earthy Tones", "Warm Pastels", "Rich Colors"]),
    ("Medium / Dark", "#8D5524", ["mustard yellow", "rust", "sage green", "warm beige"], ["Warm Earth Tones", "Spice Colors", "Autumnal"]),
    ("Dark / Deep", "#4A2912", ["bright white", "electric blue", "hot pink", "gold", "lime"], ["Vibrant Colors", "High Contrast", "Jewel Tones"]),
]

BODY_TYPE_STYLES = {
    "Petite": {
        "styles": ["A-line dresses", "Vertical stripes", "High-waist bottoms", "Monochrome outfits", "Fitted silhouettes"],
        "avoid": ["Oversized tops", "Horizontal wide stripes", "Ankle strap shoes"],
    },
    "Tall / Slim": {
        "styles": ["Wide-leg pants", "Layered outfits", "Bold patterns", "Maxi dresses", "Horizontal stripes"],
        "avoid": ["Very cropped tops without bottoms"],
    },
    "Athletic / Straight": {
        "styles": ["Peplum tops", "A-line skirts", "Wrap dresses", "Ruffled details", "Off-shoulder tops"],
        "avoid": ["Boxy oversized silhouettes"],
    },
    "Hourglass": {
        "styles": ["Wrap dresses", "Bodycon", "Belted outfits", "Fit-and-flare", "Bootcut jeans"],
        "avoid": ["Shapeless sacks", "Oversized everything"],
    },
    "Pear / Triangle": {
        "styles": ["A-line skirts", "Wide-leg pants", "Statement tops", "Boat necklines", "Off-shoulder"],
        "avoid": ["Tight skirts", "Tapered pants"],
    },
    "Apple / Round": {
        "styles": ["Empire waist", "V-necklines", "Wrap tops", "Straight-leg pants", "Dark bottoms"],
        "avoid": ["Clingy fabrics", "Tight waistbands"],
    },
}


def _get_dominant_color(image: Image.Image, sample_region: Tuple) -> np.ndarray:
    """Extract dominant color from a region of the image."""
    region = image.crop(sample_region)
    region = region.resize((50, 50))
    arr = np.array(region.convert("RGB"))
    pixels = arr.reshape(-1, 3).astype(float)
    return pixels.mean(axis=0)


def _classify_skin_tone(rgb: np.ndarray) -> Tuple[str, str, List[str], List[str]]:
    """Map average RGB to a skin tone category."""
    r, g, b = rgb
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    if brightness > 210:
        return SKIN_TONE_MAP[0]
    elif brightness > 180:
        return SKIN_TONE_MAP[1]
    elif brightness > 140:
        return SKIN_TONE_MAP[2]
    elif brightness > 100:
        return SKIN_TONE_MAP[3]
    else:
        return SKIN_TONE_MAP[4]


def _estimate_body_type(image: Image.Image) -> str:
    """
    Heuristic body-type estimate based on image aspect ratio.
    In a real system, this would use pose estimation (MediaPipe/OpenPose).
    """
    w, h = image.size
    ratio = h / w if w > 0 else 1.5

    if ratio > 2.2:
        return "Tall / Slim"
    elif ratio > 1.8:
        return "Athletic / Straight"
    elif ratio > 1.4:
        return "Hourglass"
    elif ratio > 1.0:
        return "Pear / Triangle"
    else:
        return "Petite"


def analyze_photo(image_bytes: bytes) -> Dict:
    """
    Analyze an uploaded photo and return skin tone, body type,
    recommended colors, and recommended styles.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = image.size

    # Sample from the upper-center quarter (face region approximation)
    cx, cy = w // 2, h // 4
    margin = min(w, h) // 6
    left = max(0, cx - margin)
    top = max(0, cy - margin)
    right = min(w, cx + margin)
    bottom = min(h, cy + margin)

    dominant_rgb = _get_dominant_color(image, (left, top, right, bottom))
    tone_name, tone_hex, rec_colors, rec_styles = _classify_skin_tone(dominant_rgb)
    body_type = _estimate_body_type(image)

    body_info = BODY_TYPE_STYLES.get(body_type, {"styles": ["Versatile silhouettes"], "avoid": []})

    analysis_text = (
        f"Based on your photo, you have a **{tone_name}** skin tone. "
        f"Your body type appears **{body_type}**. "
        f"You suit {rec_styles[0]} color palettes — try {rec_colors[0]} and {rec_colors[1]}. "
        f"Best styles for you: {', '.join(body_info['styles'][:3])}."
    )

    return {
        "skin_tone": tone_name,
        "skin_tone_hex": tone_hex,
        "body_type": body_type,
        "recommended_colors": rec_colors,
        "recommended_styles": body_info["styles"],
        "analysis_result": analysis_text,
    }
