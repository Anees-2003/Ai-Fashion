from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DesignRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = "anonymous"


class StyleTags(BaseModel):
    category: str
    colors: List[str]
    fabric: str
    occasion: str


class DesignResponse(BaseModel):
    id: str
    prompt: str
    generated_image_url: str
    style_tags: StyleTags
    created_at: str


class UploadAnalysis(BaseModel):
    skin_tone: str
    skin_tone_hex: str
    body_type: str
    recommended_colors: List[str]
    recommended_styles: List[str]
    analysis_result: str


class ProductOut(BaseModel):
    id: Optional[str] = None
    name: str
    outfit_type: str
    category: str
    price_range: str
    price_label: str  # Budget / Mid-range / Premium
    purchase_link: str
    tags: List[str]
    image_url: str


class RecommendationResponse(BaseModel):
    upload_id: str
    skin_tone: str
    body_type: str
    occasion: str
    gender: str
    suggested_outfits: List[dict]
    color_palette: List[str]
    casual_recommendation: str
    formal_recommendation: str
    festive_recommendation: str
    generated_preview_url: str
    created_at: str


class HistoryItem(BaseModel):
    type: str  # "design" | "upload" | "recommendation"
    id: str
    summary: str
    image_url: Optional[str] = None
    created_at: str
