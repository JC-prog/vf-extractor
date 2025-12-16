import json
import csv
from pathlib import Path
from typing import Dict

def save_json(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Saved at " + str(output_path))

def save_csv(data: Dict[str, str], output_path: str | Path):
    """Saves a flat dictionary (one row of data) to a CSV file."""
    output_path = Path(output_path)
    
    # Check if the file exists to determine if we need to write headers
    file_exists = output_path.exists()
    
    with output_path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        
        # Write header only if the file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)