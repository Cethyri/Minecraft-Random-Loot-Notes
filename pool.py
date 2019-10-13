from typing import List, Union, Callable
from condition import Condition

from mc_helper import MCDict, mc_property, mc_list_property, MCInteractable, MCActionInfo, eItemType, interact_with_subitems, interact_with_items

from entry import Entry
from mc_range import IntRange, FloatRange, init_int_or_range, init_float_or_range

class Pool(MCDict, MCInteractable):
	conditions:		List[Condition]				= mc_list_property('conditions', Condition.create)
	rolls:			Union[IntRange, int]		= mc_property('rolls', init_int_or_range)
	bonus_rolls:	Union[FloatRange, float]	= mc_property('bonus_rolls', init_float_or_range)
	entries:		List[Entry]					= mc_list_property('entries', Entry.create)

	def interact(self, info: MCActionInfo):
		if info.item_type == eItemType.Entry and 'entries' in self:
			interact_with_items(self, 'entries', info)

		elif info.item_type == eItemType.Condition:
			if 'conditions' in self:
				interact_with_items(self, 'conditions', info)
			if 'entries' in self:
				interact_with_subitems(self.entries, info)


		