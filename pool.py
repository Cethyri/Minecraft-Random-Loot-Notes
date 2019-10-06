from typing import List, Union
from condition import Condition

from mc_helper import MCDict, mc_obj, mc_multi, mc_multi_list

from entry import Entry


class RollRange(MCDict):
	min: int = mc_obj('min', int)
	max: int = mc_obj('max', int)

class BonusRollRange(MCDict):
	min: float = mc_obj('min', float)
	max: float = mc_obj('max', float)


def init_roll(json_body) -> Union[RollRange, int]:
	if isinstance(json_body, dict):
		return RollRange(json_body)
	else:
		return int(json_body)
		
def init_bonus_roll(json_body) -> Union[BonusRollRange, float]:
	if isinstance(json_body, dict):
		return BonusRollRange(json_body)
	else:
		return float(json_body)


class Pool(MCDict):
	conditions:		List[Condition]					= mc_multi_list('conditions', Condition, Condition.create)
	rolls:			Union[RollRange, int]			= mc_multi('rolls', Union[RollRange, int], init_roll)
	bonus_rolls:	Union[BonusRollRange, float]	= mc_multi('bonus_rolls', Union[BonusRollRange, float], init_bonus_roll)
	entries:		List[Entry]						= mc_multi_list('entries', Entry, Entry.create)