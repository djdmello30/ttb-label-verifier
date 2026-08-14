from backend.app.models.label import LabelFields
from backend.app.models.validation import (
    ValidationIssueResponse,
    ValidationResult,
)
import re
def validate_government_warning(warning_text: str | None) -> bool:
    """
    Check whether the extracted government warning contains
    the key required wording.

    This is a prototype screening check and is not a substitute
    for formal TTB review.
    """

    if not warning_text:
        return False

    normalized = re.sub(
        r"\s+",
        " ",
        warning_text.upper()
    ).strip()

    required_phrases = [
        "GOVERNMENT WARNING",
        "ACCORDING TO THE SURGEON GENERAL",
        "WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY",
        "RISK OF BIRTH DEFECTS",
    ]

    return all(
        phrase in normalized
        for phrase in required_phrases
    )

def validate_label(label: LabelFields) -> ValidationResult:
    """
    Validate extracted alcohol label information against
    a simplified set of TTB requirements.

    This is a prototype compliance screening tool, not
    a substitute for formal TTB label approval.
    """

    issues = []

    def add_issue(field: str, severity: str, message: str):
        issues.append(
            ValidationIssueResponse(
                field=field,
                severity=severity,
                message=message,
            )
        )

    # ---------------------------------------------------------
    # Determine beverage type
    # ---------------------------------------------------------

    beverage_type = (
        label.beverage_type.value
        if label.beverage_type and label.beverage_type.value
        else "unknown"
    )

    # ---------------------------------------------------------
    # Common checks
    # ---------------------------------------------------------

    if not label.brand_name or not label.brand_name.value:
        add_issue(
            "brand_name",
            "error",
            "Brand name was not detected."
        )

    if not label.class_type or not label.class_type.value:
        add_issue(
            "class_type",
            "error",
            "Class/type designation was not detected."
        )

    if not label.net_contents or not label.net_contents.value:
        add_issue(
            "net_contents",
            "error",
            "Net contents statement was not detected."
        )

    # Government warning
    warning_text = (
        label.government_warning.value
        if label.government_warning
        else None
    )

    if not validate_government_warning(warning_text):
        add_issue(
            "government_warning",
            "error",
            "Government health warning statement was missing or incomplete."
        )

    # ---------------------------------------------------------
    # Distilled spirits
    # ---------------------------------------------------------

    if beverage_type == "distilled_spirits":

        if not label.alcohol_content or not label.alcohol_content.value:
            add_issue(
                "alcohol_content",
                "error",
                "Alcohol content was not detected."
            )

        # -----------------------------------------------------
        # Imported distilled spirits
        # -----------------------------------------------------

        if label.is_imported is True:

            if not label.importer_name or not label.importer_name.value:
                add_issue(
                    "importer_name",
                    "error",
                    "Importer name was not detected."
                )

            if not label.importer_address or not label.importer_address.value:
                add_issue(
                    "importer_address",
                    "error",
                    "Importer address was not detected."
                )

            if not label.country_of_origin or not label.country_of_origin.value:
                add_issue(
                    "country_of_origin",
                    "error",
                    "Country of origin was not detected for an imported product."
                )

        # -----------------------------------------------------
        # Domestic distilled spirits
        # -----------------------------------------------------

        elif label.is_imported is False:

            if not label.producer_name or not label.producer_name.value:
                add_issue(
                    "producer_name",
                    "error",
                    "Bottler, producer, distiller, processor, or similar responsible party was not detected."
                )

            if not label.producer_address or not label.producer_address.value:
                add_issue(
                    "producer_address",
                    "error",
                    "Producer/bottler/distiller address was not detected."
                )

        # -----------------------------------------------------
        # Unknown import status
        # -----------------------------------------------------

        else:

            add_issue(
                "is_imported",
                "warning",
                "Import status could not be determined. Additional review is required."
            )

    # ---------------------------------------------------------
    # Unknown beverage type
    # ---------------------------------------------------------

    elif beverage_type == "unknown":

        add_issue(
            "beverage_type",
            "warning",
            "Beverage type could not be determined. Additional review is required."
        )

    # ---------------------------------------------------------
    # Calculate summary
    # ---------------------------------------------------------

    errors = sum(
        1 for issue in issues
        if issue.severity == "error"
    )

    warnings = sum(
        1 for issue in issues
        if issue.severity == "warning"
    )

    # ---------------------------------------------------------
    # Determine status
    # ---------------------------------------------------------

    if errors > 0:
        status = "FAIL"
    elif warnings > 0:
        status = "REVIEW"
    else:
        status = "PASS"

    # ---------------------------------------------------------
    # Calculate passed checks
    # ---------------------------------------------------------

    # Count the validation checks that apply to this label.
    total_checks = 4  # brand, class/type, net contents, warning

    if beverage_type in ("beer", "wine"):
        total_checks += 1  # alcohol content

    elif beverage_type == "distilled_spirits":
        total_checks += 1  # alcohol content

        if label.is_imported is True:
            total_checks += 3  # importer name, importer address, country
        elif label.is_imported is False:
            total_checks += 2  # producer name, producer address
        else:
            total_checks += 1  # import status review

    passed = max(
        total_checks - errors - warnings,
        0
    )

    return ValidationResult(
        status=status,
        passed=passed,
        warnings=warnings,
        errors=errors,
        issues=issues,
    )