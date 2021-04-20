from enum import Enum
from typing import List, Callable

from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic, mc_list
from mcr.mc.interactable import MCInteractable, MCActionInfo, interact_with_subitems

from mcr.mc.data_structures.pool import Pool
from mcr.mc.data_structures.entry import Entry


class eLootTable(str, Enum):
	advancement_reward	= 'minecraft:advancement_reward'
	barter				= 'minecraft:barter'
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
		