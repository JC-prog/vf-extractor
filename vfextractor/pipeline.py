# vfextractor/pipeline.py
from vfextractor.detectors.report_type_detector import detect_report_type
from vfextractor.parsers.hvf_parser import HVFParser
from vfextractor.parsers.vrvf_parser import VRVFParser
from vfextractor.ocr.paddle_ocr import PaddleOCREngine

def extract_report(image_path: str):
    ocr_engine = PaddleOCREngine()
    text_data = ocr_engine.extract_text(image_path)

    report_type = "HVF"
    print(text_data)
    
    if report_type == "HVF":
        parser = HVFParser()
    elif report_type == "VRVF":
        parser = VRVFParser()
    else:
        raise ValueError("Unknown visual field report type")

    return parser.parse(text_data)
