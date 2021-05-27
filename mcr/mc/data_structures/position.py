from typing import Union

from mcr.mc.properties import JsonDict

from mcr.mc.data_structures.range import FloatRange, init_float_or_range


class Position(JsonDict, overrides={'x': init_float_or_range, 'y': init_float_or_range, 'z': init_float_or_range}):
    x: Union[FloatRange, float]
    y: Union[FloatRange, float]
    z: Union[FloatRange, float]


class Distance(JsonDict):
    absolute:	FloatRange
    horizontal:	FloatRange
    x:			FloatRange
    y:			FloatRange
    z:			FloatRange
