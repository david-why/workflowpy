import copy
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict

from workflowpy.models.shortcuts import Action
from workflowpy.value_type import ValueType


class Value:
    """
    Values are the objects that only exist in the compilation phase.
    They represent any value (duh) that a variable can hold.
    """

    def synthesize(self, actions: list[Action]) -> Any:
        raise TypeError(f"Value of type {self.__class__.__name__} is not synthesizable")


class PythonValue(Value):
    pass


class PythonModuleValue(PythonValue):
    def __init__(self, /, **children: PythonValue):
        self.children = children

    def getattr(self, key: str):
        return self.children[key]


class OutputDefinition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    type: ValueType


class PythonActionBuilderValue(PythonValue):
    def __init__(
        self, /, func: Callable[..., Action | list[Action]], output_definition
    ):
        self.func = func
        self.output_definition = output_definition

    def __call__(self, *args: Any, **kwargs: Any) -> list[Action]:
        result = self.func(*args, **kwargs)
        if isinstance(result, list):
            return result
        return [result]


class ShortcutValue(Value):
    def __init__(self):
        self.aggrandizements = []

    def aggrandized(self, type: str, fields: dict[str, Any]):
        obj = copy.copy(self)
        obj.aggrandizements = self.aggrandizements.copy()
        obj.aggrandizements.append({'Type': type, **fields})
        return obj


class ConstantValue(ShortcutValue):
    def __init__(self, value: str | int | float):
        self.value = value

    def synthesize(self, actions: list[Action]) -> Any:
        return super().synthesize(actions)


class MagicVariableValue(ShortcutValue):
    def __init__(self, uuid: str, name: str) -> None:
        self.uuid = uuid
        self.name = name

    def synthesize(self, actions: list[Action]) -> Any:
        return {
            'OutputName': self.name,
            'OutputUUID': self.uuid,
            'Type': 'ActionOutput',
        }
