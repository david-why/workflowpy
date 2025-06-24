__all__ = ['modules']


from workflowpy.definitions.action import action
from workflowpy.models.shortcuts import Action, OutputDefinition
from workflowpy.value import (
    ShortcutValue as V,
    TokenAttachmentValue,
    TokenStringValue,
    Value,
)
from workflowpy import value_type as T

type L = list[Action]


@action()
def _input(actions: L, /, prompt: V):
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.ask',
        WFWorkflowActionParameters={
            'WFAllowsMultilineText': False,
            # 'WFAskActionDefaultAnswer': '',
            'WFAskActionPrompt': TokenStringValue(prompt).synthesize(actions),
        },
    ).with_output('Ask for Input', T.text)
    actions.append(action)
    return action.output


@action()
def _print(actions: L, /, *args: V):
    to_print = args[0] if len(args) == 1 else TokenStringValue(*args)
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.showresult',
        WFWorkflowActionParameters={'Text': to_print.synthesize(actions)},
    )
    actions.append(action)


@action()
def _int(a: L, /, value: V):
    action = Action(
        WFWorkflowActionIdentifier='is.workflow.actions.number',
        WFWorkflowActionParameters={
            'WFNumberActionNumber': TokenAttachmentValue(value).synthesize(a)
        },
    ).with_output('Number', T.number)
    a.append(action)
    return action.output


modules = {'workflowpy': {}, '': {'input': _input, 'print': _print, 'int': _int}}
