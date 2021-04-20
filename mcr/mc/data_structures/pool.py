from typing import List, Union, Callable

from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic, mc_list
from mcr.mc.interactable import MCInteractable, MCActionInfo, eItemType, interact_with_subitems, interact_with_items

from mcr.mc.data_structures.entry import Entry
from mcr.mc.data_structures.condition import Condition
from mcr.mc.data_structures.range import IntRange, FloatRange, init_int_or_range, init_float_or_range

class Pool(MCDict, MCInteractable):
	conditions:		List[Condition]				= mc_list('conditions', Condition.create)
	rolls:			Union[IntRange, int]		= mc_basic('rolls', init_int_or_range)
	bonus_rolls:	Union[FloatRange, float]	= mc_basic('bonus_rolls', init_float_or_range)
	entries:		List[Entry]					= mc_list('entries', Entry.create)

	def interact(self, info: MCActionInfo):
		if info.item_type == eItemType.Entry and 'entries' in self:
			interact_with_items(self, 'entries', info)

		elif info.item_type == eItemType.Condition:
			if 'conditions' in self:
				interact_with_items(self, 'conditions', info)
			if 'entries' in self:
				interact_with_subitems(self.entries, info)


		