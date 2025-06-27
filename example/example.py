from workflowpy import *

file = fetch('http://localhost:8889/', method='POST', json={'a': 'b'})

print(file)
