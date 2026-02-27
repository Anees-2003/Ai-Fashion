import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from datetime import datetime
from services.photo_analyzer import analyze_photo

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10 MB.")

    # Save file to disk (sync write — acceptable for image uploads)
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
    except OSError:
        raise HTTPException(status_code=500, detail="Could not save uploaded file.")

    # Analyze photo (pure Python — no external API needed)
    try:
        analysis = analyze_photo(image_bytes)
    except Exception as e:
        analysis = {
            "skin_tone": "Medium / Warm",
            "skin_tone_hex": "#C68642",
            "body_type": "Athletic / Straight",
            "recommended_colors": ["navy", "white", "beige", "olive"],
            "recommended_styles": ["casual", "formal", "festive"],
            "analysis_result": "Default analysis — photo analysis service unavailable.",
        }

    # Store in MongoDB — non-fatal if DB unavailable
    upload_id = str(uuid.uuid4())  # default local ID
    try:
        from database import uploads_col
        doc = {
            "image_path": file_path,
            "filename": filename,
            **analysis,
            "created_at": datetime.utcnow().isoformat(),
        }
        result = await uploads_col.insert_one(doc)
        upload_id = str(result.inserted_id)
    except Exception:
        pass  # MongoDB not available — upload_id stays as a UUID string

    return {
        "upload_id": upload_id,
        "filename": filename,
        **analysis,
        "created_at": datetime.utcnow().isoformat(),
    }
