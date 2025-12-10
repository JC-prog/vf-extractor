# dev_test.py
from vfextractor.pipeline import extract_report
from vfextractor.utils.preprocess import load_image, to_grayscale, denoise
import cv2

# Path to your sample image
image_path = r"C:\Users\PC\Projects\TTSH\vf-extractor\examples\HVF - OD.png"


# Optional: preprocess the image
image = load_image(image_path)

# If you want to visualize
cv2.imshow("Preprocessed Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Extract report using the pipeline
report = extract_report(image_path)

# Print structured output
print("Report Type:", report.report_type)
print("Patient Info:", report.patient_info)
print("Matrix:", report.matrix)
