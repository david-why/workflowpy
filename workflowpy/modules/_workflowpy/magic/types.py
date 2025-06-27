from workflowpy.value import PythonTypeValue
from workflowpy import value_type as T


module = {
    'any': PythonTypeValue(T.any),
    'file': PythonTypeValue(T.file),
    'text': PythonTypeValue(T.text),
    'number': PythonTypeValue(T.number),
    'boolean': PythonTypeValue(T.boolean),
    'dictionary': PythonTypeValue(T.dictionary),
}
