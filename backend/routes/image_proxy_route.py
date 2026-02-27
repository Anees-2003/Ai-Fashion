"""
image_proxy_route.py
GET /api/image-proxy?prompt=<text>&type=design|preview

Streams the Pollinations.ai image through our server so the browser always
gets a local URL — no CORS issues, no disk I/O, no fallback URLs needed.
"""
import hashlib
import urllib.parse
import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
FASHION_SUFFIX = (
    ", fashion photography, studio lighting, clean background, "
    "professional clothing, ultra high detail, editorial quality"
)

# Mimic a real browser so Pollinations doesn't reject the request
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://pollinations.ai/",
}


def _build_url(prompt: str, width: int, height: int) -> str:
    short = prompt[:250]  # keep URL manageable
    enhanced = short + FASHION_SUFFIX
    encoded = urllib.parse.quote(enhanced)
    seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 99999
    return (
        f"{POLLINATIONS_BASE}/{encoded}"
        f"?width={width}&height={height}&seed={seed}&nologo=true"
    )


@router.get("/image-proxy")
def proxy_image(prompt: str, type: str = "design"):
    """
    Fetches the Pollinations image server-side and streams it to the browser.
    ?type=design  → 512×768
    ?type=preview → 512×640
    """
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is required")

    width, height = (512, 640) if type == "preview" else (512, 768)
    url = _build_url(prompt, width, height)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Pollinations returned {resp.status_code}"
            )

        content = resp.content
        # Detect real image vs error page (error pages are tiny HTML)
        if len(content) < 2000:
            raise HTTPException(status_code=502, detail="Pollinations returned an error page")

        # Auto-detect content type
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            content_type = "image/jpeg"

        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",
                "X-Image-Source": "pollinations",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Image fetch failed: {str(e)}")
