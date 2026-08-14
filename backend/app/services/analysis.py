from PIL import Image

from backend.app.services.extraction import extract_label_fields
from backend.app.services.ocr import extract_text
from backend.app.services.validation import validate_label


def analyze_image(image: Image.Image):
    """
    Run the complete alcohol label analysis pipeline.

    Image
      -> OCR
      -> AI extraction
      -> Validation
    """

    # 1. OCR
    ocr_text = extract_text(image)

    if not ocr_text:
        raise ValueError(
            "No text could be detected in the image."
        )

    # 2. AI extraction
    label = extract_label_fields(ocr_text)

    # 3. Validation
    validation = validate_label(label)

    return {
        "ocr_text": ocr_text,
        "label": label,
        "validation": validation,
    }