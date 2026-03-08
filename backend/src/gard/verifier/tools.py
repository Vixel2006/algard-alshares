from gard.models import FunctionInfo, Patch, VerificationResult
from gard.verifier.agent import run_verifier_agent
from gard.logger import get_logger

logger = get_logger(__name__)

def run_unit_tests(function_info: FunctionInfo, patch: Patch) -> VerificationResult:
    """
    Executes unit tests for a given function and its patch.
    """
    logger.info("run_unit_tests tool called", function=function_info.name)
    return run_verifier_agent(function_info, patch)
