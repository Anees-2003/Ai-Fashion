import urllib.parse
from typing import Dict, List, Optional


OCCASION_MAP = {
    "casual": {
        "outfit_types": ["casual dress", "jeans and top", "casual kurta", "hoodie", "casual co-ord"],
        "colors": ["earthy tones", "pastels", "denim blue", "white", "olive"],
        "preview_prompt": "casual street fashion outfit, comfortable, trendy, simple, modern style",
    },
    "formal": {
        "outfit_types": ["business suit", "formal blazer", "formal dress", "office wear", "formal trousers"],
        "colors": ["navy", "charcoal grey", "black", "white", "beige"],
        "preview_prompt": "formal business fashion outfit, professional, elegant, office wear, studio photo",
    },
    "wedding": {
        "outfit_types": ["lehenga", "saree", "sherwani", "wedding gown", "anarkali"],
        "colors": ["gold", "red", "ivory", "rose gold", "deep maroon"],
        "preview_prompt": "Indian wedding fashion outfit, bridal wear, traditional elegant, rich embroidery, studio photo",
    },
    "party": {
        "outfit_types": ["party dress", "cocktail dress", "party jumpsuit", "embellished top", "party co-ord"],
        "colors": ["metallic gold", "black", "electric blue", "hot pink", "emerald"],
        "preview_prompt": "glamorous party fashion outfit, evening wear, sparkly, fashionable, studio lighting",
    },
    "festive": {
        "outfit_types": ["ethnic dress", "festive kurta", "silk saree", "festive lehenga", "indo-western"],
        "colors": ["orange", "yellow", "maroon", "bright pink", "peacock blue"],
        "preview_prompt": "festive Indian ethnic fashion outfit, colorful, elegant, traditional modern, studio photo",
    },
    "sport": {
        "outfit_types": ["activewear set", "yoga wear", "gym outfit", "sports tee and track", "athleisure"],
        "colors": ["black", "grey", "neon yellow", "white", "cobalt blue"],
        "preview_prompt": "sportswear activewear fashion outfit, athletic, modern gym wear, studio photo",
    },
}

GENDER_FILTER = {
    "female": ["dress", "lehenga", "saree", "skirt", "anarkali", "gown", "blouse", "kurta"],
    "male": ["suit", "sherwani", "kurta pyjama", "blazer", "tuxedo", "formal trousers", "dhoti"],
    "neutral": [],
}

SKIN_TONE_COLORS = {
    "Fair / Light": ["dusty rose", "lavender", "navy", "forest green", "burgundy"],
    "Light / Medium": ["cobalt blue", "emerald", "terracotta", "warm beige", "deep purple"],
    "Medium / Warm": ["coral", "mustard", "rust orange", "olive green", "warm brown"],
    "Medium / Dark": ["electric blue", "bright white", "gold", "vibrant orange", "lime green"],
    "Dark / Deep": ["hot pink", "cobalt blue", "lime yellow", "bright white", "royal purple"],
}

CASUAL_REC = {
    "Petite": "Try high-waist jeans with a fitted crop top and white sneakers.",
    "Tall / Slim": "Wide-leg linen trousers with a tucked-in striped tee for a chic casual look.",
    "Athletic / Straight": "A wrap dress with a denim jacket creates a feminine casual silhouette.",
    "Hourglass": "A fitted knit top with straight-leg jeans flatters your natural curves.",
    "Pear / Triangle": "A bold printed blouse with dark slim-fit trousers balances proportions beautifully.",
    "Apple / Round": "A flowy empire-waist top in a solid hue over wide-leg pants gives a relaxed stylish look.",
}

FORMAL_REC = {
    "Petite": "A tailored single-button blazer with cigarette pants and block heels elevates your frame.",
    "Tall / Slim": "A pinstripe wide-leg suit or a midi shift dress in navy gives power-executive energy.",
    "Athletic / Straight": "A belted wrap blazer-dress defines the waist elegantly for formal settings.",
    "Hourglass": "A fitted pencil skirt with a tucked-in silk blouse and structured blazer is timeless.",
    "Pear / Triangle": "A statement tailored jacket with flared trousers draws attention upward beautifully.",
    "Apple / Round": "V-neck formal blouse with straight-cut formal trousers in a monochrome palette looks polished.",
}

FESTIVE_REC = {
    "Petite": "A short anarkali or lehenga with platform heels creates a princess-like festive presence.",
    "Tall / Slim": "A floor-length embroidered anarkali or a silk saree drape suits your graceful height.",
    "Athletic / Straight": "A layered lehenga with a fitted choli and dupatta adds curves effortlessly.",
    "Hourglass": "A silk saree or embroidered lehenga with a fitted blouse enhances your natural silhouette.",
    "Pear / Triangle": "An A-line lehenga with a heavily embellished choli balances your figure beautifully.",
    "Apple / Round": "A floor-length abaya-style anarkali with vertical embroidery patterns is stunning and slimming.",
}


def get_recommendations(
    analysis: Dict,
    occasion: str,
    gender: str,
) -> Dict:
    """
    Combine photo analysis + occasion + gender into outfit recommendations.
    """
    occasion_lower = occasion.lower()
    occ_data = OCCASION_MAP.get(occasion_lower, OCCASION_MAP["casual"])
    body_type = analysis.get("body_type", "Athletic / Straight")
    skin_tone = analysis.get("skin_tone", "Medium / Warm")

    # Merge skin-tone colors with occasion colors
    tone_colors = SKIN_TONE_COLORS.get(skin_tone, ["white", "navy", "beige"])
    combined_colors = list(dict.fromkeys(tone_colors + occ_data["colors"]))[:8]

    # Filter outfit suggestions by gender
    gender_filter = GENDER_FILTER.get(gender.lower(), [])
    outfits = occ_data["outfit_types"]
    if gender_filter:
        filtered = [o for o in outfits if any(g in o.lower() for g in gender_filter)]
        outfits = filtered if filtered else outfits

    # Build suggested outfit objects
    suggested = []
    for i, outfit in enumerate(outfits[:4]):
        suggested.append({
            "rank": i + 1,
            "outfit": outfit,
            "color": combined_colors[i] if i < len(combined_colors) else "neutral",
            "reason": f"Suits a {body_type} body type with a {skin_tone} skin tone for {occasion} occasions.",
        })

    # Generate preview image prompt
    preview_prompt = (
        f"{occ_data['preview_prompt']}, color palette: {combined_colors[0]} and {combined_colors[1]}, "
        f"suitable for {body_type} body type, high fashion photography"
    )
    encoded = urllib.parse.quote(preview_prompt)
    preview_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=768&seed=99&nologo=true"

    return {
        "skin_tone": skin_tone,
        "body_type": body_type,
        "occasion": occasion,
        "gender": gender,
        "suggested_outfits": suggested,
        "color_palette": combined_colors[:6],
        "casual_recommendation": CASUAL_REC.get(body_type, "Try comfortable, well-fitted casual clothing."),
        "formal_recommendation": FORMAL_REC.get(body_type, "A tailored suit or structured dress works well."),
        "festive_recommendation": FESTIVE_REC.get(body_type, "Traditional ethnic wear with rich embroidery is perfect."),
        "generated_preview_url": preview_url,  # will be overwritten by route with locally-served URL
        "_preview_prompt": preview_prompt,
    }
