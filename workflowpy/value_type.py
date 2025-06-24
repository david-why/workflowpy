from typing import ClassVar


class ValueType:
    def __init__(
        self,
        name: str,
        content_item_class: str,
        properties: dict[str, 'ValueType'],
    ):
        self.name = name
        self.content_item_class = content_item_class
        self.properties = properties

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ValueType):
            return NotImplemented
        return value.content_item_class == self.content_item_class


_file_size = ValueType('File size', 'WFFileSizeContentItem', {})

text = ValueType('Text', 'WFStringContentItem', {'File Size': _file_size})
number = ValueType('Number', 'WFNumberContentItem', {})

any = ValueType('', '', {})  # FIXME ???
