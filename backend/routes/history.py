from fastapi import APIRouter
from database import designs_col, uploads_col, recommendations_col

router = APIRouter()


@router.get("/history")
async def get_history():
    history = []

    # Designs
    async for doc in designs_col.find({}, {"_id": 1, "prompt": 1, "generated_image_url": 1, "created_at": 1}).sort("created_at", -1).limit(20):
        history.append({
            "type": "design",
            "id": str(doc["_id"]),
            "summary": doc.get("prompt", "Design"),
            "image_url": doc.get("generated_image_url"),
            "created_at": doc.get("created_at", ""),
        })

    # Uploads
    async for doc in uploads_col.find({}, {"_id": 1, "skin_tone": 1, "body_type": 1, "created_at": 1}).sort("created_at", -1).limit(20):
        history.append({
            "type": "upload",
            "id": str(doc["_id"]),
            "summary": f"Photo: {doc.get('skin_tone', '?')} skin, {doc.get('body_type', '?')} body",
            "image_url": None,
            "created_at": doc.get("created_at", ""),
        })

    # Recommendations
    async for doc in recommendations_col.find({}, {"_id": 1, "occasion": 1, "gender": 1, "generated_preview_url": 1, "created_at": 1}).sort("created_at", -1).limit(20):
        history.append({
            "type": "recommendation",
            "id": str(doc["_id"]),
            "summary": f"Outfit for {doc.get('gender', 'neutral')} — {doc.get('occasion', 'casual')} occasion",
            "image_url": doc.get("generated_preview_url"),
            "created_at": doc.get("created_at", ""),
        })

    # Sort all by date desc
    history.sort(key=lambda x: x["created_at"], reverse=True)

    return {"total": len(history), "items": history}
