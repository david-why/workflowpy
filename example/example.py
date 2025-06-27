from workflowpy.magic import *
from workflowpy.magic.custom import *
from workflowpy.magic import types as T

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

print(text)
