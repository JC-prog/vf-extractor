import re
from typing import Dict, Any, List

def normalize_header_data(raw_data: str, template_labels: List[str]) -> Dict[str, str]:
    """
    Cleans and normalizes key-value pair data from a raw OCR string (like the 'header').
    
    The raw data is assumed to be a string of key:value pairs separated by commas.
    The function tries to match values to keys based on the template labels.
    
    Args:
        raw_data: The raw OCR string for a section.
        template_labels: The list of expected keys/labels from the template.
        
    Returns:
        A dictionary mapping template labels to their extracted values.
    """
    normalized = {}
    
    temp_data = raw_data.replace(':,', ';').replace(':', ';').replace(',', ';')
    parts = [p.strip() for p in temp_data.split(';') if p.strip()]

    for i in range(len(parts)):
        current_part = parts[i]
        
        if current_part in template_labels:
            key = current_part
            value = None
            
            if i + 1 < len(parts):
                next_part = parts[i+1]
                
                if next_part not in template_labels:
                    value = next_part

                    parts[i+1] = "" 
            
            normalized[key] = value if value is not None else ""
        
    for label in template_labels:
        if label not in normalized:
            normalized[label] = ""
            
    return normalized


def normalize_data(template: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses the template's labels to structure the extracted data into a single, flat dictionary.
    
    Args:
        template: The loaded template JSON dictionary.
        extracted_data: The raw data extracted by the OCR pipeline.
        
    Returns:
        A flat dictionary ready for CSV/JSON serialization.
    """
    final_output = {}
    
    for section_name, section_def in template.items():
        raw_section_data = extracted_data.get(section_name, "")
        template_labels = section_def.get("labels", [])
        
        if not template_labels or not raw_section_data:
            final_output[section_name] = raw_section_data
            continue

        if section_name in ["header", "ght_vfi"]:
            normalized_section = normalize_header_data(raw_section_data, template_labels)
            
            for key, value in normalized_section.items():
                final_output[f"{section_name}_{key}"] = value
        
    return final_output