from workflowpy.definitions.action import action
from workflowpy.models.shortcuts import Action
from workflowpy.value import PythonTypeValue, ShortcutInputValue
from workflowpy.value_type import ValueType
from workflowpy import value_type as T

type L = list[Action]


@action()
def shortcut_input(a: L):
    return ShortcutInputValue()


App = PythonTypeValue(ValueType('App', 'WFAppContentItem', {'Is Running': T.boolean}))

module = {'shortcut_input': shortcut_input, 'App': App}
