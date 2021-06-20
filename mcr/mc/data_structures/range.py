from typing import Union

from mcr.json_dict import JsonDict, UnionInit


class IntRange(JsonDict, UnionInit):
    min: int
    max: int

    @staticmethod
    def create(value: Union[dict[str, float], int]) -> Union['IntRange', int]:
        if isinstance(value, dict):
            return IntRange(value)
        else:
            return value


class FloatRange(JsonDict, UnionInit):
    min: float
    max: float

    @staticmethod
    def create(value: Union[dict[str, float], float]) -> Union['FloatRange', float]:
        if isinstance(value, dict):
            return FloatRange(value)
        else:
            return value
