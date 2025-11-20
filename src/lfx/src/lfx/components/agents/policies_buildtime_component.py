import asyncio
import os
from typing import cast
import json
from lfx.io import MessageTextInput
from langflow.inputs import MultilineInput

from lfx.base.agents.agent import LCToolsAgentComponent
from lfx.io import Output

from langchain_core.runnables import Runnable
from lfx.schema.message import Message
from lfx.log.logger import logger
from os.path import join

from altk.toolkit_core.llm.base import get_llm
from altk.toolkit_core.core.toolkit import AgentPhase
from altk.pre_tool_guard_toolkit import PreToolGuardComponent, ToolGuardComponentConfig, ToolGuardBuildInput, ToolGuardBuildOutput

from lfx.components.agents.open_api import tools_to_openapi 

MODEL = "gpt-4o-2024-08-06"
STEP1 = "Step_1"
STEP2 = "Step_2"

class PoliciesComponent(LCToolsAgentComponent):
    def create_agent_runnable(self) -> Runnable:
        pass

    display_name = "ToolGuard Buildtime"
    description = "Buildtime (offline) component converting textual policies to executable ToolGuard code."
    documentation: str = "..."  # once we have a URL or alike
    icon = "clipboard-check"  # consider also file-text
    name = "policies"
    beta = True

    inputs = [
        MultilineInput(
            name="policies",
            display_name="Business Policies",
            info="Company business policies: concise, well-defined, self-contained policies, one in a line.",
            value="<example: division by zero is prohibited>",
            # advanced=True,
        ),
        MessageTextInput(
            name="guard_code_path",
            display_name="ToolGuards Generated Code Path",
            info="Automatically generated ToolGuards code",
            # show_if={"enable_tool_guard": True},  # conditional visibility  # check how to do that
            #advanced=False,
        ),

        *LCToolsAgentComponent.get_base_inputs()[0:1],
    ]
    outputs = [
        Output(display_name="ToolGuard Code", name="guard_code", method="build_guards"),
    ]

    def run(self):
        pass

    def build_guards(self) -> Message:
        """ToolGuard buidtime component (both steps)

        Args:
        Returns:
            A textual message with the generated code for human review
        """

        if self.policies:
            logger.info(f"🔒️ToolGuard: Building guards for {self.policies}")
            logger.info(f"🔒️ToolGuard: Using the following tools {self.tools}")
        else:
            logger.error("🔒️ToolGuard: Policies cannot be empty!")

        OPENAILiteLLMClientOutputVal = get_llm("litellm.output_val")
        config = ToolGuardComponentConfig(
            llm_client = OPENAILiteLLMClientOutputVal(
                model_name=MODEL,
                custom_llm_provider="azure", #FIXME
            )
        )
        component = PreToolGuardComponent(config = config)
        
        work_dir = self.guard_code_path
        os.makedirs(work_dir, exist_ok=True)
        open_api = tools_to_openapi(self.tools)
        open_api_path = join(work_dir, "open_api.json")
        with open(open_api_path, "w") as f:
            json.dump(open_api, f, indent=2)

        toolguard_step1_dir = join(work_dir, STEP1)
        out_dir = join(work_dir, STEP2)
        build_input = ToolGuardBuildInput(
            policy_text=self.policies,
            tools=open_api_path,
            step1_dir = toolguard_step1_dir,
            out_dir=out_dir,
        )
        output = cast(ToolGuardBuildOutput, asyncio.run(
            component.aprocess(build_input, phase=AgentPhase.BUILDTIME)
        ))
        return Message(text=output.root_dir, sender="toolguard buildtime")
    