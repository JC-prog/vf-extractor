from pdf2image import convert_from_path
import os

class PDFConverter:
    """
    Converts PDF files into PNG images for OCR processing.
    
    Attributes:
        dpi (int): Resolution for the output images.
        output_folder (str): Directory where converted images will be saved.
    """

    def __init__(self, dpi=300, output_folder="data/processed/pdf_images"):
        """
        Initialize the PDFConverter.
        
        Args:
            dpi (int, optional): Resolution for output images. Default is 300.
            output_folder (str, optional): Directory to save PNG images. Default is 'data/processed/pdf_images'.
        """
        self.dpi = dpi
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def convert(self, pdf_path):
        """
        Convert a PDF into PNG images.
        
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
