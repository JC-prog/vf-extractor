# vfextractor/detectors/report_type_detector.py
def detect_report_type(text_lines):
    text = " ".join(text_lines).lower()
    
    if "humphrey" in text or "hvf" in text:
        return "HVF"
    elif "virtual" in text or "vrvf" in text:
        return "VRVF"
    return "UNKNOWN"
