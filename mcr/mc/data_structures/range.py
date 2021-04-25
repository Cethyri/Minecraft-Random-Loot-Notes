from typing import Union

from mcr.mc.base import JsonDict
from mcr.mc.properties import json_basic

class IntRange(JsonDict):
	min: int = json_basic('min', int)
	max: int = json_basic('max', int)

class FloatRange(JsonDict):
	min: float = json_basic('min', float)
	max: float = json_basic('max', float)


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