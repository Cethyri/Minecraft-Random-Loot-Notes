from typing import Union

from mcr.json_dict import JsonDict

from mcr.mc.data_structures.range import FloatRange


class Position(JsonDict):
    x: Union[float, FloatRange]
    y: Union[float, FloatRange]
    z: Union[float, FloatRange]


class Distance(JsonDict):
    absolute:	FloatRange
    horizontal:	FloatRange
    x:			FloatRange
    y:			FloatRange
    z:			FloatRange
