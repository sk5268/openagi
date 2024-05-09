import json
from typing import Dict, Optional, Union

from pydantic import Field

from openagi.actions.base import BaseAction
from openagi.actions.human_input import HumanCLIInput
from openagi.llms.azure import LLMBaseModel
from openagi.planner.base import BasePlanner
from openagi.prompts.base import BasePrompt
from openagi.prompts.task_creator import TaskCreator
from openagi.utils.extraction import get_last_json


class TaskPlanner(BasePlanner):
    human_intervene: bool = Field(
        default=True, description="If human internvention is required or not."
    )
    actions: Optional[BaseAction] = Field(
        default=HumanCLIInput,
        description="If `human_intervene` is enabled, which action to be performed.",
    )
    prompt: BasePrompt = Field(
        default=TaskCreator(), description="Prompt to be used"
    )  # TODO: Add default planner
    llm: Optional[LLMBaseModel] = Field(default=None, description="LLM Model to be used")

    def _extract_task_from_response(self, llm_response: str) -> Union[str, None]:
        return get_last_json(llm_response)

    def _should_clarify(self, query: str) -> bool:
        # TODO: Setup a way for human intervention

        return False

    def plan(self, query: str) -> Dict:
        prompt: str = self.prompt.base_prompt
        prompt = prompt.replace("{objective}", query)
        resp = self.llm.run(prompt)
        while self.human_intervene and self._should_clarify(resp):
            # TODO: Add logic for taking input from the user using actions
            human_intervene = self.actions(query=query)
            human_intervene.execute()
            pass
        tasks = self._extract_task_from_response(llm_response=resp)
        return tasks