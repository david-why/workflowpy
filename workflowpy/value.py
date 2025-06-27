import ast
import copy
from typing import Any, Callable, Literal

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

    @property
    def type(self) -> ValueType:
        raise TypeError(f"Value of type {self.__class__.__name__} has no content type")

    @property
    def can_get_property(self) -> bool:
        return False

    def copy(self):
        return copy.copy(self)


class PythonValue(Value):
    pass


class PythonModuleValue(PythonValue):
    def __init__(self, /, **children: Any):
        super().__init__()
        self.children = children

    def getattr(self, key: str):
        value = self.children[key]
        if isinstance(value, Value):
            return value
        if isinstance(value, dict):
            return PythonModuleValue(**value)
        raise TypeError(f'Unknown type in module path: {value.__class__.__name__}')


class PythonFunctionValue(PythonValue):
    def __init__(
        self, /, func: Callable[..., Value | None], raw_params: list[str] | None = None
    ):
        super().__init__()
        self.func = func
        self.raw_params = raw_params or []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


class PythonTypeValue(PythonValue):
    def __init__(self, type: ValueType) -> None:
        super().__init__()
        self.value_type = type


class ShortcutValue(Value):
    def __init__(self):
        super().__init__()
        self.aggrandizements = []

    def aggrandized(self, type: str, fields: dict[str, Any]):
        obj = copy.copy(self)
        obj.aggrandizements = self.aggrandizements.copy()
        obj.aggrandizements.append({'Type': type, **fields})
        return obj

    @property
    def _aggrandize_props(self):
        if self.aggrandizements:
            return {'Aggrandizements': self.aggrandizements}
        return {}

    @property
    def can_get_property(self) -> bool:
        return not any(
            x['Type'] == 'WFPropertyVariableAggrandizement'
            for x in self.aggrandizements
        )


class ConstantValue(ShortcutValue):
    def __init__(self, value: str | int | float):
        super().__init__()
        self.value = value

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        if isinstance(self.value, str):
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.gettext',
                WFWorkflowActionParameters={'WFTextActionText': self.value},
            ).with_output('Text', T.text)
            actions.append(action)
            assert action.output
            return action.output.synthesize(actions) | self._aggrandize_props
        if isinstance(self.value, (int, float)):
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.number',
                WFWorkflowActionParameters={'WFNumberActionNumber': str(self.value)},
            ).with_output('Number', T.number)
            actions.append(action)
            assert action.output
            return action.output.synthesize(actions) | self._aggrandize_props
        assert False

    @property
    def type(self):
        if isinstance(self.value, str):
            return T.text
        if isinstance(self.value, (int, float)):
            return T.number
        assert False


class MagicVariableValue(ShortcutValue):
    def __init__(self, uuid: str, name: str, type: ValueType) -> None:
        super().__init__()
        self.uuid = uuid
        self.name = name
        self._type = type

    def synthesize(self, actions: list[Action]) -> Any:
        return {
            'OutputName': self.name,
            'OutputUUID': self.uuid,
            'Type': 'ActionOutput',
        } | self._aggrandize_props

    @property
    def type(self):
        return self._type


class VariableValue(ShortcutValue):
    def __init__(self, name: str, type: ValueType) -> None:
        super().__init__()
        self.name = name
        self._type = type

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        return {'Type': 'Variable', 'VariableName': self.name} | self._aggrandize_props

    @property
    def type(self):
        return self._type


class ShortcutInputValue(ShortcutValue):
    def __init__(self):
        super().__init__()
        self._type = T.any

    @property
    def type(self):
        return self._type

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        return {'Type': 'ExtensionInput'} | self._aggrandize_props


# "pseudo" value, will never be held by a variable
class TokenStringValue(ShortcutValue):
    def __init__(self, *parts: str | ShortcutValue):
        super().__init__()
        self.parts = parts

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        if len(self.parts) == 1:
            if isinstance(self.parts[0], TokenStringValue):
                return self.parts[0].synthesize(actions)
            if isinstance(self.parts[0], str):
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
        super().__init__()
        self.value = value

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        return {
            'Value': self.value.synthesize(actions),
            'WFSerializationType': 'WFTextTokenAttachment',
        }


# pseudo, used in list/dict items
class ItemValue(ShortcutValue):
    def __init__(
        self, item_type: int, value: ShortcutValue, key: TokenStringValue | None = None
    ):
        super().__init__()
        self.item_type = item_type
        self.value = value
        self.key = key

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        return {
            'WFItemType': self.item_type,
            'WFValue': self.value.synthesize(actions),
        } | ({'WFKey': self.key.synthesize(actions)} if self.key is not None else {})


# pseudo
class DictionaryFieldValue(ShortcutValue):
    def __init__(self, *items: ItemValue):
        super().__init__()
        self.items = items

    def synthesize(self, actions: list[Action]) -> dict[str, Any]:
        return {
            'Value': {
                'WFDictionaryFieldValueItems': [
                    x.synthesize(actions) for x in self.items
                ]
            },
            'WFSerializationType': 'WFDictionaryFieldValue',
        }


# helper functions


def token_string(actions: list[Action], *parts: str | ShortcutValue):
    return TokenStringValue(*parts).synthesize(actions)


def token_attachment(actions: list[Action], value: ShortcutValue):
    return TokenAttachmentValue(value).synthesize(actions)


def item_value(actions: list[Action], item_type: int, value: ShortcutValue):
    return ItemValue(item_type=item_type, value=value).synthesize(actions)
