from fastapi import APIRouter, HTTPException
from datetime import datetime
from models import DesignRequest
from services.local_image_gen import generate_fashion_image_b64
from services.image_generator import get_style_attributes
from services.product_matcher import find_matching_products
import asyncio

router = APIRouter()


@router.post("/generate")
async def generate_design(request: DesignRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # Generate image in-memory and return as base64 data URI
    image_url = await asyncio.to_thread(
        generate_fashion_image_b64,
        request.prompt,
        512, 768
    )

    # Extract style attributes from prompt keywords
    try:
        style_tags = get_style_attributes(request.prompt)
    except Exception:
        style_tags = []

    # Store in MongoDB — non-fatal if DB unavailable
    doc_id = "local"
    try:
        from database import designs_col, users_col
        from bson import ObjectId
        doc = {
            "prompt": request.prompt,
            "generated_image_url": "[base64-omitted]",  # don't store 100KB in MongoDB
            "style_tags": style_tags,
            "user_id": request.user_id or "anonymous",
            "created_at": datetime.utcnow().isoformat(),
        }
        result = await designs_col.insert_one(doc)
        doc_id = str(result.inserted_id)
    except Exception:
        pass  # MongoDB unavailable — image still returns fine

    # Find matching products based on style tags and prompt keywords
    try:
        # Extract keywords from prompt for better tag matching
        prompt_keywords = [w.strip().lower() for w in request.prompt.replace(',', ' ').split() if len(w) > 2]
        
        suggested_products = await find_matching_products(
            tags=prompt_keywords,
            category=style_tags.get("category"),
            limit=4
        )
    except Exception:
        suggested_products = []

    return {
        "id": doc_id,
        "prompt": request.prompt,
        "generated_image_url": image_url,
        "style_tags": style_tags,
        "suggested_products": suggested_products,
        "created_at": datetime.utcnow().isoformat(),
    }
