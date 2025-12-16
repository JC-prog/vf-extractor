# dev_test.py
import cv2
from pathlib import Path

from vfextractor.postprocessing.extract import Extractor
from vfextractor.config.templates import read_template
from vfextractor.postprocessing.export import save_json

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Path to your sample image
image_path = BASE_DIR / "examples" / "vrvf_od.jpg"
json_path = BASE_DIR / "data" / "vrvf_template.json"
output_path = BASE_DIR / "data" / "result.json"

def preview_crop(image, crop, section_name):
    cv2.imshow(f"Crop: {section_name}", crop)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

json_data = read_template(json_path)
print(json_data)

# Load Image
image = cv2.imread(str(image_path))

extractor = Extractor()

data = {}
for section_name, boxes in json_data.items():
    print("Section: " + section_name)

    labels = ["x", "y", "width", "height"]

    for i in range(len(boxes)): 
        print(labels[i] + ": " + str(boxes[i]))

    x = boxes[0]
    y = boxes[1]
    w = boxes[2]
    h = boxes[3]

    cropped_img = image[y:y+h, x:x+w]
    # preview_crop(image, cropped_img, section_name)

    data[section_name] = extractor.extract(cropped_img)

print(data)

save_json(
    data=data,
    output_path=output_path
)

# data = extractor.extract(image_path)

# print(data)