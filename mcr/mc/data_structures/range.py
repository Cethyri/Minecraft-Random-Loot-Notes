from typing import Union

from mcr.mc.properties import JsonDict, SpecialInit


class IntRange(JsonDict):
    min: int
    max: int

    # @staticmethod
    # def create(value: Union[dict, int]) -> Union['IntRange', int]:
    #     if isinstance(value, dict):
    #         return IntRange(value)
    #     else:
    #         return int(value)


class FloatRange(JsonDict):
    min: float
    max: float


def init_int_or_range(value: Union[dict, int]) -> Union[IntRange, int]:
    if isinstance(value, dict):
        return IntRange(value)
    else:
        return int(value)


def init_float_or_range(value: Union[dict, float]) -> Union[FloatRange, float]:
    if isinstance(value, dict):
        return FloatRange(value)
    else:
        return int(value)
