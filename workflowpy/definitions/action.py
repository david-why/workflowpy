import functools
import inspect
from typing import Callable, ParamSpec
import uuid

from pydantic import BaseModel

from workflowpy.models.shortcuts import Action, OutputDefinition
from workflowpy.value import PythonActionBuilderValue, Value
from workflowpy.value_type import ValueType

P = ParamSpec('P')


def action(raw_params: list[str] | None = None, compiler_arg: str | None = None):
    def decorator(func: Callable[..., Value | None]) -> PythonActionBuilderValue:
        builder = PythonActionBuilderValue(func, raw_params=raw_params, compiler_arg=compiler_arg)
        return builder

    return decorator
