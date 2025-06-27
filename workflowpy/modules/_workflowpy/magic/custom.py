import ast as a
import warnings
from typing import Any, cast

from workflowpy import value_type as T
from workflowpy.definitions.action import ActionHelper as H
from workflowpy.definitions.action import action
from workflowpy.value import (
    DictionaryFieldValue,
    ItemValue,
    PythonTypeValue,
    ShortcutInputValue,
    ShortcutValue,
    TokenAttachmentValue,
    TokenStringValue,
    Value,
)
from workflowpy.value_type import ValueType

type V = ShortcutValue


def _compile_expr(h: H, node: a.expr):
    if isinstance(node, a.Dict):
        result = {}
        for key, value in zip(node.keys, node.values):
            assert key is not None, '**dict expression is not supported'
            assert isinstance(key, a.Constant), 'Only constant dict keys are supported'
            assert isinstance(key.value, str), 'Only string dict keys are supported'
            result[key.value] = _compile_expr(h, value)
        return result
    if isinstance(node, a.List):
        return [_compile_expr(h, x) for x in node.elts]
    if isinstance(node, a.Constant):
        assert isinstance(
            node.value, (int, float, str, bool)
        ), f'Value {node.value!r} is not supported'
        if isinstance(node.value, float):
            return str(node.value)
        return node.value
    if isinstance(node, a.Call):
        func = h.visit(node.func)
        if func is _attachment:
            return h.visit(node).synthesize(h.actions)
        raise ValueError(f'Function call {func} is not allowed')
    if isinstance(node, a.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, a.Constant):
                assert isinstance(value.value, str)
                parts.append(value.value)
            elif isinstance(value, a.FormattedValue):
                parts.append(h.visit(value))
            else:
                raise TypeError(
                    f'Type {value.__class__.__name__} not supported in this f-string'
                )
        return h.token_string(*parts)
        # parts = [_compile_expr(h, x) for x in node.values]
        # return h.token_string(*parts)
    # if isinstance(node, a.FormattedValue):
    #     assert node.conversion == -1, 'Conversions in f-strings are not supported'
    #     return _compile_expr(h, node.value)
    raise TypeError(f'Node type {node.__class__.__name__} is not supported')


@action(raw_params=[0, 1, 2, 'id', 'params', 'output'])
def _action(
    h: H,
    /,
    id: a.expr,
    params: a.expr | None = None,
    output: a.expr | None = None,
):
    # this has basically the same signature as h.action
    if not isinstance(id, a.Constant) or not isinstance(id.value, str):
        raise TypeError('Action ID must be a literal string')
    if params is not None and not isinstance(params, a.Dict):
        raise TypeError('Action parameters must be a literal dict')
    if output is not None and not (
        isinstance(output, a.Tuple)
        and len(output.elts) == 2
        and isinstance(output.elts[0], a.Constant)
        and isinstance(output.elts[0].value, str)
    ):
        raise TypeError('Action output must be a literal 2-tuple')

    action_id = id.value
    action_params = cast(dict, _compile_expr(h, params) if params is not None else {})
    action_output = None
    if output is not None:
        output_name = cast(str, cast(a.Constant, output.elts[0]).value)
        output_type_value = h.visit(output.elts[1])
        if not isinstance(output_type_value, PythonTypeValue):
            raise TypeError('Action output specification is not a type value')
        output_type = output_type_value.value_type
        action_output = (output_name, output_type)

    return h.action(action_id, action_params, action_output)


@action()
def _attachment(h: H, /, value: V):
    return TokenAttachmentValue(value)


module = {'action': _action, 'attachment': _attachment}
