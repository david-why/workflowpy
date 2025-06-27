from workflowpy import value_type as T
from workflowpy.definitions.action import ActionHelper as H
from workflowpy.definitions.action import action
from workflowpy.modules import _workflowpy
from workflowpy.value import MagicVariableValue, Value
from workflowpy.value import ShortcutValue as V
from workflowpy.value import TokenStringValue

__all__ = ['register']


def register(module_path: str, module: dict[str, Value]):
    mod = modules
    *parts, last_part = module_path.split('.')
    for part in parts:
        mod = mod.setdefault(part, {})
    if last_part in mod:
        raise ValueError(f'Module {module_path} is already registered')
    mod[last_part] = module


@action()
def _input(h: H, /, prompt: V):
    return h.action(
        'is.workflow.actions.ask',
        {
            'WFAllowsMultilineText': False,
            # 'WFAskActionDefaultAnswer': '',
            'WFAskActionPrompt': h.token_string(prompt),
        },
        ('Ask for Input', T.text),
    )


@action()
def _print(h: H, /, *args: V):
    items: list[V | str] = list(args)
    for i in range(len(items) - 1):
        items.insert(i * 2, ' ')
    h.action('is.workflow.actions.showresult', {'Text': h.token_string(*items)})


@action()
def _int(h: H, /, value: V):
    if isinstance(value, MagicVariableValue):
        input_action = h.find_action(value.uuid)
        if (
            input_action is not None
            and input_action.WFWorkflowActionIdentifier == 'is.workflow.actions.ask'
        ):
            params = input_action.WFWorkflowActionParameters
            params['WFInputType'] = 'Number'
            params['WFAskActionAllowsDecimalNumbers'] = False
            input_action.with_output('Ask for Input', T.number)
            return input_action.output
    output = h.action(
        'is.workflow.actions.number',
        {'WFNumberActionNumber': h.token_attachment(value)},
        ('Number', T.number),
    )

    output = h.action(
        'is.workflow.actions.text.split',
        {
            'WFTextCustomSeparator': '.',
            'WFTextSeparator': 'Custom',
            'text': h.token_attachment(output),
        },
        ('Split Text', T.text),
    )

    output = h.action(
        'is.workflow.actions.getitemfromlist',
        {'WFInput': h.token_attachment(output)},
        ('Item from List', T.text),
    )

    return h.action(
        'is.workflow.actions.number',
        {'WFNumberActionNumber': h.token_attachment(output)},
        ('Number', T.number),
    )


@action()
def _float(h: H, /, value: V):
    if isinstance(value, MagicVariableValue):
        input_action = h.find_action(value.uuid)
        if (
            input_action is not None
            and input_action.WFWorkflowActionIdentifier == 'is.workflow.actions.ask'
        ):
            params = input_action.WFWorkflowActionParameters
            params['WFInputType'] = 'Number'
            input_action.with_output('Ask for Input', T.number)
            return input_action.output
    return h.action(
        'is.workflow.actions.number',
        {'WFNumberActionNumber': h.token_attachment(value)},
        ('Number', T.number),
    )


@action()
def _str(h: H, /, value: V):
    return TokenStringValue(value)


@action()
def _dict(h: H, /, value: V):
    return h.action(
        'is.workflow.actions.detect.dictionary',
        {'WFInput': h.token_attachment(value)},
        ('Dictionary', T.dictionary),
    )


@action()
def _exit(h: H, /, code=None):
    h.action('is.workflow.actions.exit')


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
