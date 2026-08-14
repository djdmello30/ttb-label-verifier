import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.models.label import LabelFields


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY was not found. "
        "Make sure it is defined in your .env file."
    )

client = OpenAI(api_key=api_key)


def extract_label_fields(ocr_text: str) -> LabelFields:
    """
    Convert raw OCR text into structured alcohol beverage label fields.
    """

    system_prompt = """
    You are an information extraction system for U.S. alcohol beverage labels.

    Your job is to extract information ONLY from the supplied OCR text.

    IMPORTANT RULES:

    1. Never invent, infer, or guess information that is not explicitly present.

    2. A brand name is NOT automatically a producer, bottler, distiller,
       processor, or importer.

    3. Only populate producer_name when the OCR explicitly associates a
       company/person with a production or bottling role.

       Examples of supporting phrases include:
       - Distilled by
       - Distilled and bottled by
       - Bottled by
       - Produced by
       - Produced and bottled by
       - Bottled for
       - Processor
       - Distiller

    4. Do NOT put importer information into producer_name.

    5. If a company name appears by itself and there is no wording indicating
       a producer, bottler, distiller, or processor role, DO NOT use it as
       producer_name.

    6. Only populate producer_address when an actual address is explicitly
       present and associated with the producer, bottler, distiller,
       processor, or similar entity.

    7. Do not construct or infer an address from other information.

    8. Importer rules:

       - If the OCR contains "IMPORTED BY", extract the company into
         importer_name.

       - If the OCR contains "IMPORTED AND BOTTLED BY", extract the
         importer/bottler appropriately.

       - If an address is explicitly associated with the importer,
         extract it into importer_address.

       - Do not put importer information into producer_name unless the
         OCR explicitly identifies that entity as the producer as well.

    9. Determine is_imported as follows:

       - Return true ONLY when the OCR explicitly indicates that the
         product is imported.

       - Examples include:
         - Imported by
         - Imported and bottled by
         - Imported for
         - Similar explicit import language

       - Return false ONLY when the OCR explicitly provides evidence
         that the product is domestic/U.S.-produced.

       - Otherwise return null.

    10. Only populate country_of_origin when the OCR explicitly identifies
        the country of origin.

        Examples include:
        - Product of Scotland
        - Product of France
        - Country of Origin: Italy

    11. Never infer country_of_origin from:
        - Brand name
        - Producer name
        - Producer address
        - Importer name
        - Beverage type
        - Class/type designation

    12. Determine beverage_type only from evidence in the OCR text.

    13. Use exactly one of:
        - beer
        - wine
        - distilled_spirits
        - unknown

    14. Confidence must be between 0.0 and 1.0.

    15. source_text must contain the exact OCR text that supports the
        extracted value.

    16. If information is missing, return null.

    17. Do not treat the absence of information as evidence that a product
        is imported or domestic.

    18. Government warning:

        Only populate government_warning when the OCR contains evidence
        of the government health warning.

        Do not invent missing portions of the warning.

        If only a partial warning is visible in the OCR, extract only the
        text actually present and use an appropriately lower confidence.

    19. When extracting a value, prefer the smallest exact span of OCR text
        that directly supports that value.

    20. When multiple pieces of information appear together, keep each field
        separate and do not combine unrelated information.
    """

    user_prompt = f"""
Extract the structured label information from this OCR text:

-------------------------
{ocr_text}
-------------------------
"""

    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=system_prompt,
        input=user_prompt,
        text_format=LabelFields,
    )

    if response.output_parsed is None:
        raise RuntimeError("The AI model did not return structured label data.")

    return response.output_parsed