import functools
import inspect
from typing import Callable, ParamSpec
import uuid

from pydantic import BaseModel

from workflowpy.models.shortcuts import Action, OutputDefinition
from workflowpy.value import  PythonActionBuilderValue, Value
from workflowpy.value_type import ValueType

P = ParamSpec('P')


def action():
    def decorator(func: Callable[..., Value | None]) -> PythonActionBuilderValue:
        # signature = inspect.signature(func)
        # return_annot = signature.return_annotation
        # has_output = not (return_annot is inspect.Signature.empty or return_annot is None)

        # @functools.wraps(func)
        # def wrapper(*args, **kwargs):
        #     actions = func(*args, **kwargs)
        #     if not isinstance(actions, list):
        #         actions = [actions]
        #     if has_output:
        #         actions.WFWorkflowActionParameters.setdefault(
        #             'UUID', str(uuid.uuid4()).upper()
        #         )
        #     return action

        builder = PythonActionBuilderValue(func)

        return builder

    return decorator
