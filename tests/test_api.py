from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.label import LabelField, LabelFields


client = TestClient(app)
# A tiny valid PNG image.
PNG_BYTES = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01"
        b"\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"\x00\x00\x00\x0cIDAT"
        b"\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00"
        b"\x05\x00\x01\xff"
        b"\x89\x99=\x1d"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

def complete_warning():
    return (
        "GOVERNMENT WARNING: "
        "According to the Surgeon General, "
        "women should not drink alcoholic beverages "
        "during pregnancy because of the risk of birth defects."
    )


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["version"] == "0.1.0"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ocr_rejects_unsupported_file_type():
    response = client.post(
        "/ocr",
        files={
            "file": (
                "test.txt",
                b"This is not an image.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert "Unsupported image type" in data["error"]


def test_extract_rejects_unsupported_file_type():
    response = client.post(
        "/extract",
        files={
            "file": (
                "test.txt",
                b"This is not an image.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert "Unsupported image type" in data["error"]


def test_analyze_rejects_unsupported_file_type():
    response = client.post(
        "/analyze",
        files={
            "file": (
                "test.txt",
                b"This is not an image.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert "Unsupported image type" in data["error"]


def test_analyze_valid_image(monkeypatch):
    """
    Test the complete /analyze API pipeline while mocking
    OCR and AI extraction.

    This keeps the automated test independent of:
    - Tesseract installation
    - OpenAI API credits
    - network availability
    """

    fake_ocr_text = """
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
    """

    fake_label = LabelFields(
        beverage_type=LabelField(
            value="beer",
            confidence=0.99,
            source_text="AMERICAN LAGER",
        ),
        brand_name=LabelField(
            value="RIVER VALLEY BREWING CO.",
            confidence=0.95,
            source_text="RIVER VALLEY BREWING CO.",
        ),
        class_type=LabelField(
            value="AMERICAN LAGER",
            confidence=0.99,
            source_text="AMERICAN LAGER",
        ),
        alcohol_content=LabelField(
            value="5.0% Alc. by Vol.",
            confidence=0.98,
            source_text="5.0% Alc. by Vol.",
        ),
        net_contents=LabelField(
            value="12 FL OZ (355 mL)",
            confidence=0.98,
            source_text="12 FL OZ (355 mL)",
        ),
        producer_name=LabelField(
            value="RIVER VALLEY BREWING CO.",
            confidence=0.99,
            source_text="BREWED AND BOTTLED BY RIVER VALLEY BREWING CO.",
        ),
        producer_address=LabelField(
            value="123 BREWERY ROAD PORTLAND, OR 97201",
            confidence=0.98,
            source_text="123 BREWERY ROAD PORTLAND, OR 97201",
        ),
        government_warning=LabelField(
            value=complete_warning(),
            confidence=0.95,
            source_text=complete_warning(),
        ),
    )

    def fake_extract_text(image):
        return fake_ocr_text

    def fake_extract_label_fields(ocr_text):
        return fake_label

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_text",
        fake_extract_text,
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_label_fields",
        fake_extract_label_fields,
    )


    response = client.post(
        "/analyze",
        files={
            "file": (
                "test_beer.png",
                PNG_BYTES,
                "image/png",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["filename"] == "test_beer.png"

    assert "ocr_text" in data
    assert "label" in data
    assert "validation" in data

    assert data["label"]["beverage_type"]["value"] == "beer"

    assert (
        data["label"]["brand_name"]["value"]
        == "RIVER VALLEY BREWING CO."
    )

    assert data["label"]["class_type"]["value"] == "AMERICAN LAGER"

    assert data["validation"]["status"] == "PASS"

    assert data["validation"]["errors"] == 0
    assert data["validation"]["warnings"] == 0

def test_analyze_imported_spirits_passes(monkeypatch):
    """Imported spirits with importer and country should pass."""

    fake_ocr_text = """
    OLD WORLD DISTILLERY
    SCOTTISH SINGLE MALT SCOTCH WHISKY
    40% Alc./Vol.
    750 mL

    IMPORTED BY
    ABC IMPORTS LLC
    100 MARKET STREET
    NEW YORK, NY 10001

    PRODUCT OF SCOTLAND

    GOVERNMENT WARNING:
    According to the Surgeon General,
    women should not drink alcoholic beverages
    during pregnancy because of the risk of birth defects.
    """

    fake_label = LabelFields(
        beverage_type=LabelField(
            value="distilled_spirits",
            confidence=0.98,
            source_text="SCOTTISH SINGLE MALT SCOTCH WHISKY",
        ),
        brand_name=LabelField(
            value="OLD WORLD DISTILLERY",
            confidence=0.95,
            source_text="OLD WORLD DISTILLERY",
        ),
        class_type=LabelField(
            value="SCOTTISH SINGLE MALT SCOTCH WHISKY",
            confidence=0.98,
            source_text="SCOTTISH SINGLE MALT SCOTCH WHISKY",
        ),
        alcohol_content=LabelField(
            value="40% Alc./Vol.",
            confidence=0.98,
            source_text="40% Alc./Vol.",
        ),
        net_contents=LabelField(
            value="750 mL",
            confidence=0.98,
            source_text="750 mL",
        ),
        importer_name=LabelField(
            value="ABC IMPORTS LLC",
            confidence=0.98,
            source_text="IMPORTED BY ABC IMPORTS LLC",
        ),
        importer_address=LabelField(
            value="100 MARKET STREET NEW YORK, NY 10001",
            confidence=0.95,
            source_text="100 MARKET STREET NEW YORK, NY 10001",
        ),
        country_of_origin=LabelField(
            value="Scotland",
            confidence=0.98,
            source_text="PRODUCT OF SCOTLAND",
        ),
        government_warning=LabelField(
            value=complete_warning(),
            confidence=0.95,
            source_text=complete_warning(),
        ),
        is_imported=True,
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_text",
        lambda image: fake_ocr_text,
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_label_fields",
        lambda text: fake_label,
    )

    response = client.post(
        "/analyze",
        files={
            "file": (
                "imported_scotch.png",
                PNG_BYTES,
                "image/png",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["validation"]["status"] == "PASS"
    assert data["validation"]["errors"] == 0
    assert data["validation"]["warnings"] == 0


def test_analyze_imported_spirits_missing_country_fails(monkeypatch):
    """Imported spirits without country of origin should fail."""

    fake_label = LabelFields(
        beverage_type=LabelField(
            value="distilled_spirits",
            confidence=0.98,
            source_text="SCOTTISH SINGLE MALT SCOTCH WHISKY",
        ),
        brand_name=LabelField(
            value="OLD WORLD DISTILLERY",
            confidence=0.95,
            source_text="OLD WORLD DISTILLERY",
        ),
        class_type=LabelField(
            value="SCOTTISH SINGLE MALT SCOTCH WHISKY",
            confidence=0.98,
            source_text="SCOTTISH SINGLE MALT SCOTCH WHISKY",
        ),
        alcohol_content=LabelField(
            value="40% Alc./Vol.",
            confidence=0.98,
            source_text="40% Alc./Vol.",
        ),
        net_contents=LabelField(
            value="750 mL",
            confidence=0.98,
            source_text="750 mL",
        ),
        importer_name=LabelField(
            value="ABC IMPORTS LLC",
            confidence=0.98,
            source_text="IMPORTED BY ABC IMPORTS LLC",
        ),
        importer_address=LabelField(
            value="100 MARKET STREET NEW YORK, NY 10001",
            confidence=0.95,
            source_text="100 MARKET STREET NEW YORK, NY 10001",
        ),
        government_warning=LabelField(
            value=complete_warning(),
            confidence=0.95,
            source_text=complete_warning(),
        ),
        is_imported=True,
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_text",
        lambda image: "Imported Scotch label",
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_label_fields",
        lambda text: fake_label,
    )

    response = client.post(
        "/analyze",
        files={
            "file": (
                "missing_country.png",
                PNG_BYTES,
                "image/png",
            )
        },
    )

    data = response.json()

    assert data["success"] is True
    assert data["validation"]["status"] == "FAIL"

    assert any(
        issue["field"] == "country_of_origin"
        and issue["severity"] == "error"
        for issue in data["validation"]["issues"]
    )


def test_analyze_imported_spirits_missing_importer_fails(monkeypatch):
    """Imported spirits without importer information should fail."""

    fake_label = LabelFields(
        beverage_type=LabelField(
            value="distilled_spirits",
            confidence=0.98,
            source_text="SCOTTISH SINGLE MALT SCOTCH WHISKY",
        ),
        brand_name=LabelField(
            value="OLD WORLD DISTILLERY",
            confidence=0.95,
            source_text="OLD WORLD DISTILLERY",
        ),
        class_type=LabelField(
            value="SCOTTISH SINGLE MALT SCOTCH WHISKY",
            confidence=0.98,
            source_text="SCOTTISH SINGLE MALT SCOTCH WHISKY",
        ),
        alcohol_content=LabelField(
            value="40% Alc./Vol.",
            confidence=0.98,
            source_text="40% Alc./Vol.",
        ),
        net_contents=LabelField(
            value="750 mL",
            confidence=0.98,
            source_text="750 mL",
        ),
        country_of_origin=LabelField(
            value="Scotland",
            confidence=0.98,
            source_text="PRODUCT OF SCOTLAND",
        ),
        government_warning=LabelField(
            value=complete_warning(),
            confidence=0.95,
            source_text=complete_warning(),
        ),
        is_imported=True,
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_text",
        lambda image: "Imported Scotch label",
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_label_fields",
        lambda text: fake_label,
    )

    response = client.post(
        "/analyze",
        files={
            "file": (
                "missing_importer.png",
                PNG_BYTES,
                "image/png",
            )
        },
    )

    data = response.json()

    assert data["success"] is True
    assert data["validation"]["status"] == "FAIL"

    assert any(
        issue["field"] == "importer_name"
        and issue["severity"] == "error"
        for issue in data["validation"]["issues"]
    )


def test_analyze_domestic_spirits_missing_producer_fails(monkeypatch):
    """Domestic spirits without producer information should fail."""

    fake_label = LabelFields(
        beverage_type=LabelField(
            value="distilled_spirits",
            confidence=0.98,
            source_text="KENTUCKY STRAIGHT BOURBON WHISKEY",
        ),
        brand_name=LabelField(
            value="OLD TOM",
            confidence=0.95,
            source_text="OLD TOM",
        ),
        class_type=LabelField(
            value="KENTUCKY STRAIGHT BOURBON WHISKEY",
            confidence=0.98,
            source_text="KENTUCKY STRAIGHT BOURBON WHISKEY",
        ),
        alcohol_content=LabelField(
            value="45% Alc./Vol.",
            confidence=0.98,
            source_text="45% Alc./Vol.",
        ),
        net_contents=LabelField(
            value="750 mL",
            confidence=0.98,
            source_text="750 mL",
        ),
        government_warning=LabelField(
            value=complete_warning(),
            confidence=0.95,
            source_text=complete_warning(),
        ),
        is_imported=False,
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_text",
        lambda image: "Domestic bourbon label",
    )

    monkeypatch.setattr(
        "backend.app.routes.labels.extract_label_fields",
        lambda text: fake_label,
    )

    response = client.post(
        "/analyze",
        files={
            "file": (
                "missing_producer.png",
                PNG_BYTES,
                "image/png",
            )
        },
    )

    data = response.json()

    assert data["success"] is True
    assert data["validation"]["status"] == "FAIL"

    producer_fields = {
        issue["field"]
        for issue in data["validation"]["issues"]
        if issue["severity"] == "error"
    }

    assert "producer_name" in producer_fields
    assert "producer_address" in producer_fields