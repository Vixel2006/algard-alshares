from typing import Literal
from pydantic import BaseModel


class FunctionInfo(BaseModel):
    name: str
    file_path: str
    start_line: int
    end_line: int
    code: str
    test_file: str | None = None
    test_function_names: list[str] = []


class VulnerabilityReport(BaseModel):
    function_name: str
    file_path: str
    is_vulnerable: bool
    confidence: float


class Patch(BaseModel):
    function_name: str
    file_path: str
    original_code: str
    patched_code: str
    explanation: str
    diff: str


class VerificationResult(BaseModel):
    function_name: str
    status: Literal["passed", "failed", "error"]
    tests_run: int
    tests_passed: int
    test_output: str
    regression_detected: bool


class FullVulnerabilityReport(BaseModel):
    function: FunctionInfo
    vulnerability: VulnerabilityReport
    patch: Patch | None = None
    verification: VerificationResult | None = None
