# WorkflowPy: Create iOS Shortcuts with Python code

Write plain Python code, and compile it to an iOS Shortcut!

## Example

Write some Python code, put it in a string, and compile it like so:

```python
from workflowpy.compiler import Compiler
from workflowpy.utils import sign_shortcut

code = """
from workflowpy import *
thresholds = [90, 80, 60, 0]
names = ['wonderful', 'great', 'okay', 'terrible']
grade = int(input("Please enter your grade: "))
for i, threshold in enumerate(thresholds):
    if grade > threshold:
        print(f"You are doing {names[i]}!")
        break
"""

shortcut = Compiler().compile(code)
signed_shortcut = sign_shortcut(shortcut)

with open('How are my grades.shortcut', 'wb') as f:
    f.write(signed_shortcut)
```

Now, you can double click the `How are my grades.shortcut` file on your Mac, import it into the Shortcuts app, and run it!

## How it works

This project uses Python's `ast` module to convert your Python code into an Abstract Syntax Tree, which is then traversed to find 
