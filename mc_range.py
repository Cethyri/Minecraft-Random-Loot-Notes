from typing import Union
from mc_helper import MCDict, mc_obj

class IntRange(MCDict):
	min: int = mc_obj('min', int)
	max: int = mc_obj('max', int)

class FloatRange(MCDict):
	min: float = mc_obj('min', float)
	max: float = mc_obj('max', float)


def init_int_or_range(json_body) -> Union[IntRange, int]:
	if isinstance(json_body, dict):
		return IntRange(json_body)
	else:
		return int(json_body)

def init_float_or_range(json_body) -> Union[FloatRange, float]:
	if isinstance(json_body, dict):
		return FloatRange(json_body)
	else:
		return int(json_body)