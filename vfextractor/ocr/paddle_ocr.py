# vfextractor/ocr/paddle_ocr.py
from vfextractor.ocr.base_ocr import BaseOCREngine
from paddleocr import PaddleOCR

class PaddleOCREngine(BaseOCREngine):
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def extract_text(self, image_path: str):
        result = self.ocr.ocr(image_path)
        
        print(result)

        text_data = []
        for line in result:
            try:
                text = line[1][0]  # text string
                text_data.append(text)
            except (IndexError, KeyError):
                # skip invalid lines
                continue
        return text_data
