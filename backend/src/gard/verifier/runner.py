import subprocess
import json
import os
from abc import ABC, abstractmethod
from typing import List, Optional
from gard.logger import get_logger
from gard.models import VerificationResult

logger = get_logger(__name__)

class TestRunner(ABC):
    @abstractmethod
    def run_tests(self, function_name: str, file_path: str, test_file: Optional[str] = None) -> VerificationResult:
        pass

class PytestRunner(TestRunner):
    def run_tests(self, function_name: str, file_path: str, test_file: Optional[str] = None) -> VerificationResult:
        logger.info("Running pytest", function=function_name, file=file_path, test_file=test_file)
        
        if not test_file:
            return VerificationResult(
                function_name=function_name,
                status="error",
                tests_run=0,
                tests_passed=0,
                test_output="No test file found for function",
                regression_detected=False
            )

        # Run pytest with json-report if possible, or just parse output
        # For now, let's use a simple command and capture output
        cmd = ["pytest", test_file, "-k", function_name, "--verbose"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            passed = "passed" in output.lower() and result.returncode == 0
            
            # Simple parsing for now
            # In a real world scenario, we'd use pytest-json-report
            return VerificationResult(
                function_name=function_name,
                status="passed" if passed else "failed",
                tests_run=1, # Mock for now
                tests_passed=1 if passed else 0,
                test_output=output,
                regression_detected=not passed
            )
            
        except subprocess.TimeoutExpired:
            return VerificationResult(
                function_name=function_name,
                status="error",
                tests_run=0,
                tests_passed=0,
                test_output="Test execution timed out",
                regression_detected=False
            )
        except Exception as e:
            logger.error("Error running pytest", error=str(e))
            return VerificationResult(
                function_name=function_name,
                status="error",
                tests_run=0,
                tests_passed=0,
                test_output=f"Error: {str(e)}",
                regression_detected=False
            )

class JestRunner(TestRunner):
    def run_tests(self, function_name: str, file_path: str, test_file: Optional[str] = None) -> VerificationResult:
        logger.info("Running jest", function=function_name, file=file_path, test_file=test_file)
        
        if not test_file:
            return VerificationResult(
                function_name=function_name,
                status="error",
                tests_run=0,
                tests_passed=0,
                test_output="No test file found for function",
                regression_detected=False
            )

        cmd = ["npx", "jest", test_file, "-t", function_name, "--verbose"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            passed = result.returncode == 0
            
            return VerificationResult(
                function_name=function_name,
                status="passed" if passed else "failed",
                tests_run=1,
                tests_passed=1 if passed else 0,
                test_output=output,
                regression_detected=not passed
            )
            
        except subprocess.TimeoutExpired:
            return VerificationResult(
                function_name=function_name,
                status="error",
                tests_run=0,
                tests_passed=0,
                test_output="Test execution timed out",
                regression_detected=False
            )
        except Exception as e:
            logger.error("Error running jest", error=str(e))
            return VerificationResult(
                function_name=function_name,
                status="error",
                tests_run=0,
                tests_passed=0,
                test_output=f"Error: {str(e)}",
                regression_detected=False
            )
