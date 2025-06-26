from typing import ClassVar


class ValueType:
    def __init__(
        self,
        name: str,
        content_item_class: str,
        properties: dict[str, 'ValueType'],
        python_class: type | None = None,
    ):
        self.name = name
        self.content_item_class = content_item_class
        self.properties = properties
        self.python_class = python_class

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ValueType):
            return NotImplemented
        return value.content_item_class == self.content_item_class


_file_size = ValueType('File size', 'WFFileSizeContentItem', {})

text = ValueType('Text', 'WFStringContentItem', {'File Size': _file_size}, str)
number = ValueType('Number', 'WFNumberContentItem', {}, float)

any = ValueType('', '', {})  # FIXME ???
