import json
from typing import Optional
from google import genai
from gard.config import get_config
from gard.models import FunctionInfo, VulnerabilityReport, Patch
from gard.logger import get_logger
from gard.actor.diff import generate_diff

logger = get_logger(__name__)


class PatchGenerator:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if self.client is None:
            config = get_config()
            if not config.validate():
                raise ValueError("GEMINI_API_KEY is not set")
            self.client = genai.Client(api_key=config.gemini_api_key)
        return self.client

    def _build_prompt(
        self,
        function_info: FunctionInfo,
        vulnerability_report: VulnerabilityReport,
        test_code: Optional[str] = None,
    ) -> str:
        prompt = f"""You are a security expert specializing in code vulnerability remediation. 
Your task is to analyze the following function, identify any security vulnerabilities, and generate a secure patch.

## Vulnerable Function
File: {function_info.file_path}
Function Name: {function_info.name}
```
{function_info.code}
```
"""
        if test_code:
            prompt += f"""
## Associated Tests
Please ensure the patch maintains the same functionality. Tests:
```
{test_code}
```
"""
        else:
            prompt += """
## Associated Tests
No tests found for this function. Ensure the patch maintains the original functionality.
"""

        prompt += """
## Requirements
1. Generate the patched function code that fixes the security vulnerability
2. Provide a clear explanation of what was changed and why
3. The patch should maintain the original function signature
4. Output your response as JSON with the following format:
```json
{{
  "patched_code": "...",
  "explanation": "..."
}}
```

Respond only with valid JSON, no additional text.
"""
        return prompt

    def generate_patch(
        self,
        function_info: FunctionInfo,
        vulnerability_report: VulnerabilityReport,
        test_code: Optional[str] = None,
    ) -> Patch:
        logger.info(
            "Generating patch",
            function=function_info.name,
            confidence=vulnerability_report.confidence,
        )

        prompt = self._build_prompt(function_info, vulnerability_report, test_code)

        client = self._get_client()
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        try:
            result = json.loads(response.text)
            patched_code = result.get("patched_code", "")
            explanation = result.get("explanation", "No explanation provided")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini response", error=str(e))
            patched_code = function_info.code
            explanation = "Failed to generate patch"

        diff = generate_diff(function_info.code, patched_code)

        return Patch(
            function_name=function_info.name,
            file_path=function_info.file_path,
            original_code=function_info.code,
            patched_code=patched_code,
            explanation=explanation,
            diff=diff,
        )


def get_patch_generator(model_name: str = "gemini-2.0-flash") -> PatchGenerator:
    return PatchGenerator(model_name)
