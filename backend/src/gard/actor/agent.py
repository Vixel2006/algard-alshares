from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from gard.models import FunctionInfo, VulnerabilityReport, Patch
from gard.actor.generator import get_patch_generator
from gard.logger import get_logger

logger = get_logger(__name__)


class ActorState(TypedDict):
    vulnerability_report: VulnerabilityReport
    function_info: FunctionInfo
    test_code: Optional[str]
    patch: Optional[Patch]
    messages: list


def prepare_context_node(state: ActorState) -> ActorState:
    logger.info("prepare_context_node called", function=state["function_info"].name)
    return {
        **state,
        "messages": state.get("messages", [])
        + [AIMessage(content="Prepared context for patch generation")],
    }


def generate_patch_node(state: ActorState) -> ActorState:
    logger.info(
        "generate_patch_node called",
        function=state["function_info"].name,
    )

    generator = get_patch_generator()
    patch = generator.generate_patch(
        state["function_info"],
        state["vulnerability_report"],
        state.get("test_code"),
    )

    return {
        **state,
        "patch": patch,
        "messages": state.get("messages", [])
        + [
            AIMessage(
                content=f"Generated patch for {state['function_info'].name}: {patch.explanation}"
            )
        ],
    }


def create_actor_agent():
    workflow = StateGraph(ActorState)

    workflow.add_node("prepare", prepare_context_node)
    workflow.add_node("generate", generate_patch_node)

    workflow.set_entry_point("prepare")
    workflow.add_edge("prepare", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


actor_agent = create_actor_agent()


def run_actor_agent(
    function_info: FunctionInfo,
    vulnerability_report: VulnerabilityReport,
    test_code: Optional[str] = None,
) -> Patch:
    initial_state: ActorState = {
        "function_info": function_info,
        "vulnerability_report": vulnerability_report,
        "test_code": test_code,
        "patch": None,
        "messages": [],
    }

    result = actor_agent.invoke(initial_state)
    return result["patch"]
