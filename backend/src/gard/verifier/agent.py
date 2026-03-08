from typing import TypedDict, Annotated, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from gard.models import FunctionInfo, Patch, VerificationResult
from gard.verifier.runner import PytestRunner, JestRunner
from gard.logger import get_logger
import os

logger = get_logger(__name__)

class VerifierState(TypedDict):
    function_info: FunctionInfo
    patch: Patch
    verification_result: Optional[VerificationResult]
    messages: List

def execute_tests_node(state: VerifierState) -> VerifierState:
    logger.info("execute_tests_node called", function=state["function_info"].name)
    
    file_path = state["function_info"].file_path
    ext = os.path.splitext(file_path)[1]
    
    runner = None
    if ext == ".py":
        runner = PytestRunner()
    elif ext in [".js", ".ts", ".tsx", ".jsx"]:
        runner = JestRunner()
    
    if not runner:
        result = VerificationResult(
            function_name=state["function_info"].name,
            status="error",
            tests_run=0,
            tests_passed=0,
            test_output=f"No test runner for extension {ext}",
            regression_detected=False
        )
    else:
        # We assume the patch has been applied or we pass the patched code to the runner
        # In a real system, we might need to write the patched code to a temporary file
        result = runner.run_tests(
            state["function_info"].name,
            file_path,
            state["function_info"].test_file
        )
    
    return {
        **state,
        "verification_result": result,
        "messages": state.get("messages", []) + [
            AIMessage(content=f"Verification result for {state['function_info'].name}: {result.status}")
        ]
    }

def create_verifier_agent():
    workflow = StateGraph(VerifierState)
    
    workflow.add_node("verify", execute_tests_node)
    
    workflow.set_entry_point("verify")
    workflow.add_edge("verify", END)
    
    return workflow.compile()

verifier_agent = create_verifier_agent()

def run_verifier_agent(function_info: FunctionInfo, patch: Patch) -> VerificationResult:
    initial_state: VerifierState = {
        "function_info": function_info,
        "patch": patch,
        "verification_result": None,
        "messages": []
    }
    
    result = verifier_agent.invoke(initial_state)
    return result["verification_result"]
