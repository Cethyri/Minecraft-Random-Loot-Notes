import re
from typing import Any, List

TAG = Any


class NBT(dict[str, TAG]):

    @classmethod
    def safeTagName(cls, name: str):
        if not name or '"' in name:
            #error? warn?
            pass
        return name if re.fullmatch(r"[a-zA-Z_]+[a-zA-Z_0-9]*", name) else f'"{name}"'

    def __init__(self, initialValue: dict[str, TAG]):
        super().__init__()
        for key, value in initialValue.items():
            self[NBT.safeTagName(key)] = self.handleValue(value)

    def handleValue(self, value: TAG) -> TAG:
        result = value
        if isinstance(value, dict[str, TAG]):
            result = NBT(value)
        elif isinstance(value, list[TAG]):
            newList = List[TAG]()
            for val in value:
                newList.append(self.handleValue(val))
            result = newList
        return result

    def __str__(self) -> str:
        values = ", ".join(f"{key}: {value}" for key, value in self.items())
        if values:
            values = f' {values} '
        return f"{{{values}}}"
