from typing import Union

from mc_helper import MCDict, mc_obj, mc_multi

class CoordRange(MCDict):
	min: float = mc_obj('min', float)
	max: float = mc_obj('max', float)

def init_coord(json_body) -> Union[CoordRange, float]:
	if isinstance(json_body, dict):
		return CoordRange(json_body)
	else:
		return float(json_body)

class Position(MCDict):
	x: Union[CoordRange, float] = mc_multi('x', Union[CoordRange, float], init_coord)
	y: Union[CoordRange, float] = mc_multi('y', Union[CoordRange, float], init_coord)
	z: Union[CoordRange, float] = mc_multi('z', Union[CoordRange, float], init_coord)