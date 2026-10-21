"""Visual tokens shared with the site (site/src/styles/tokens.css) and the Inter font."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import requests
from matplotlib import font_manager

from pnsm.load import DEFAULT_CACHE_DIR

BG = "#FFFFFF"
SURFACE = "#F7F7F8"  # pitch
LINE = "#D4D4D8"  # pitch lines, strong borders
BORDER = "#E4E4E7"
ROW = "#F0F0F2"
TEXT = "#0A0A0B"
TEXT_2 = "#3F3F46"
TEXT_MUTED = "#6B6B73"
TEXT_FAINT = "#A1A1AA"

# the post is drawn at 100 dpi, so 1 px = 0.72 pt
DPI = 100
PT = 72 / DPI

INTER_URL = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
INTER_FILES = ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold"]
FONT_DIR = DEFAULT_CACHE_DIR / "fonts"


def ensure_inter(font_dir: Path = FONT_DIR) -> str:
    """Register Inter (static TTFs, SIL OFL) with matplotlib, downloading it once into the cache.

    Returns the family name to use; falls back to DejaVu Sans when the download fails.
    """
    paths = [font_dir / f"Inter-{w}.ttf" for w in INTER_FILES]
    if not all(p.exists() for p in paths):
        try:
            response = requests.get(INTER_URL, timeout=120)
            response.raise_for_status()
            font_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                for p in paths:
                    p.write_bytes(archive.read(f"extras/ttf/{p.name}"))
        except (requests.RequestException, KeyError, zipfile.BadZipFile):
            return "DejaVu Sans"
    for p in paths:
        font_manager.fontManager.addfont(str(p))
    return "Inter"
