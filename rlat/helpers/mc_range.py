from typing import Union

from mc_helper import MCDict, mc_property

class IntRange(MCDict):
	min: int = mc_property('min', int)
	max: int = mc_property('max', int)

class FloatRange(MCDict):
	min: float = mc_property('min', float)
	max: float = mc_property('max', float)


def init_int_or_range(json_dict) -> Union[IntRange, int]:
	if isinstance(json_dict, dict):
		return IntRange(json_dict)
	else:
		return int(json_dict)

def init_float_or_range(json_dict) -> Union[FloatRange, float]:
	if isinstance(json_dict, dict):
		return FloatRange(json_dict)
	else:
		return int(json_dict)