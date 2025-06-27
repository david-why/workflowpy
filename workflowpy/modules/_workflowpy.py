import ast
import warnings
from typing import Any

from workflowpy import value_type as T
from workflowpy.definitions.action import ActionHelper as H
from workflowpy.definitions.action import action
from workflowpy.value import (
    DictionaryFieldValue,
    ItemValue,
    PythonTypeValue,
    ShortcutInputValue,
    ShortcutValue,
    TokenStringValue,
)
from workflowpy.value_type import ValueType

type V = ShortcutValue


@action()
def shortcut_input(h: H):
    return ShortcutInputValue()


fetch_supported_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']


@action(raw_params=['method', 'headers'])
def fetch(
    h: H,
    /,
    url: V,
    *,
    method: ast.expr | None = None,
    headers: ast.expr | None = None,
    data: V | None = None,
    json: V | None = None,
):
    params: dict[str, Any] = {'ShowHeaders': True, 'WFURL': h.token_string(url)}
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
        params['WFRequestVariable'] = h.token_attachment(data)
    if json is not None:
        params['WFHTTPBodyType'] = 'File'
        json = h.action(
            'is.workflow.actions.gettypeaction',
            {'WFFileType': 'public.json', 'WFInput': h.token_attachment(json)},
            ('File of Type', T.file),
        )
        params['WFRequestVariable'] = h.token_attachment(json)
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
                    TokenStringValue(h.visit(value)),
                    TokenStringValue(h.visit(key)),
                )
            )
        params['WFHTTPHeaders'] = DictionaryFieldValue(*header_items).synthesize(
            h.actions
        )
    return h.action(
        'is.workflow.actions.downloadurl', params, ('Contents of URL', T.file)
    )


App = PythonTypeValue(ValueType('App', 'WFAppContentItem', {'Is Running': T.boolean}))

module = {'shortcut_input': shortcut_input, 'fetch': fetch, 'App': App}
