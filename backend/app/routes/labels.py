from io import BytesIO

from fastapi import APIRouter, File, UploadFile
from PIL import Image

from backend.app.services.ocr import extract_text
from backend.app.services.extraction import extract_label_fields
from backend.app.services.validation import validate_label


router = APIRouter()


# =========================================================
# Constants
# =========================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


# =========================================================
# Helper functions
# =========================================================

def is_supported_image(file: UploadFile) -> bool:
    return file.content_type in ALLOWED_IMAGE_TYPES


async def read_image(file: UploadFile) -> Image.Image:
    contents = await file.read()

    return Image.open(
        BytesIO(contents)
    ).convert("RGB")


# =========================================================
# OCR
# =========================================================

@router.post("/ocr")
async def ocr_label(file: UploadFile = File(...)):
    """
    Run OCR on an uploaded alcohol label image.
    """

    if not is_supported_image(file):
        return {
            "success": False,
            "error": (
                "Unsupported image type. "
                "Please upload JPG, PNG, or WEBP."
            ),
        }

    try:
        image = await read_image(file)

        text = extract_text(image)

        return {
            "success": True,
            "filename": file.filename,
            "text": text,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unable to process image: {str(e)}",
        }


# =========================================================
# Extraction
# =========================================================

@router.post("/extract")
async def extract_label(file: UploadFile = File(...)):
    """
    Run OCR and AI extraction on an uploaded label.
    """

    if not is_supported_image(file):
        return {
            "success": False,
            "error": (
                "Unsupported image type. "
                "Please upload JPG, PNG, or WEBP."
            ),
        }

    try:
        # 1. Image
        image = await read_image(file)

        # 2. OCR
        ocr_text = extract_text(image)

        if not ocr_text:
            return {
                "success": False,
                "error": "No text could be detected in the image.",
            }

        # 3. AI extraction
        label = extract_label_fields(ocr_text)

        return {
            "success": True,
            "filename": file.filename,
            "ocr_text": ocr_text,
            "label": label.model_dump(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unable to analyze label: {str(e)}",
        }


# =========================================================
# Complete Analysis
# =========================================================

@router.post("/analyze")
async def analyze_label(file: UploadFile = File(...)):
    """
    Complete label analysis pipeline:

        Image
          ↓
        OCR
          ↓
        AI extraction
          ↓
        Validation
          ↓
        Result
    """

    if not is_supported_image(file):
        return {
            "success": False,
            "error": (
                "Unsupported image type. "
                "Please upload JPG, PNG, or WEBP."
            ),
        }

    try:
        # -------------------------------------------------
        # 1. Read image
        # -------------------------------------------------

        image = await read_image(file)

        # -------------------------------------------------
        # 2. OCR
        # -------------------------------------------------

        ocr_text = extract_text(image)

        if not ocr_text:
            return {
                "success": False,
                "error": "No text could be detected in the image.",
            }

        # -------------------------------------------------
        # 3. AI extraction
        # -------------------------------------------------

        label = extract_label_fields(ocr_text)

        # -------------------------------------------------
        # 4. Validation
        # -------------------------------------------------

        validation = validate_label(label)

        # -------------------------------------------------
        # 5. Return result
        # -------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "ocr_text": ocr_text,
            "label": label.model_dump(),
            "validation": validation.model_dump(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unable to analyze label: {str(e)}",
        }