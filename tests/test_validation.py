from backend.app.models.label import LabelField, LabelFields
from backend.app.services.validation import validate_label


def field(value, source=None, confidence=0.95):
    return LabelField(
        value=value,
        confidence=confidence,
        source_text=source or value
    )


def complete_warning():
    return (
        "GOVERNMENT WARNING: "
        "According to the Surgeon General, "
        "women should not drink alcoholic beverages "
        "during pregnancy because of the risk of birth defects."
    )


def test_valid_beer_passes():
    label = LabelFields(
        beverage_type=field("beer", "AMERICAN LAGER"),
        brand_name=field("RIVER VALLEY BREWING CO."),
        class_type=field("AMERICAN LAGER"),
        alcohol_content=field("5.0% Alc. by Vol."),
        net_contents=field("12 FL OZ (355 mL)"),
        producer_name=field(
            "RIVER VALLEY BREWING CO.",
            "BREWED AND BOTTLED BY RIVER VALLEY BREWING CO."
        ),
        producer_address=field(
            "123 BREWERY ROAD PORTLAND, OR 97201"
        ),
        government_warning=field(complete_warning()),
    )

    result = validate_label(label)

    assert result.status == "PASS"
    assert result.errors == 0
    assert result.warnings == 0


def test_valid_wine_passes():
    label = LabelFields(
        beverage_type=field("wine", "CABERNET SAUVIGNON"),
        brand_name=field("SUNSET VALLEY VINEYARDS"),
        class_type=field("CABERNET SAUVIGNON"),
        alcohol_content=field("13.5% Alc. by Vol."),
        net_contents=field("750 mL"),
        producer_name=field(
            "SUNSET VALLEY VINEYARDS",
            "PRODUCED AND BOTTLED BY SUNSET VALLEY VINEYARDS"
        ),
        producer_address=field(
            "456 VINEYARD ROAD NAPA, CA 94558"
        ),
        government_warning=field(complete_warning()),
    )

    result = validate_label(label)

    assert result.status == "PASS"
    assert result.errors == 0
    assert result.warnings == 0


def test_missing_government_warning_fails():
    label = LabelFields(
        beverage_type=field("beer"),
        brand_name=field("RIVER VALLEY BREWING CO."),
        class_type=field("AMERICAN LAGER"),
        alcohol_content=field("5.0% Alc. by Vol."),
        net_contents=field("12 FL OZ (355 mL)"),
        producer_name=field("RIVER VALLEY BREWING CO."),
        producer_address=field(
            "123 BREWERY ROAD PORTLAND, OR 97201"
        ),
        government_warning=None,
    )

    result = validate_label(label)

    assert result.status == "FAIL"
    assert result.errors == 1

    assert any(
        issue.field == "government_warning"
        for issue in result.issues
    )


def test_corrupted_government_warning_fails():
    corrupted_warning = (
        "GOVERNMENT WARNING: "
        "According to the Surgeon General, "
        "women should not drink alcoholic "
        "havaranac AIIrinn nrannanry haraiica"
    )

    label = LabelFields(
        beverage_type=field("distilled_spirits"),
        brand_name=field("OLD WORLD DISTILLERY"),
        class_type=field(
            "SCOTTISH SINGLE MALT SCOTCH WHISKY"
        ),
        alcohol_content=field("40% Alc./Vol."),
        net_contents=field("750 mL"),
        importer_name=field("ABC IMPORTS LLC"),
        importer_address=field(
            "100 MARKET STREET NEW YORK, NY 10001"
        ),
        country_of_origin=field("Scotland"),
        government_warning=field(corrupted_warning),
        is_imported=True,
    )

    result = validate_label(label)

    assert result.status == "FAIL"

    assert any(
        issue.field == "government_warning"
        for issue in result.issues
    )


def test_imported_spirits_require_importer_and_country():
    label = LabelFields(
        beverage_type=field("distilled_spirits"),
        brand_name=field("OLD WORLD DISTILLERY"),
        class_type=field(
            "SCOTTISH SINGLE MALT SCOTCH WHISKY"
        ),
        alcohol_content=field("40% Alc./Vol."),
        net_contents=field("750 mL"),
        government_warning=field(complete_warning()),
        is_imported=True,
    )

    result = validate_label(label)

    assert result.status == "FAIL"

    fields = {issue.field for issue in result.issues}

    assert "importer_name" in fields
    assert "importer_address" in fields
    assert "country_of_origin" in fields


def test_domestic_spirits_require_producer_information():
    label = LabelFields(
        beverage_type=field("distilled_spirits"),
        brand_name=field("OLD TOM DISTILLERY"),
        class_type=field(
            "Kentucky Straight Bourbon Whiskey"
        ),
        alcohol_content=field("45% Alc./Vol."),
        net_contents=field("750 mL"),
        government_warning=field(complete_warning()),
        is_imported=False,
    )

    result = validate_label(label)

    assert result.status == "FAIL"

    fields = {issue.field for issue in result.issues}

    assert "producer_name" in fields
    assert "producer_address" in fields


def test_unknown_beverage_type_requires_review():
    label = LabelFields(
        beverage_type=field("unknown"),
        brand_name=field("TEST BRAND"),
        class_type=field("TEST TYPE"),
        net_contents=field("750 mL"),
        government_warning=field(complete_warning()),
    )

    result = validate_label(label)

    assert result.status == "REVIEW"
    assert result.warnings >= 1

    assert any(
        issue.field == "beverage_type"
        for issue in result.issues
    )