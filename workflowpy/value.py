class Value:
    def synthesize(self):
        raise TypeError(
            f"Value of type {self.__class__.__name__} cannot be synthesized"
        )


class PythonValue(Value):
    pass


class PythonModuleValue(PythonValue):
    def __init__(self, /, **children: PythonValue):
        self.children = children

    def getattr(self, key: str):
        return self.children[key]


class ShortcutValue(Value):
    pass


class MagicVariableValue(ShortcutValue):
    def __init__(self, uuid: str, name: str) -> None:
        self.uuid = uuid
        self.name = name

    def synthesize(self):
        return super().synthesize()
