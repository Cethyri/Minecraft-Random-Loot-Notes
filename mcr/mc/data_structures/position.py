from typing import Union

from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic

from mcr.mc.data_structures.range import FloatRange, init_float_or_range

class Position(MCDict):
	x: Union[FloatRange, float] = mc_basic('x', init_float_or_range)
	y: Union[FloatRange, float] = mc_basic('y', init_float_or_range)
	z: Union[FloatRange, float] = mc_basic('z', init_float_or_range)

class Distance(MCDict):
	absolute:	FloatRange = mc_basic('absolute', FloatRange)
	horizontal:	FloatRange = mc_basic('horizontal', FloatRange)
	x:			FloatRange = mc_basic('x', FloatRange)
	y:			FloatRange = mc_basic('y', FloatRange)
	z:			FloatRange = mc_basic('z', FloatRange)