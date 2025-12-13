from paddleocr import PaddleOCR

_ocr_instance = None

def get_ocr():
    """
    Lazily initialize and return a shared PaddleOCR instance.

    Returns:
        PaddleOCR: Loaded OCR model (singleton).
    """
    global _ocr_instance

    if _ocr_instance is None:
        _ocr_instance = PaddleOCR(
            lang="en",
            use_angle_cls=False,
        )

    return _ocr_instance
