from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from workflowpy.models.shortcuts import Action


def find_action_with_uuid(actions: list[Action], uuid: str):
    for action in actions:
        if action.uuid == uuid:
            return action
    assert False
