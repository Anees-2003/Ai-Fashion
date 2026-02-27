from typing import List, Optional, Dict
from database import products_col


async def find_matching_products(
    tags: Optional[List[str]] = None,
    category: Optional[str] = None,
    price_label: Optional[str] = None,
    limit: int = 6,
) -> List[Dict]:
    """
    Query MongoDB products collection by tags, category, and price_label.
    Returns a list of matching products.
    """
    query = {}

    if tags:
        query["tags"] = {"$in": tags}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if price_label:
        query["price_label"] = price_label

    cursor = products_col.find(query, {"_id": 0}).limit(limit)
    results = await cursor.to_list(length=limit)
    return results


async def get_all_products(
    category: Optional[str] = None,
    price_label: Optional[str] = None,
    outfit_type: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    """
    Get products with optional filters. Used by /api/products endpoint.
    """
    query = {}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if price_label:
        query["price_label"] = price_label
    if outfit_type:
        query["outfit_type"] = {"$regex": outfit_type, "$options": "i"}

    cursor = products_col.find(query, {"_id": 0}).limit(limit)
    return await cursor.to_list(length=limit)
