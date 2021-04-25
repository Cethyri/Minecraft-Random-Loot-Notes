from typing import Union

from mcr.mc.base import JsonDict
from mcr.mc.properties import json_basic

from mcr.mc.data_structures.range import FloatRange, init_float_or_range

class Position(JsonDict):
	x: Union[FloatRange, float] = json_basic('x', init_float_or_range)
	y: Union[FloatRange, float] = json_basic('y', init_float_or_range)
	z: Union[FloatRange, float] = json_basic('z', init_float_or_range)

class Distance(JsonDict):
	absolute:	FloatRange = json_basic('absolute', FloatRange)
	horizontal:	FloatRange = json_basic('horizontal', FloatRange)
	x:			FloatRange = json_basic('x', FloatRange)
	y:			FloatRange = json_basic('y', FloatRange)
	z:			FloatRange = json_basic('z', FloatRange)