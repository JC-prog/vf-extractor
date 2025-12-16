from vfextractor.ocr.paddle import get_ocr

class Extractor:
    def __init__(self):
        self.ocr = get_ocr()

    def extract(self, image_path):
        ocr_result = self.ocr.predict(image_path)

        rec_texts = []
        for block in ocr_result:
            rec_texts.extend(block.get("rec_texts", []))

        result = ",".join(rec_texts) if rec_texts else ""

        return result
