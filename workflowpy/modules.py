__all__ = ['modules']


from workflowpy.definitions.action import action
from workflowpy.models.shortcuts import Action
from workflowpy.value import OutputDefinition, Value
from workflowpy import value_type as T


@action(output_definition=OutputDefinition(name='Ask for Input', type=T.text))
def _input(prompt: Value):
    actions = []
    actions.append(
        Action(
            WFWorkflowActionIdentifier='is.workflow.actions.ask',
            WFWorkflowActionParameters={
                'WFAllowsMultilineText': False,
                # 'WFAskActionDefaultAnswer': '',
                'WFAskActionPrompt': prompt.synthesize(actions),
            },
        )
    )
    return actions


modules = {'workflowpy': {}, '': {'input': _input}}
