from types import SimpleNamespace

from backend.app.services.extraction import extract_label_fields

class MockResponses:
    def __init__(self, response):
        self.response = response

    def parse(self, **kwargs):
        return self.response
class MockClient:
    def __init__(self, response):
        self.responses = MockResponses(response)

def make_mock_response(label):
    return SimpleNamespace(
        output_parsed=label
    )


def test_extract_beer(monkeypatch):
    from backend.app.services import extraction
    from backend.app.models.label import LabelFields, LabelField

    expected = LabelFields(
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
    )

    mock_response = make_mock_response(expected)

    monkeypatch.setattr(
        extraction,
        "client",
        MockClient(mock_response),
    )

    ocr_text = """
    RIVER VALLEY BREWING CO.
    AMERICAN LAGER

    5.0% Alc. by Vol.

    12 FL OZ (355 mL)
    """

    result = extract_label_fields(ocr_text)

    assert result.beverage_type.value == "beer"
    assert result.brand_name.value == "RIVER VALLEY BREWING CO."
    assert result.class_type.value == "AMERICAN LAGER"
    assert result.alcohol_content.value == "5.0% Alc. by Vol."
    assert result.net_contents.value == "12 FL OZ (355 mL)"


def test_extract_imported_spirits(monkeypatch):
    from backend.app.services import extraction
    from backend.app.models.label import LabelFields, LabelField

    expected = LabelFields(
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
        is_imported=True,
    )

    mock_response = make_mock_response(expected)

    monkeypatch.setattr(
        extraction,
        "client",
        MockClient(mock_response),
    )

    ocr_text = """
    OLD WORLD DISTILLERY
    SCOTTISH SINGLE MALT SCOTCH WHISKY

    40% Alc./Vol.
    750 mL

    IMPORTED BY ABC IMPORTS LLC
    100 MARKET STREET
    NEW YORK, NY 10001

    PRODUCT OF SCOTLAND
    """

    result = extract_label_fields(ocr_text)

    assert result.beverage_type.value == "distilled_spirits"
    assert result.importer_name.value == "ABC IMPORTS LLC"
    assert result.importer_address.value == (
        "100 MARKET STREET NEW YORK, NY 10001"
    )
    assert result.country_of_origin.value == "Scotland"
    assert result.is_imported is True


def test_missing_fields_return_none(monkeypatch):
    from backend.app.services import extraction
    from backend.app.models.label import LabelFields, LabelField

    expected = LabelFields(
        beverage_type=LabelField(
            value="beer",
            confidence=0.95,
            source_text="AMERICAN LAGER",
        ),
        brand_name=LabelField(
            value="RIVER VALLEY BREWING CO.",
            confidence=0.95,
            source_text="RIVER VALLEY BREWING CO.",
        ),
    )

    mock_response = make_mock_response(expected)

    monkeypatch.setattr(
        extraction,
        "client",
        MockClient(mock_response),
    )

    result = extract_label_fields(
        "RIVER VALLEY BREWING CO.\nAMERICAN LAGER"
    )

    assert result.beverage_type.value == "beer"
    assert result.brand_name.value == "RIVER VALLEY BREWING CO."

    assert result.producer_name is None
    assert result.producer_address is None
    assert result.country_of_origin is None
    assert result.government_warning is None