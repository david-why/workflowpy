from workflowpy.magic import *
from workflowpy.magic import types as T
from workflowpy.magic.custom import *

file = fetch('http://localhost:8889/', method='POST', json={'a': 'b'})

text = action(
    'is.workflow.actions.setitemname',
    {
        'WFDontIncludeFileExtension': True,
        'WFInput': attachment(file),
        'WFName': 'text.txt',
    },
    ('Renamed Item', T.file),
)

text = action(
    'is.workflow.actions.gettext',
    {'WFTextActionText': f'some{text}thing'},
    ('Text', T.text),
)

print(text)
