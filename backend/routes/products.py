from fastapi import APIRouter, Query
from typing import Optional
from services.product_matcher import get_all_products

router = APIRouter()


@router.get("/products")
async def list_products(
    category: Optional[str] = Query(None),
    price_label: Optional[str] = Query(None, description="Budget | Mid-range | Premium"),
    outfit_type: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
):
    products = await get_all_products(
        category=category,
        price_label=price_label,
        outfit_type=outfit_type,
        limit=limit,
    )
    return {"total": len(products), "products": products}
