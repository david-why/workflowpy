import ast
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, overload

from workflowpy.models.shortcuts import Action
from workflowpy.utils import find_action_with_uuid
from workflowpy.value import (
    ItemValue,
    MagicVariableValue,
    PythonFunctionValue,
    ShortcutValue,
    Value,
    item_value,
    token_attachment,
    token_string,
)
from workflowpy.value_type import ValueType

if TYPE_CHECKING:
    from workflowpy.compiler import Compiler

P = ParamSpec('P')


class ActionHelper:
    def __init__(self, compiler: 'Compiler'):
        self.compiler = compiler

    @property
    def actions(self) -> list[Action]:
        return self.compiler.actions

    def find_action(self, uuid: str):
        return find_action_with_uuid(self.actions, uuid)

    def visit(self, node: ast.AST) -> Any:
        return self.compiler.visit(node)

    @overload
    def action(
        self, id: str, params: dict[str, Any] = ..., output: None = None
    ) -> None: ...

    @overload
    def action(
        self, id: str, params: dict[str, Any], output: tuple[str, ValueType]
    ) -> MagicVariableValue: ...

    def action(
        self,
        id: str,
        params: dict[str, Any] | None = None,
        output: tuple[str, ValueType] | None = None,
    ) -> MagicVariableValue | None:
        action = Action(
            WFWorkflowActionIdentifier=id,
            WFWorkflowActionParameters=params or {},
        )
        if output:
            action = action.with_output(output[0], output[1])
        self.actions.append(action)
        return action.output

    def token_string(self, *parts: str | ShortcutValue):
        return token_string(self.actions, *parts)

    def token_attachment(self, value: ShortcutValue):
        return token_attachment(self.actions, value)

    def item_value(self, item_type: int, value: ShortcutValue):
        return item_value(self.actions, item_type, value)


def action(raw_params: list[str | int] | None = None):
    def decorator(func: Callable[..., Value | None]) -> PythonFunctionValue:
        builder = PythonFunctionValue(func, raw_params=raw_params)
        return builder

    return decorator
