import json
from pathlib import Path


def read_template(template_path: str | Path) -> dict[str, list[list[int]]]:
    """
    Read OCR extraction template from JSON file.

    Args:
        template_path (str | Path): Path to template JSON.

    Returns:
        dict: Mapping of section_name to list of bounding boxes
              in (x, y, width, height) format.
    """
    template_path = Path(template_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with template_path.open("r", encoding="utf-8") as f:
        return json.load(f)
