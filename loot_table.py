from enum import Enum
from typing import List

from mc_helper import MCDict, mc_obj, mc_list

from pool import Pool


class eLootTable(str, Enum):
	empty = 'minecraft:empty'
	entity = 'minecraft:entity'
	block = 'minecraft:block'
	chest = 'minecraft:chest'
	fishing = 'minecraft:fishing'
	advancement_reward = 'minecraft:advancement_reward'
	generic = 'minecraft:generic'
	gift = 'minecraft:gift'


class LootTable(MCDict):
	typ:	eLootTable = mc_obj('type', eLootTable)
	pools:	List[Pool] = mc_list('pools', Pool)