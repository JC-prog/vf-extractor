import fitz  # pymupdf
import os
from PIL import Image


def convert_from_path(pdf_path, dpi=300):
    """
    Convert a PDF file to a list of PIL Images.
    Drop-in replacement for pdf2image.convert_from_path — no poppler required.

    Args:
        pdf_path (str | Path): Path to the PDF file.
        dpi (int): Resolution for the output images. Default is 300.

    Returns:
        List[PIL.Image.Image]: One PIL Image per PDF page.
    """
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    doc = fitz.open(str(pdf_path))
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


class PDFConverter:
    """
    Converts PDF files into PNG images for OCR processing.

    Attributes:
        dpi (int): Resolution for the output images.
        output_folder (str): Directory where converted images will be saved.
    """

    def __init__(self, dpi=300, output_folder="data/processed/pdf_images"):
        self.dpi = dpi
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def convert(self, pdf_path):
        """
        Convert a PDF into PNG images saved to disk.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            List[str]: Paths of generated PNG images.
        """
        images = convert_from_path(pdf_path, dpi=self.dpi)
        output_paths = []

        for i, img in enumerate(images):
            output_path = os.path.join(
                self.output_folder,
                f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page{i+1}.png"
            )
            img.save(output_path, "PNG")
            output_paths.append(output_path)

        return output_paths
