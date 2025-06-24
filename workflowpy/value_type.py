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


_file_size = ValueType('File size', 'WFFileSizeContentItem', {})

text = ValueType('Text', 'WFStringContentItem', {'File Size': _file_size})
