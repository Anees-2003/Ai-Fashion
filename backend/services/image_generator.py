import requests
import urllib.parse
import random
from typing import Dict, List


FASHION_STYLE_SUFFIX = (
    ", fashion design, studio lighting, white background, "
    "professional clothing photography, high detail, 4k"
)

STYLE_ATTRIBUTES = {
    "office": {"category": "Formal Wear", "fabric": "Wool Blend / Polyester", "occasion": "Office / Business"},
    "casual": {"category": "Casual Wear", "fabric": "Cotton / Denim", "occasion": "Everyday / Casual"},
    "wedding": {"category": "Ethnic / Bridal", "fabric": "Silk / Georgette", "occasion": "Wedding / Festive"},
    "lehenga": {"category": "Ethnic / Bridal", "fabric": "Silk / Net / Georgette", "occasion": "Wedding / Festive"},
    "saree": {"category": "Traditional Ethnic", "fabric": "Silk / Cotton Silk", "occasion": "Festive / Cultural"},
    "hoodie": {"category": "Streetwear", "fabric": "Fleece / Cotton Terry", "occasion": "Casual / Streetwear"},
    "streetwear": {"category": "Streetwear", "fabric": "Cotton / Synthetic Blend", "occasion": "Casual / Urban"},
    "kurthi": {"category": "Ethnic Fusion", "fabric": "Cotton / Chiffon", "occasion": "Casual / Semi-Formal"},
    "gown": {"category": "Evening Wear", "fabric": "Satin / Chiffon / Velvet", "occasion": "Party / Formal Evening"},
    "dress": {"category": "Western Wear", "fabric": "Cotton / Jersey / Crepe", "occasion": "Casual / Party"},
    "suit": {"category": "Formal Wear", "fabric": "Wool / Linen", "occasion": "Business / Formal"},
    "blazer": {"category": "Smart Casual / Formal", "fabric": "Wool Blend / Polyester", "occasion": "Office / Semi-Formal"},
    "denim": {"category": "Casual Wear", "fabric": "Denim", "occasion": "Everyday / Casual"},
    "ethnic": {"category": "Ethnic / Traditional", "fabric": "Silk / Cotton", "occasion": "Festive / Cultural"},
    "traditional": {"category": "Traditional Ethnic", "fabric": "Handloom Cotton / Silk", "occasion": "Cultural / Festive"},
    "minimalist": {"category": "Minimalist / Contemporary", "fabric": "Cotton / Linen", "occasion": "Everyday / Office"},
    "party": {"category": "Party Wear", "fabric": "Sequin / Satin / Velvet", "occasion": "Party / Night Out"},
    "summer": {"category": "Summer / Resort Wear", "fabric": "Linen / Cotton / Crepe", "occasion": "Vacation / Casual"},
    "winter": {"category": "Winter Wear", "fabric": "Wool / Fleece / Cashmere", "occasion": "Cold Weather / Casual"},
    "sporty": {"category": "Activewear / Athleisure", "fabric": "Polyester / Spandex", "occasion": "Sports / Gym"},
}

COLOR_KEYWORDS = {
    "black": ["#1a1a1a", "#2d2d2d", "#404040"],
    "white": ["#FFFFFF", "#F5F5F5", "#FAFAFA"],
    "red": ["#D32F2F", "#E53935", "#FF5252"],
    "blue": ["#1565C0", "#1976D2", "#42A5F5"],
    "navy": ["#0D1B2A", "#1A2744", "#2C3E6B"],
    "green": ["#2E7D32", "#388E3C", "#66BB6A"],
    "pink": ["#C2185B", "#E91E63", "#F48FB1"],
    "purple": ["#6A1B9A", "#7B1FA2", "#CE93D8"],
    "yellow": ["#F9A825", "#FBC02D", "#FFF176"],
    "orange": ["#E65100", "#F57C00", "#FFCC80"],
    "grey": ["#424242", "#616161", "#BDBDBD"],
    "brown": ["#4E342E", "#6D4C41", "#A1887F"],
    "beige": ["#D7CCC8", "#BCAAA4", "#F5F0EB"],
    "pastel": ["#B2EBF2", "#F8BBD9", "#DCEDC8"],
    "gold": ["#FFD700", "#FFC107", "#FFCA28"],
    "neon": ["#39FF14", "#FF073A", "#00FFFF"],
    "maroon": ["#880E4F", "#AD1457", "#C62828"],
    "ivory": ["#FFFFF0", "#F5F5DC", "#FAEBD7"],
    "teal": ["#00695C", "#00838F", "#4DB6AC"],
}


def extract_colors(prompt: str) -> List[str]:
    prompt_lower = prompt.lower()
    found_colors = []
    for color, hexes in COLOR_KEYWORDS.items():
        if color in prompt_lower:
            found_colors.extend(hexes)
    if not found_colors:
        found_colors = ["#2d2d2d", "#F5F5F5", "#D7CCC8"]
    return found_colors[:6]


def extract_style(prompt: str) -> Dict:
    prompt_lower = prompt.lower()
    for keyword, attrs in STYLE_ATTRIBUTES.items():
        if keyword in prompt_lower:
            return attrs
    return {
        "category": "Fashion / Contemporary",
        "fabric": "Mixed / Designer Blend",
        "occasion": "General / Versatile"
    }


def generate_fashion_image(prompt: str) -> str:
    """
    Generate a fashion design image using Pollinations.ai (free, no key required).
    Returns the direct image URL — the browser fetches the image asynchronously.
    Uses a random seed so each generation is unique.
    """
    enhanced_prompt = prompt + FASHION_STYLE_SUFFIX
    encoded = urllib.parse.quote(enhanced_prompt)
    seed = random.randint(1, 99999)
    # Proven stable URL format with no model param (uses default stable-diffusion)
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=512&height=768&seed={seed}&nologo=true"
    )
    return image_url


def get_style_attributes(prompt: str) -> Dict:
    style = extract_style(prompt)
    colors = extract_colors(prompt)
    return {
        "category": style["category"],
        "colors": colors,
        "fabric": style["fabric"],
        "occasion": style["occasion"]
    }
