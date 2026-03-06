from typing import Annotated
from langchain_core.tools import tool
from gard.models import FunctionInfo
from gard.logger import get_logger

logger = get_logger(__name__)

# Note: These tools currently expect the function info to be passed in.
# In a real LangGraph scenario, we might store the detected functions in the state.

@tool
def get_function_code(function_info: FunctionInfo) -> str:
    """Returns the source code of the specified function."""
    return function_info.code

@tool
def get_function_tests(function_info: FunctionInfo) -> str:
    """Returns the test function names associated with the specified function."""
    if not function_info.test_function_names:
        return "No tests found for this function."
    return f"Tests found: {', '.join(function_info.test_function_names)} in {function_info.test_file}"
