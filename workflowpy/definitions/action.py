import functools
from typing import Callable, ParamSpec
import uuid

from workflowpy.models.shortcuts import Action

P = ParamSpec('P')


def action(has_output: bool = True):
    def decorator(func: Callable[P, Action]) -> Callable[P, Action]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            action = func(*args, **kwargs)
            if has_output:
                action.WFWorkflowActionParameters.setdefault(
                    'UUID', str(uuid.uuid4()).upper()
                )
            return action

        return wrapper

    return decorator
