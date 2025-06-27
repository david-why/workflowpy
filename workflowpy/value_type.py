from typing import ClassVar


class ValueType:
    ALL_TYPES: ClassVar['list[ValueType]'] = []

    def __init__(
        self,
        name: str,
        content_item_class: str,
        properties: dict[str, 'ValueType'],
        python_class: type | tuple[type, ...] | None = None,
    ):
        self.name = name
        self.content_item_class = content_item_class
        self.properties = properties
        self.python_class = (
            python_class
            if isinstance(python_class, (tuple, type(None)))
            else (python_class,)
        )
        ValueType.ALL_TYPES.append(self)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ValueType):
            return NotImplemented
        return value.content_item_class == self.content_item_class

    __hash__ = object.__hash__

    def __repr__(self):
        return f'<ValueType name={self.name}>'

_file_size = ValueType('File size', 'WFFileSizeContentItem', {})
any = ValueType('', '', {})  # FIXME ???

file = ValueType('File', 'WFGenericFileContentItem', {'File Size': _file_size})
text = ValueType('Text', 'WFStringContentItem', {'File Size': _file_size}, str)
number = ValueType('Number', 'WFNumberContentItem', {}, (float, int))
boolean = ValueType('Boolean', 'WFBooleanContentItem', {}, bool)
dictionary = ValueType(
    'Dictionary', 'WFDictionaryContentItem', {'Keys': text, 'Values': any}, dict
)
