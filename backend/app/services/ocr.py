import pytesseract
import os
from PIL import Image


# Explicitly configure Tesseract on Windows
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


def extract_text(image: Image.Image) -> str:
    """
    Extract text from an image using Tesseract OCR.
    """

    text = pytesseract.image_to_string(image)

    return text.strip()