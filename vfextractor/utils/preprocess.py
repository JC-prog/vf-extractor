# vfextractor/utils/preprocess.py
import cv2
import numpy as np

def load_image(path):
    return cv2.imread(path, cv2.IMREAD_COLOR)

def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def denoise(image):
    return cv2.fastNlMeansDenoising(image, h=10)
