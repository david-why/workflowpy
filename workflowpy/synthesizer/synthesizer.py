from typing import Any

from workflowpy.models.shortcuts import Action, Shortcut, ShortcutType


class Synthesizer:
    """
    This class is responsible for synthesizing a Shortcut object.
    """

    def __init__(self):
        self.actions: list[Action] = []

    def add_action(self, identifier: str, parameters: dict[str, Any]) -> None:
        action = Action(
            WFWorkflowActionIdentifier=identifier, WFWorkflowActionParameters=parameters
        )
        self.actions.append(action)

    def synthesize(self) -> Shortcut:
        return Shortcut(WFWorkflowActions=self.actions)
