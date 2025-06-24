import copy
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict

from workflowpy.models.shortcuts import Action
from workflowpy.value_type import ValueType
from workflowpy import value_type as T


class Value:
    """
    Values are the objects that only exist in the compilation phase.
    They represent any value (duh) that a variable can hold.
    """

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        raise TypeError(f"Value of type {self.__class__.__name__} is not synthesizable")

    def getattr(self, key: str) -> 'Value':
        raise TypeError(f"Cannot getattr on value of type {self.__class__.__name__}")


class PythonValue(Value):
    pass


class PythonModuleValue(PythonValue):
    def __init__(self, /, **children: PythonValue):
        self.children = children

    def getattr(self, key: str):
        return self.children[key]


class PythonActionBuilderValue(PythonValue):
    def __init__(self, /, func: Callable[..., Value | None]):
        self.func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


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

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        if isinstance(self.value, str):
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.gettext',
                WFWorkflowActionParameters={'WFTextActionText': self.value},
            ).with_output('Text', T.text)
            actions.append(action)
            assert action.output
            return action.output.synthesize(actions)
        if isinstance(self.value, (int, float)):
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.number',
                WFWorkflowActionParameters={'WFNumberActionNumber': str(self.value)},
            ).with_output('Number', T.number)
            actions.append(action)
            assert action.output
            return action.output.synthesize(actions)
        assert False


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


# "pseudo" value, will never be held by a variable
class TokenStringValue(ShortcutValue):
    def __init__(self, *parts: str | ShortcutValue):
        self.parts = parts

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        if len(self.parts) == 1:
            if isinstance(self.parts[0], TokenStringValue):
                return self.parts[0].synthesize(actions)
            return self.parts[0]  # type: ignore  # FIXME maybe...?
        attachments = {}
        text = ''
        for part in self.parts:
            if isinstance(part, str):
                text += part
            else:
                val = part.synthesize(actions)
                attachments[f'{{{len(text)}, 1}}'] = val
                text += '\ufffc'
        return {
            'Value': {'attachmentsByRange': attachments, 'string': text},
            'WFSerializationType': 'WFTextTokenString',
        }


# also pseudo
class TokenAttachmentValue(ShortcutValue):
    def __init__(self, value: ShortcutValue):
        self.value = value

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        return {
            'Value': self.value.synthesize(actions),
            'WFSerializationType': 'WFTextTokenAttachment',
        }
