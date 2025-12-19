import cv2
import logging
from pathlib import Path

from vfextractor.postprocessing.extract import Extractor
from vfextractor.config.templates import read_template
from vfextractor.postprocessing.normalize import normalize_data
from vfextractor.postprocessing.export import save_json, save_csv

logger = logging.getLogger(__name__)

def default_pipeline(image_path, output_path):
    image = cv2.imread(str(image_path))

    extractor = Extractor()
    data = extractor.extract(image)

    save_json(
        data=data,
        output_path=output_path
    )

    return data

def cropped_pipeline(image_path, crop_coordinates, output_dir=None):
    """
    Performs OCR extraction on cropped regions defined in a template, normalizes the data,
    and optionally saves the final JSON/CSV and cropped images into the specified output directory.
    
    Args:
        image_path (str | Path): Path to the input image.
        crop_coordinates (str | Path): Path to the JSON template file.
        output_dir (str | Path, optional): Directory to save all outputs 
            (final JSON, final CSV, and individual cropped images).
    
    Returns:
        dict: The normalized extracted data (a flat dictionary).
    """
    
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))
    
    if image is None:
        logger.error(f"Could not read image from path: {image_path}. Check file existence and format.")
        raise FileNotFoundError(f"Could not read image from path: {image_path}")

    output_dir_path = None
    image_base_name = image_path.stem
    
    if output_dir:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using output directory: {output_dir_path}")

    # Read crop coordinates
    template_data = read_template(crop_coordinates)
    
    # Extraction
    extractor = Extractor()
    raw_extracted_data = {} 
    
    for section_name, section_def in template_data.items():
        logger.info(f"Processing section: {section_name}")
        
        crop_region = section_def["crop_region"]
        # Unpack the coordinates: [x, y, width, height]
        x, y, w, h = crop_region
        
        # Crop the image (OpenCV format: [y:y+h, x:x+w])
        cropped_img = image[y:y+h, x:x+w]

        if output_dir_path:
            crop_filename = f"{image_base_name}_{section_name}.png"
            save_path = output_dir_path / "crops" / crop_filename # Save crops in a subdirectory
            
            # Ensure the crops subdirectory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the image
            cv2.imwrite(str(save_path), cropped_img)
            logger.debug(f"Saved cropped image to: {save_path}")

        # Extract data from the cropped image
        raw_extracted_data[section_name] = extractor.extract(cropped_img)

    if output_dir_path:
        raw_extracted_data_filename = f"{image_base_name}_raw.json"
        save_path = output_dir_path / raw_extracted_data_filename

        save_json(
            data=raw_extracted_data,
            output_path=save_path
        )

        logger.debug(f"Saved Extracted raw data to : {save_path}")

    # Normalize and Flatten Data
    logger.info("Normalizing and flattening extracted data.")
    normalized_data = normalize_data(template=template_data, extracted_data=raw_extracted_data)
    logger.debug(f"Normalized data: {normalized_data}")

    # Save Outputs (Auto-naming files inside output_dir)
    if output_dir_path:
        # Auto-generate file paths based on the input image name
        output_json_path = output_dir_path / f"{image_base_name}_data.json"
        output_csv_path = output_dir_path / f"output_summary.csv" # Or f"{image_base_name}_data.csv"

        # Save Final JSON 
        save_json(
            data=normalized_data,
            output_path=output_json_path
        )
        logger.info(f"Saved final JSON to: {output_json_path}")
        
        # Save Final CSV 
        save_csv(
            data=normalized_data,
            output_path=output_csv_path
        )
        logger.info(f"Appended row to CSV at: {output_csv_path}")

    return normalized_data