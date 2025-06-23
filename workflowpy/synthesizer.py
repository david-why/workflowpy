from typing import Any

from workflowpy.models.shortcuts import Action, Shortcut, ShortcutType


class Synthesizer:
    """
    This class is responsible for synthesizing a Shortcut object.
    """

    def __init__(self):
        self.actions: list[Action] = []
        self.functions: dict[str, list[Action]] = {}

    def synthesize(self) -> Shortcut:
        if self.functions:
            raise NotImplementedError("Functions are not implemented yet!")
        return Shortcut(WFWorkflowActions=self.actions)
