from typing import Union

from mc_helper import MCDict, mc_property
from mc_range import FloatRange, init_float_or_range

class Position(MCDict):
	x: Union[FloatRange, float] = mc_property('x', init_float_or_range)
	y: Union[FloatRange, float] = mc_property('y', init_float_or_range)
	z: Union[FloatRange, float] = mc_property('z', init_float_or_range)

class Distance(MCDict):
	absolute:	FloatRange = mc_property('absolute', FloatRange)
	horizontal:	FloatRange = mc_property('horizontal', FloatRange)
	x:			FloatRange = mc_property('x', FloatRange)
	y:			FloatRange = mc_property('y', FloatRange)
	z:			FloatRange = mc_property('z', FloatRange)