import json
from pathlib import Path
from typing import Any, Dict 

def read_template(template_path: str | Path) -> dict[str, Any]:
    """
    Read OCR extraction template from JSON file.

    Args:
        template_path (str | Path): Path to template JSON.

    Returns:
        dict: The loaded JSON content. The structure is 
              dict[section_name, dict[key, value]], where the inner 
              dict contains keys like 'crop_region' and 'labels'.
    """
    template_path = Path(template_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with template_path.open("r", encoding="utf-8") as f:
        return json.load(f)