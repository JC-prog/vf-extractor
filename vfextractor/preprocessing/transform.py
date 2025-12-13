import cv2

class Preprocessor:
    """
    Handles image preprocessing for the OCR pipeline.
    
    Attributes:
        target_size (tuple): Desired output size for the images (width, height).
    """

    def __init__(self, target_size=(640, 640)):
        """
        Initialize the Preprocessor with optional target size.
        
        Args:
            target_size (tuple, optional): Resize images to this size. Default is (640, 640).
        """
        self.target_size = target_size

    def resize(self, image):
        """
        Resize an image to the target size.
        
        Args:
            image (numpy.ndarray): Input image in OpenCV format.
            
        Returns:
            numpy.ndarray: Resized image.
        """
        return cv2.resize(image, self.target_size)

    def normalize(self, image):
        """
        Normalize image pixel values to [0,1] range.
        
        Args:
            image (numpy.ndarray): Input image.
            
        Returns:
            numpy.ndarray: Normalized image.
        """
        return image / 255.0
