# TTB Alcohol Label Verifier

AI-powered alcohol beverage label screening system that uses OCR, structured AI extraction, and rule-based validation to identify potential U.S. alcohol label compliance issues.

> **Prototype disclaimer:** This project is a compliance screening prototype and is not a substitute for formal TTB label approval or legal advice.

---

## Overview

The TTB Alcohol Label Verifier analyzes alcohol beverage label images and extracts key information such as:

- Beverage type
- Brand name
- Class/type designation
- Alcohol content
- Proof
- Net contents
- Producer/bottler information
- Importer information
- Country of origin
- Government health warning

The extracted information is then evaluated against a simplified set of compliance rules.

The system produces a structured result indicating whether the label:

- **PASS** — required screening checks passed
- **REVIEW** — additional review is recommended
- **FAIL** — one or more compliance requirements were not satisfied

---

## Architecture

```text
                    ┌──────────────────┐
                    │   Label Image    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │       OCR        │
                    │    Tesseract     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  AI Extraction   │
                    │    OpenAI API     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Structured Data  │
                    │    Pydantic      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Validation     │
                    │  Rule Engine     │
                    └────────┬─────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │       Compliance Result    │
              │                             │
              │   PASS / REVIEW / FAIL     │
              └─────────────────────────────┘
```
---
## Tech Stack
# Backend
- Python
- FastAPI
- Pydantic
- OpenAI API
- Tesseract OCR
- Pillow
- pytest

# Frontend
- React
- Vite
- JavaScript
- CSS

## Project Structure
```text
ttb-label-verifier/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── test_labels/
│   ├── test_beer.png
│   ├── test_complete.png
│   ├── test_imported_spirits.png
│   ├── test_label.png
│   ├── test_missing_warning.png
│   └── test_wine.png
│
├── tests/
│   ├── test_api.py
│   ├── test_extraction.py
│   └── test_validation.py
│
├── .gitignore
└── README.md
```
## Requirements
- Python 3.11+
- Node.js
- npm
- Tesseract OCR
- OpenAI API key

## Backend Setup

Clone the repository:
```text
git clone https://github.com/djdmello30/ttb-label-verifier.git
cd ttb-label-verifier
```
Create a virtual environment:
```text
python -m venv .venv
```
Activate on Windows:
```text
.venv\Scripts\activate
```
Install the backend dependencies:
```text
pip install -r backend/requirements.txt
```

## Environment Variables
Create a .env file in the project root:
```text
OPENAI_API_KEY=your_openai_api_key
```
Do not commit your .env file or API key to GitHub.

The repository uses .gitignore to prevent environment secrets from being committed.

## Running the Backend

From the project root:
```text
uvicorn backend.app.main:app --reload
```
The API will be available at:
```text
http://127.0.0.1:8000
```
FastAPI interactive documentation:
```text
http://127.0.0.1:8000/docs
```
## API Endpoints
**Health Check** 
```text
GET /health
```
Example response:
```text
{
  "status": "healthy"
}
```
## OCR
```text
POST /ocr
```
Accepts:

- JPG
- PNG
- WEBP

The endpoint extracts raw text from the uploaded label image.

Example response:
```text
{
  "success": true,
  "filename": "label.png",
  "text": "RIVER VALLEY BREWING CO..."
}
```
## Label Extraction
```text
POST /extract
```
Pipeline:
```text
Image
  ↓
OCR
  ↓
AI Extraction
  ↓
Structured Label Fields
```
The endpoint returns the OCR text and extracted label information.
## Complete Analysis
```text
POST /analyze
```
The /analyze endpoint runs the complete compliance pipeline:
```text
Image
  ↓
OCR
  ↓
AI Extraction
  ↓
Validation
  ↓
Compliance Result
```
Example:
```text
{
  "success": true,
  "filename": "label.png",
  "ocr_text": "...",
  "label": {
    "beverage_type": "beer",
    "brand_name": "RIVER VALLEY BREWING CO.",
    "class_type": "AMERICAN LAGER"
  },
  "validation": {
    "status": "PASS",
    "passed": 4,
    "warnings": 0,
    "errors": 0
  }
}
```
## Compliance Results

The prototype validator produces three possible results.

# PASS

All required prototype screening checks passed.
```text
PASS
```
# REVIEW

The system detected a warning that requires additional review.
```text
REVIEW
```
# FAIL

One or more required prototype screening checks failed.
```text
FAIL
```
Example:
```text
{
  "status": "FAIL",
  "passed": 7,
  "warnings": 0,
  "errors": 1
}
```
## Label Information Extracted

The system can extract the following information:
```text
| Field              | Description                        |
| ------------------ | ---------------------------------- |
| Beverage Type      | Beer, wine, or distilled spirits   |
| Brand Name         | Brand/product name                 |
| Class / Type       | Beverage classification            |
| Alcohol Content    | Alcohol by volume                  |
| Proof              | Proof when present                 |
| Net Contents       | Container volume                   |
| Producer Name      | Producer, bottler, distiller, etc. |
| Producer Address   | Producer/bottler address           |
| Importer Name      | Importer                           |
| Importer Address   | Importer address                   |
| Country of Origin  | Explicit country of origin         |
| Government Warning | Government health warning          |
| Confidence         | AI extraction confidence           |
| Source Evidence    | OCR text supporting the extraction |

```
## Extraction Design Principles

The AI extraction system is intentionally designed to minimize hallucinated information.

# Producer information

A company name by itself is not automatically considered a producer.

Producer information requires explicit language such as:
```text
Distilled by
Distilled and bottled by
Bottled by
Produced by
Produced and bottled by
Bottled for
Processor
Distiller
```
# Import information

Importer information is extracted when the label contains explicit language such as:
```text
IMPORTED BY
IMPORTED AND BOTTLED BY
IMPORTED FOR
```
# Country of Origin

Country of origin is only extracted when explicitly stated.

Examples:
```text
PRODUCT OF SCOTLAND
PRODUCT OF FRANCE
COUNTRY OF ORIGIN: ITALY
```
The system does not infer country of origin from:

- Brand name
- Producer name
- Producer address
- Importer name
- Beverage type
- Class/type

# Missing Information

When information is not present, the extraction system returns:
```text
null
```
rather than guessing.

# Government Warning Detection

The system checks whether the required government warning is present.

For example:
```text
GOVERNMENT WARNING:

According to the Surgeon General,
women should not drink alcoholic beverages
during pregnancy because of the risk of birth defects.
```
The system also detects incomplete or corrupted warning text and can flag it for compliance review.

## Compliance Validation

The current prototype implements simplified validation rules.

# Common Requirements

The validator checks for:

- Brand name
- Class/type designation
- Net contents
- Government warning
- Distilled Spirits

Additional checks include:

- Alcohol content
- Import status
- Importer name
- Importer address
- Country of origin
- Producer information for domestic spirits

If import status cannot be determined, the system can return:
```text
REVIEW
```
## Testing

The project uses pytest.

Run the complete test suite:
```text
python -m pytest tests/ -v
```
Current test suite:
```text
20 passed
```
The tests cover:

- API root endpoint
- API health endpoint
- Unsupported image types
- OCR pipeline
- Complete analysis pipeline
- Beer labels
- Wine labels
- Imported spirits
- Domestic spirits
- Missing importer information
- Missing producer information
- Missing country of origin
- Missing government warning
- Corrupted government warning
- Unknown beverage types
- AI extraction
- Missing extraction fields

The API tests mock OCR and AI extraction where appropriate, keeping the test suite independent of:

- Tesseract installation
- OpenAI API credits
- Network availability

## Frontend Setup

Navigate to the frontend directory:

```text
cd frontend
```

Install dependencies:

```text
npm install
```
Start the development server:

```text
npm run dev
```
Vite will display the local development URL in the terminal.

## Example Analysis

Example beer label:

```text
RIVER VALLEY BREWING CO.
AMERICAN LAGER


5.0% Alc. by Vol.


12 FL OZ (355 mL)


BREWED AND BOTTLED BY
RIVER VALLEY BREWING CO.
123 BREWERY ROAD
PORTLAND, OR 97201


GOVERNMENT WARNING:


According to the Surgeon General,
women should not drink alcoholic beverages
during pregnancy because of the risk of birth defects.
```

Expected screening result:

```text
Beverage Type: beer
Brand: RIVER VALLEY BREWING CO.
Class/Type: AMERICAN LAGER
Alcohol Content: 5.0% Alc. by Vol.
Net Contents: 12 FL OZ (355 mL)
Producer: RIVER VALLEY BREWING CO.
Producer Address: 123 BREWERY ROAD PORTLAND, OR 97201
Government Warning: Detected


Result: PASS
```
## Project Status

The current prototype includes:

 - FastAPI backend
 - OCR service
 - AI extraction service
 - Structured Pydantic models
 - Compliance validation service
 - Complete /analyze pipeline
 - React frontend
 - API tests
 - Extraction tests
 - Validation tests
 - Imported spirits validation
 - Domestic spirits validation
 - Government warning validation
 - 20 passing automated tests
 - GitHub repository

## Future Improvements

Potential future improvements include:

 - Improved OCR preprocessing
 - Additional TTB compliance rules
 - Expanded beverage categories
 - Improved AI confidence scoring
 - Label image quality detection
 - Human review workflow
 - Database storage
 - User authentication
 - Audit logging
 - Configurable compliance rules
 - Production deployment
 - Expanded automated test coverage
 - Improved frontend reporting

## Limitations

This project is a prototype and does not implement the complete body of TTB regulations.

Potential limitations include:

- OCR errors
- Poor image quality
- Unusual label layouts
- AI extraction errors
- Incomplete label information
- Complex regulatory requirements
- Need for human review

The system should therefore be treated as a screening and decision-support tool, not an official regulatory approval system.

## Disclaimer

This software is an experimental/prototype compliance screening system.

It does not provide legal advice and does not constitute:

- Official TTB approval
- Regulatory certification
- A legal determination of compliance

Always consult the applicable TTB regulations and qualified regulatory professionals for formal compliance decisions.

## License

This project currently does not specify a license.

If this repository will be distributed as open-source software, an appropriate license should be added.