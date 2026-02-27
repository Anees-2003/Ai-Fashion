from fastapi import APIRouter, HTTPException
from datetime import datetime
from services.recommender import get_recommendations
from services.local_image_gen import generate_fashion_image_b64
import asyncio

router = APIRouter()


@router.get("/recommend")
async def get_recommendation(upload_id: str, occasion: str = "casual", gender: str = "neutral"):
    # Try to fetch the stored upload analysis — fall back to defaults if DB unavailable
    analysis = {
        "skin_tone": "Medium / Warm",
        "body_type": "Athletic / Straight",
        "recommended_colors": [],
        "recommended_styles": [],
    }

    try:
        from database import uploads_col, recommendations_col
        from bson import ObjectId
        upload = await uploads_col.find_one({"_id": ObjectId(upload_id)})
        if upload:
            analysis = {
                "skin_tone": upload.get("skin_tone", "Medium / Warm"),
                "body_type": upload.get("body_type", "Athletic / Straight"),
                "recommended_colors": upload.get("recommended_colors", []),
                "recommended_styles": upload.get("recommended_styles", []),
            }
    except Exception:
        pass  # MongoDB unavailable — use defaults

    # Get recommendations (no network call, pure Python)
    rec = get_recommendations(analysis, occasion, gender)

    # Build preview prompt
    preview_prompt = rec.get(
        "_preview_prompt",
        f"{occasion} {gender} fashion outfit, professional clothing photography"
    )

    # Generate image in-memory as base64 data URI — always works, no file paths
    preview_url = await asyncio.to_thread(
        generate_fashion_image_b64,
        preview_prompt,
        512, 640
    )

    # Overwrite the URL in rec dict
    rec["generated_preview_url"] = preview_url

    # Strip internal _ keys
    rec_to_store = {k: v for k, v in rec.items() if not k.startswith("_")}

    # Store in MongoDB — non-fatal if DB unavailable
    recommendation_id = "local"
    try:
        from database import recommendations_col
        doc = {
            "upload_id": upload_id,
            "occasion": occasion,
            "gender": gender,
            **{k: v for k, v in rec_to_store.items() if k != "generated_preview_url"},
            "generated_preview_url": "[base64-omitted]",  # don't store 100KB in MongoDB
            "created_at": datetime.utcnow().isoformat(),
        }
        res = await recommendations_col.insert_one(doc)
        recommendation_id = str(res.inserted_id)
    except Exception:
        pass  # MongoDB unavailable — response still works fine

    return {
        "recommendation_id": recommendation_id,
        "upload_id": upload_id,
        **rec_to_store,
        "generated_preview_url": preview_url,
        "created_at": datetime.utcnow().isoformat(),
    }
