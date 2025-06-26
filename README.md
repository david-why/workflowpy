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

This project uses Python's `ast` module to convert your Python code into an Abstract Syntax Tree, which is then traversed to convert each line of code into one or more actions in Shortcuts. Because of this nature, not all Python commands are implemented; I'm working on implementing all of them soon!

## Supported Python code

- `from ... import ...`
  - Only supported modules (see the end of [this file](./workflowpy/modules/__init__.py) for details)
- `name = value`
- `input(prompt)` (Ask for Input), `print(value, ...)` (Show Result)
- `int(value)` (Number), `str(value)` (Text)
- `for name in range(val[, val])`
  - Only one or two parameters supported
- `for index, value in enumerate(iterable)`
  - Only unpacking is supported (i.e., two loop variables)
- `for name in list`, `for name in dict`
- `if x [OP] y ... elif ... else`
  - For a number `x`: `[OP]` in `==`, `!=`, `>`, `<`, `<=`, `>=`
  - For text `x`: `[OP]` in `==`, `!=`
  - For dictionary `y`: `[OP]` in `in`
- `break`, `pass`
- `str`, `int`, `float`, `list`, `dict` constants
- F-strings
- `list` and `dict` subscript access (read-only)
- `+`, `-`, `*`, `/` for numbers
- `-number`
- Special constructions:
  - `int(input(prompt))`: an Ask for Input action with integer number type
  - `float(input(prompt))`: an Ask for Input action with number type

More coming soon!

## Type Confusion

Sometimes, the compiler will get confused as to what type a variable is. One common case is when getting a value from a dictionary. This is undesirable because Shortcuts treats things of different types differently; for example, an `if x == y` statement for numbers is different than for text.

To solve this issue, there are two ways:

1. Add an explicit conversion, such as `str(var)`. This will add an extra action (in this case, Text) to the shortcut, but it will ensure the value is now of the given type. The following conversions are supported: `int`, `str`, `float`.
2. If you're confident about the type a thing is, and you're confident that the Shortcuts runtime can figure it out, you can add a type annotation. Only the following annotations are supported: `int`, `float`, `str`, `bool`, `dict`, and `list[one_of_the_above]`. In most cases, it's probably best to use method 1.
