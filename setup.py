# setup.py
from setuptools import setup, find_packages

setup(
    name="vfextractor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "paddleocr>=2.6",
        "paddlepaddle>=2.5",
        "opencv-python-headless>=4.7",
        # add other dependencies here
    ],
    python_requires='>=3.12',
)
