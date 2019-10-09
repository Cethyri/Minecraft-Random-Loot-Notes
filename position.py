from typing import Union

from mc_helper import MCDict, mc_obj, mc_multi
from mc_range import FloatRange, init_float_or_range

class Position(MCDict):
	x: Union[FloatRange, float] = mc_multi('x', Union[FloatRange, float], init_float_or_range)
	y: Union[FloatRange, float] = mc_multi('y', Union[FloatRange, float], init_float_or_range)
	z: Union[FloatRange, float] = mc_multi('z', Union[FloatRange, float], init_float_or_range)

class Distance(MCDict):
	absolute:	FloatRange = mc_obj('absolute', FloatRange)
	horizontal:	FloatRange = mc_obj('horizontal', FloatRange)
	x:			FloatRange = mc_obj('x', FloatRange)
	y:			FloatRange = mc_obj('y', FloatRange)
	z:			FloatRange = mc_obj('z', FloatRange)