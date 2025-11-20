import json
from typing import Callable, List, Dict, Any, Type, TypeVar, cast

from langchain_core.messages import BaseMessage
from altk.pre_tool_guard_toolkit import IToolInvoker, ToolGuardRunInput, ToolFunctionsInvoker, ToolGuardRunOutput, ToolGuardComponentConfig, PreToolGuardComponent
from altk.toolkit_core.core.toolkit import AgentPhase
# from altk.toolkit_core.llm.base import get_llm
from lfx.log.logger import logger


# MODEL: str = "gpt-4o-2024-08-06" #FIXME
# LLM_PROVIDER: str = "azure" #FIXME
class DummyToolInvoker(IToolInvoker):
    T = TypeVar("T")
    def invoke(self, toolname: str, arguments: Dict[str, Any], return_type: Type[T])->T:
        pass

def tool_guard_validation(toolguard_path: str, fc: List[Dict], messages: List[BaseMessage], tools: List[Callable]) -> ToolGuardRunOutput:
    """Umbrella function for tool guards invocation

    Args:
        toolguard_path: path to toolguard generated code
        fc: the function to be called, along with its arguments
        messages: conversation history till this point
        tools: a list of all tool specs

    Returns:
        ToolGuardRunOutput: potentially with a violation object
    """
    config = ToolGuardComponentConfig()
    component = PreToolGuardComponent(config=config)

    tool_name = fc[0]['function']['name']
    tool_args = {"args": json.loads(fc[0]['function']['arguments'])}
    tool_invoker = DummyToolInvoker()
    toolguard_input = ToolGuardRunInput(
        generated_guard_dir=toolguard_path,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_invoker=tool_invoker,
        messages=messages,
        metadata={}
    )
    toolguard_output = cast(
        ToolGuardRunOutput,
        component.process(toolguard_input, phase=AgentPhase.RUNTIME),
    )
    return toolguard_output