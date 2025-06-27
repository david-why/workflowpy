from workflowpy import value_type as T
from workflowpy.definitions.action import action
from workflowpy.models.shortcuts import Action
from workflowpy.modules import _workflowpy
from workflowpy.utils import find_action_with_uuid
from workflowpy.value import MagicVariableValue
from workflowpy.value import ShortcutValue as V
from workflowpy.value import TokenStringValue, token_attachment, token_string

type L = list[Action]

__all__ = ['modules']


@action()
def _input(a: L, /, prompt: V):
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.ask',
        WFWorkflowActionParameters={
            'WFAllowsMultilineText': False,
            # 'WFAskActionDefaultAnswer': '',
            'WFAskActionPrompt': token_string(a, prompt),
        },
    ).with_output('Ask for Input', T.text)
    a.append(action)
    return action.output


@action()
def _print(a: L, /, *args: V):
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.showresult',
        WFWorkflowActionParameters={'Text': token_string(a, *args)},
    )
    a.append(action)


@action()
def _int(a: L, /, value: V):
    if isinstance(value, MagicVariableValue):
        input_action = find_action_with_uuid(a, value.uuid)
        if (
            input_action is not None
            and input_action.WFWorkflowActionIdentifier == 'is.workflow.actions.ask'
        ):
            params = input_action.WFWorkflowActionParameters
            params['WFInputType'] = 'Number'
            params['WFAskActionAllowsDecimalNumbers'] = False
            input_action.with_output('Ask for Input', T.number)
            return input_action.output
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.number',
        WFWorkflowActionParameters={'WFNumberActionNumber': token_attachment(a, value)},
    ).with_output('Number', T.number)
    a.append(action)
    output = action.output
    assert output

    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.text.split',
        WFWorkflowActionParameters={
            'WFTextCustomSeparator': '.',
            'WFTextSeparator': 'Custom',
            'text': token_attachment(a, output),
        },
    ).with_output('Split Text', T.text)
    a.append(action)
    output = action.output
    assert output

    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.getitemfromlist',
        WFWorkflowActionParameters={'WFInput': token_attachment(a, output)},
    ).with_output('Item from List', T.text)
    a.append(action)
    output = action.output
    assert output

    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.number',
        WFWorkflowActionParameters={
            'WFNumberActionNumber': token_attachment(a, output)
        },
    ).with_output('Number', T.number)
    a.append(action)
    output = action.output
    assert output

    return output


@action()
def _float(a: L, /, value: V):
    if isinstance(value, MagicVariableValue):
        input_action = find_action_with_uuid(a, value.uuid)
        if (
            input_action is not None
            and input_action.WFWorkflowActionIdentifier == 'is.workflow.actions.ask'
        ):
            params = input_action.WFWorkflowActionParameters
            params['WFInputType'] = 'Number'
            input_action.with_output('Ask for Input', T.number)
            return input_action.output
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.number',
        WFWorkflowActionParameters={'WFNumberActionNumber': token_attachment(a, value)},
    ).with_output('Number', T.number)
    a.append(action)
    return action.output


@action()
def _str(a: L, /, value: V):
    return TokenStringValue(value)


@action()
def _dict(a: L, /, value: V):
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.detect.dictionary',
        WFWorkflowActionParameters={'WFInput': token_attachment(a, value)},
    ).with_output('Dictionary', T.dictionary)
    a.append(action)
    return action.output


@action()
def _exit(a: L, /, code=None):
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.exit',
        WFWorkflowActionParameters={},
    )
    a.append(action)


modules = {
    'workflowpy': _workflowpy.module,
    '': {
        'input': _input,
        'print': _print,
        'int': _int,
        'float': _float,
        'str': _str,
        'dict': _dict,
        'exit': _exit,
    },
}
