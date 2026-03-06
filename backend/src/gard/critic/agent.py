from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from gard.models import FunctionInfo, VulnerabilityReport
from gard.critic import get_detector, get_function_code, get_function_tests
from gard.logger import get_logger

logger = get_logger(__name__)


class CriticState(TypedDict):
    functions: list[FunctionInfo]
    vulnerability_reports: list[VulnerabilityReport]
    current_function: FunctionInfo | None
    messages: list


def extract_functions_node(state: CriticState) -> CriticState:
    logger.info("extract_functions_node called")
    return {
        **state,
        "vulnerability_reports": [],
        "messages": state.get("messages", [])
        + [AIMessage(content="Extracted functions from workspace")],
    }


def detect_vulnerabilities_node(state: CriticState) -> CriticState:
    logger.info(
        "detect_vulnerabilities_node called", num_functions=len(state["functions"])
    )

    if not state["functions"]:
        return {
            **state,
            "messages": state.get("messages", [])
            + [AIMessage(content="No functions to scan")],
        }

    detector = get_detector()
    reports = detector.detect_vulnerabilities(state["functions"])

    return {
        **state,
        "vulnerability_reports": reports,
        "messages": state.get("messages", [])
        + [
            AIMessage(
                content=f"Scanned {len(state['functions'])} functions, found {sum(1 for r in reports if r.is_vulnerable)} vulnerabilities"
            )
        ],
    }


def should_scan(state: CriticState) -> str:
    if not state.get("functions"):
        return "skip"
    return "scan"


def create_critic_agent():
    workflow = StateGraph(CriticState)

    workflow.add_node("extract", extract_functions_node)
    workflow.add_node("detect", detect_vulnerabilities_node)

    workflow.set_entry_point("extract")

    workflow.add_conditional_edges(
        "extract", should_scan, {"scan": "detect", "skip": END}
    )

    workflow.add_edge("detect", END)

    return workflow.compile()


critic_agent = create_critic_agent()


def run_critic_agent(functions: list[FunctionInfo]) -> list[VulnerabilityReport]:
    initial_state: CriticState = {
        "functions": functions,
        "vulnerability_reports": [],
        "current_function": None,
        "messages": [],
    }

    result = critic_agent.invoke(initial_state)
    return result["vulnerability_reports"]
