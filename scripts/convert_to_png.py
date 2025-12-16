import os 
from PIL import Image

from pdf2image import convert_from_path

PDF_NAME = "deidentified.pdf"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(SCRIPT_DIR, "input", PDF_NAME)
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "output")

images = convert_from_path(PDF_PATH)

output_paths = []
for i, img in enumerate(images):
    output_path = os.path.join(
        OUTPUT_PATH,
        f"{os.path.splitext(os.path.basename(PDF_NAME))[0]}_page{i+1}.png"
    )
    img.save(output_path, "PNG")
    output_paths.append(output_path)

print("PDF Converted")
