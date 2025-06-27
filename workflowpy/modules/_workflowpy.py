import ast
from typing import TYPE_CHECKING, Any
import warnings

from workflowpy import value_type as T
from workflowpy.definitions.action import action
from workflowpy.models.shortcuts import Action
from workflowpy.value import (
    DictionaryFieldValue,
    ItemValue,
    PythonTypeValue,
    ShortcutInputValue,
    ShortcutValue,
    TokenStringValue,
    token_attachment,
    token_string,
)
from workflowpy.value_type import ValueType

if TYPE_CHECKING:
    from workflowpy.compiler import Compiler

type L = list[Action]
type V = ShortcutValue


@action()
def shortcut_input(a: L):
    return ShortcutInputValue()


fetch_supported_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']


@action(raw_params=['method', 'headers'], compiler_arg='_compiler')
def fetch(
    a: L,
    /,
    url: V,
    *,
    method: ast.expr | None = None,
    headers: ast.expr | None = None,
    data: V | None = None,
    json: V | None = None,
    _compiler: 'Compiler',
):
    params: dict[str, Any] = {'ShowHeaders': True, 'WFURL': token_string(a, url)}
    if method is not None:
        if not (
            isinstance(method, ast.Constant) and method.value in fetch_supported_methods
        ):
            raise ValueError(
                f'Method must be a literal string from the set {fetch_supported_methods}'
            )
        params['WFHTTPMethod'] = method.value
    if data is not None and json is not None:
        raise ValueError('Only one of data and json can be specified')
    if (data is not None or json is not None) and params.get(
        'WFHTTPMethod', 'GET'
    ) == 'GET':
        raise ValueError('GET requests do not have a body')
    if headers is not None and not isinstance(headers, ast.Dict):
        raise TypeError('Headers must be a literal dict')
    if data is not None:
        params['WFHTTPBodyType'] = 'File'
        params['WFRequestVariable'] = token_attachment(a, data)
    if json is not None:
        params['WFHTTPBodyType'] = 'File'
        convert_action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.gettypeaction',
            WFWorkflowActionParameters={
                'WFFileType': 'public.json',
                'WFInput': token_attachment(a, json),
            },
        ).with_output('File of Type', T.file)
        a.append(convert_action)
        json = convert_action.output
        assert json
        params['WFRequestVariable'] = token_attachment(a, json)
        should_add_header = True
        if headers is not None:
            for key, value in zip(headers.keys, headers.values):
                if (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and key.value.lower() == 'content-type'
                ):
                    warnings.warn(
                        "A header is provided with the key Content-Type. This might cause issues. Please don't provide the Content-Type header when using json=....",
                        UserWarning,
                    )
                    should_add_header = False
                    break
        if should_add_header:
            if headers is None:
                headers = ast.Dict()
            headers.keys.append(ast.Constant(value='Content-Type'))
            headers.values.append(ast.Constant('application/json'))
    if headers is not None:
        header_items = []
        for key, value in zip(headers.keys, headers.values):
            if key is None:
                raise ValueError('**dict syntax not supported in headers dict')
            header_items.append(
                ItemValue(
                    0,
                    TokenStringValue(_compiler.visit(value)),
                    TokenStringValue(_compiler.visit(key)),
                )
            )
        params['WFHTTPHeaders'] = DictionaryFieldValue(*header_items).synthesize(a)
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.downloadurl',
        WFWorkflowActionParameters=params,
    ).with_output('Contents of URL', T.file)
    a.append(action)
    return action.output


App = PythonTypeValue(ValueType('App', 'WFAppContentItem', {'Is Running': T.boolean}))

module = {'shortcut_input': shortcut_input, 'fetch': fetch, 'App': App}
