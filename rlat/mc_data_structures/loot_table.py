from enum import Enum
from typing import List, Callable

from mc_helper import MCDict, mc_property, mc_list_property, MCInteractable, MCActionInfo, interact_with_subitems

from pool import Pool
from entry import Entry


class eLootTable(str, Enum):
	advancement_reward = 'minecraft:advancement_reward'
	block = 'minecraft:block'
	chest = 'minecraft:chest'
	empty = 'minecraft:empty'
	entity = 'minecraft:entity'
	fishing = 'minecraft:fishing'
	generic = 'minecraft:generic'
	gift = 'minecraft:gift'


class LootTable(MCDict, MCInteractable):
	typ:	eLootTable = mc_property('type', eLootTable)
	pools:	List[Pool] = mc_list_property('pools', Pool)

	def interact(self, info: MCActionInfo):
		if 'pools' in self:
			interact_with_subitems(self.pools, info)
		