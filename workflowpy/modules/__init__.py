import ast
from workflowpy import value_type as T
from workflowpy.definitions.action import action
from workflowpy.models.shortcuts import Action, OutputDefinition
from workflowpy.utils import find_action_with_uuid
from workflowpy.value import (
    MagicVariableValue,
    ShortcutValue as V,
    token_attachment,
    token_string,
)
from workflowpy.value import TokenAttachmentValue, TokenStringValue, Value

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
    return action.output


@action()
def _str(a: L, /, value: V):
    return TokenStringValue(value)


modules = {
    'workflowpy': {},
    '': {'input': _input, 'print': _print, 'int': _int, 'str': _str},
}
