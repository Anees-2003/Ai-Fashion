"""
image_proxy.py  — Fetch AI images from Pollinations and serve them locally.
Uses requests (sync, already in requirements) via asyncio.to_thread.
Falls back to the direct Pollinations URL if download fails/times out.
"""
import os
import uuid
import hashlib
import asyncio
import requests
import urllib.parse


POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"

FASHION_SUFFIX = (
    ", fashion photography, studio lighting, clean background, "
    "professional clothing, ultra high detail, editorial quality, 8k"
)

# Browser-like headers so Pollinations doesn't reject the request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://pollinations.ai/",
}


def build_image_url(prompt: str, width: int = 512, height: int = 768) -> str:
    """Build a deterministic Pollinations URL (same prompt → same seed → Pollinations caches it)."""
    # Limit prompt length to avoid URL being too long
    short_prompt = prompt[:300] if len(prompt) > 300 else prompt
    enhanced = short_prompt + FASHION_SUFFIX
    encoded = urllib.parse.quote(enhanced)
    # Deterministic seed: hash of the prompt → consistent URL for same prompt
    seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 99999
    return (
        f"{POLLINATIONS_BASE}/{encoded}"
        f"?width={width}&height={height}&seed={seed}&nologo=true&enhance=true"
    )


def _sync_download(url: str, filepath: str) -> bool:
    """Synchronous download using requests. Returns True on success."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True, stream=True)
        if resp.status_code == 200:
            content = resp.content
            # Ignore tiny/error responses (real images are >5KB)
            if len(content) > 5000:
                with open(filepath, "wb") as f:
                    f.write(content)
                return True
    except Exception:
        pass
    return False


async def _download_image(url: str, filepath: str) -> bool:
    """Async wrapper around the sync download — runs in a thread pool."""
    return await asyncio.to_thread(_sync_download, url, filepath)


async def fetch_and_save_image(prompt: str, save_dir: str = "uploads/designs") -> str:
    """
    Fetch AI design image from Pollinations, save locally, return /uploads/designs/xxx.jpg.
    Falls back to direct Pollinations URL if download fails.
    """
    os.makedirs(save_dir, exist_ok=True)
    poll_url = build_image_url(prompt, width=512, height=768)
    filename = f"design_{uuid.uuid4().hex[:16]}.jpg"
    filepath = os.path.join(save_dir, filename)
    local_url = f"/uploads/designs/{filename}"

    if await _download_image(poll_url, filepath):
        return local_url

    # Fallback: return Pollinations URL directly
    return poll_url


async def fetch_and_save_preview(prompt: str, save_dir: str = "uploads/previews") -> str:
    """
    Fetch outfit preview image from Pollinations, save locally, return /uploads/previews/xxx.jpg.
    Falls back to direct Pollinations URL if download fails.
    """
    os.makedirs(save_dir, exist_ok=True)
    poll_url = build_image_url(prompt, width=512, height=640)
    filename = f"preview_{uuid.uuid4().hex[:16]}.jpg"
    filepath = os.path.join(save_dir, filename)
    local_url = f"/uploads/previews/{filename}"

    if await _download_image(poll_url, filepath):
        return local_url

    # Fallback: return Pollinations URL directly
    return poll_url
