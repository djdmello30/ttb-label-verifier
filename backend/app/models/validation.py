from typing import List

from pydantic import BaseModel


class ValidationIssueResponse(BaseModel):
    field: str
    severity: str
    message: str


class ValidationResult(BaseModel):
    status: str
    passed: int
    warnings: int
    errors: int
    issues: List[ValidationIssueResponse]