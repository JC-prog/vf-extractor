# vfextractor/ocr/base_ocr.py
from abc import ABC, abstractmethod

class BaseOCREngine(ABC):
    @abstractmethod
    def extract_text(self, image_path: str):
        pass
