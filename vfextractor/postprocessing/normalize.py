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

def normalize_map_data(raw_data: str, template_labels: List[str]) -> Dict[str, str]:
    """
    Cleans and normalizes map-like data from a raw OCR string, designed for structured data like visual field maps.

    The function assumes the raw data contains values intended to be mapped sequentially
    to the `template_labels`. It performs robust cleaning steps to handle common OCR errors:

    1.  **Delimitation:** Splits the string by commas (`,`).
    2.  **Internal Spacing:** If an extracted part contains internal whitespace (e.g., ' -1 -2 '), it is split further to separate merged values.
    3.  **Numeric Filtering:** It strictly filters for values that represent **signed integers** (positive or negative, including optional trailing dots for OCR noise, e.g., '31.' or '-5'). All non-numeric characters (like symbols or text) are discarded.
    4.  **Mapping:** The filtered numeric values are mapped sequentially to the `template_labels` in the order they appear.
    5.  **Handling Gaps:** If there are fewer numeric values than `template_labels`, the remaining labels are filled with an empty string ('').

    Args:
        raw_data: The raw OCR string for a section (e.g., "29,28,...,30" or "-5, -1 0, \u0394, -3").
        template_labels: The list of expected keys/labels (e.g., STATIC_MAP_LABELS) to structure the output.

    Returns:
        A dictionary mapping every template label to either its extracted and cleaned numeric value (as a string) 
        or an empty string if no corresponding value was found in the data stream.
    """

    initial_parts = [p.strip() for p in raw_data.split(',')]
    
    parts = []
    for part in initial_parts:
        if ' ' in part and re.search(r'[^\s]', part):
            parts.extend([p.strip() for p in part.split(' ') if p.strip()])
        elif part:
            parts.append(part)
    
    SIGNED_INTEGER_PATTERN = re.compile(r'^\s*([+-]?\d+)\.?\s*$')
    
    numeric_values = []

    for part in parts:
        match = SIGNED_INTEGER_PATTERN.match(part)
        
        if match:
            cleaned_value = match.group(1)
            numeric_values.append(cleaned_value)
            
    normalized: Dict[str, str] = {}
    
    num_labels = len(template_labels)
    num_values = len(numeric_values)

    map_count = min(num_labels, num_values)
    
    for i in range(map_count):
        label = template_labels[i]
        value = numeric_values[i]
        normalized[label] = value
        
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

        if section_name in ["header", "test_details", "ght_vfi", "vfi"]:
            normalized_section = normalize_header_data(raw_section_data, template_labels)
            
            for key, value in normalized_section.items():
                final_output[f"{section_name}_{key}"] = value

        if section_name in ["threshold_map", "total_deviation", "pattern_deviation"]:
            normalized_section = normalize_map_data(raw_section_data, template_labels)
            
            for key, value in normalized_section.items():
                final_output[f"{section_name}_{key}"] = value
        
    return final_output