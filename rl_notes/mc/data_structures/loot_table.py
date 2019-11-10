from enum import Enum
from typing import List, Callable

from rl_notes.mc.base import MCDict
from rl_notes.mc.properties import mc_basic, mc_list
from rl_notes.mc.interactable import MCInteractable, MCActionInfo, interact_with_subitems

from rl_notes.mc.data_structures.pool import Pool
from rl_notes.mc.data_structures.entry import Entry


class eLootTable(str, Enum):
	advancement_reward	= 'minecraft:advancement_reward'
	block				= 'minecraft:block'
	chest				= 'minecraft:chest'
	empty				= 'minecraft:empty'
	entity				= 'minecraft:entity'
	fishing				= 'minecraft:fishing'
	generic				= 'minecraft:generic'
	gift				= 'minecraft:gift'


class LootTable(MCDict, MCInteractable):
	typ:	eLootTable = mc_basic('type', eLootTable)
	pools:	List[Pool] = mc_list('pools', Pool)

	def interact(self, info: MCActionInfo):
		if 'pools' in self:
			interact_with_subitems(self.pools, info)
		