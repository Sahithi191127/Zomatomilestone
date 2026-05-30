"""Local image assets from project /images folder."""

from __future__ import annotations

import base64
import io
import urllib.request
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGES_DIR = PROJECT_ROOT / "images"

LOGO_PATH = IMAGES_DIR / "tastepilot-logo.png"
LOGO_PATH_DARK = IMAGES_DIR / "tastepilot-logo-dark.png"
EMPTY_ILLUSTRATION_PATH = IMAGES_DIR / "empty-illustration.svg"
LOADING_RING_PATH = IMAGES_DIR / "loading-ring.svg"

# Fallback URL from images/code.html when local file missing
LOGO_URL_FALLBACK = (
    "https://lh3.googleusercontent.com/aida/ADBb0uhhKIocJR4Z8K0c3zGUfSTtAbc5JmwiuM8wzjoe8krVI1uX6rsE4WnxpayP"
    "-dbEzLqXEzonzdc5VnUFk0-RllykmO-YsC0giI0xFPc1kP5T0EibF1wtB2_sZGoDwQo3YoP5NZmqUU3of07xI4zpP0_vE7_"
    "NyF2m0xrdLmlEC_5M7I-SV7BZCJDInBu_USsHmYYyScnifnkVFyzh62tPibJVNXvjyzmHHbAX9tPmA_NUR9fbKZfkJzva3A"
)

# Warm off-white wordmark on dark surfaces (matches --tp-text)
_LOGO_TEXT_RGB = (240, 232, 229)


def _is_logo_red_pixel(r: int, g: int, b: int) -> bool:
    return r > 140 and r > g + 25 and r > b + 25


def _process_logo_for_dark_theme(png_bytes: bytes) -> bytes:
    """Remove white box; lighten wordmark for dark UI; keep coral icon."""
    from PIL import Image

    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            if r >= 238 and g >= 238 and b >= 238:
                pixels[x, y] = (r, g, b, 0)
                continue

            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            chroma = max(r, g, b) - min(r, g, b)

            if _is_logo_red_pixel(r, g, b):
                pixels[x, y] = (
                    min(255, int(r * 1.08)),
                    min(255, int(g * 1.02)),
                    min(255, int(b * 1.02)),
                    a,
                )
            elif luminance < 110 and chroma < 50:
                pixels[x, y] = (*_LOGO_TEXT_RGB, a)
            elif r >= 210 and g >= 210 and b >= 210:
                avg = (r + g + b) / 3
                alpha = int(max(0, min(255, (248 - avg) * 4)))
                pixels[x, y] = (r, g, b, min(a, alpha))

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def _load_logo_source_bytes() -> bytes:
    if LOGO_PATH_DARK.is_file():
        return LOGO_PATH_DARK.read_bytes()
    if LOGO_PATH.is_file():
        return _process_logo_for_dark_theme(LOGO_PATH.read_bytes())
    with urllib.request.urlopen(LOGO_URL_FALLBACK, timeout=15) as response:
        return _process_logo_for_dark_theme(response.read())


@lru_cache(maxsize=1)
def logo_src() -> str:
    """Return data URI for dark-theme logo (transparent, warm wordmark)."""
    encoded = base64.b64encode(_load_logo_source_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def logo_exists_locally() -> bool:
    return LOGO_PATH_DARK.is_file() or LOGO_PATH.is_file()
