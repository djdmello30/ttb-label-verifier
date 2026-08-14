from typing import Optional

from pydantic import BaseModel, Field


class LabelField(BaseModel):
    """
    Represents a single piece of information extracted from a label.
    """

    value: Optional[str] = None

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    source_text: Optional[str] = None


class LabelFields(BaseModel):
    """
    Structured information extracted from an alcohol beverage label.
    """

    beverage_type: Optional[LabelField] = None

    brand_name: Optional[LabelField] = None

    class_type: Optional[LabelField] = None

    alcohol_content: Optional[LabelField] = None

    proof: Optional[LabelField] = None

    net_contents: Optional[LabelField] = None

    producer_name: Optional[LabelField] = None

    producer_address: Optional[LabelField] = None

    importer_name: Optional[LabelField] = None

    importer_address: Optional[LabelField] = None

    country_of_origin: Optional[LabelField] = None

    government_warning: Optional[LabelField] = None

    is_imported: Optional[bool] = None