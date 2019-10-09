from typing import List, Union
from condition import Condition

from mc_helper import MCDict, mc_obj, mc_multi, mc_multi_list

from entry import Entry
from mc_range import *

class Pool(MCDict):
	conditions:		List[Condition]					= mc_multi_list('conditions', Condition, Condition.create)
	rolls:			Union[IntRange, int]			= mc_multi('rolls', Union[IntRange, int], init_int_or_range)
	bonus_rolls:	Union[FloatRange, float]	= mc_multi('bonus_rolls', Union[FloatRange, float], init_float_or_range)
	entries:		List[Entry]						= mc_multi_list('entries', Entry, Entry.create)