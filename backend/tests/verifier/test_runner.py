import pytest
from unittest.mock import MagicMock, patch
from gard.verifier.runner import PytestRunner
from gard.models import FunctionInfo, VerificationResult

def test_pytest_runner_no_test_file():
    runner = PytestRunner()
    result = runner.run_tests("my_func", "path/to/file.py", None)
    assert result.status == "error"
    assert "No test file found" in result.test_output

@patch("subprocess.run")
def test_pytest_runner_success(mock_run):
    # Mock subprocess success
    mock_run.return_value = MagicMock(
        stdout="1 passed",
        stderr="",
        returncode=0
    )
    
    runner = PytestRunner()
    result = runner.run_tests("my_func", "path/to/file.py", "path/to/test_file.py")
    
    assert result.status == "passed"
    assert not result.regression_detected
    assert mock_run.called

@patch("subprocess.run")
def test_pytest_runner_failure(mock_run):
    # Mock subprocess failure
    mock_run.return_value = MagicMock(
        stdout="1 failed",
        stderr="AssertionError",
        returncode=1
    )
    
    runner = PytestRunner()
    result = runner.run_tests("my_func", "path/to/file.py", "path/to/test_file.py")
    
    assert result.status == "failed"
    assert result.regression_detected
    assert mock_run.called
