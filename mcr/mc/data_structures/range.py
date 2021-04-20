from typing import Union

from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic

class IntRange(MCDict):
	min: int = mc_basic('min', int)
	max: int = mc_basic('max', int)

class FloatRange(MCDict):
	min: float = mc_basic('min', float)
	max: float = mc_basic('max', float)


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