"""
Run this script ONCE on an internet-connected machine to pre-download PaddleOCR models.

Models will be saved directly into the project models/ directory, which is then
bundled with the portable distribution for offline use.

Usage:
    python scripts/download_models.py
"""

import os
import shutil
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
PADDLEX_CACHE = MODELS_DIR / "paddlex"

# Redirect paddlex model cache into models/paddlex/ before importing PaddleOCR.
# PADDLE_PDX_CACHE_HOME is read at paddlex import time, so must be set first.
os.environ["PADDLE_PDX_CACHE_HOME"] = str(PADDLEX_CACHE)
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

MODELS_DIR.mkdir(exist_ok=True)
PADDLEX_CACHE.mkdir(exist_ok=True)

print(f"Downloading PaddleOCR models into: {PADDLEX_CACHE}")
print("This may take several minutes...")

from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="en", use_textline_orientation=False)

# Run a quick prediction to ensure all model weights are fully loaded and cached
print("Verifying models with a test prediction...")
test_img = np.zeros((100, 300, 3), dtype=np.uint8)
ocr.predict(test_img)

# Fallback: if models were previously cached in the default ~/.paddlex location,
# copy them in so this script works even if run before the env var redirect.
default_cache = Path.home() / ".paddlex"
if default_cache.exists() and default_cache != PADDLEX_CACHE:
    print(f"Copying any cached models from {default_cache} ...")
    shutil.copytree(default_cache, PADDLEX_CACHE, dirs_exist_ok=True)

print(f"Done. Models saved to: {MODELS_DIR}")
print("Include the models/ directory when building the portable distribution.")
