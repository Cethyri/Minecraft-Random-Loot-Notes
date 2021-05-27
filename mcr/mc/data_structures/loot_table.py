from enum import Enum
from typing import List

from mcr.mc.properties import JsonDict
from mcr.mc.interactable import MCInteractable, MCActionInfo, interact_with_subitems

from mcr.mc.data_structures.pool import Pool


class eLootTable(str, Enum):
    advancement_reward = 'minecraft:advancement_reward'
    barter = 'minecraft:barter'
    block = 'minecraft:block'
    chest = 'minecraft:chest'
    empty = 'minecraft:empty'
    entity = 'minecraft:entity'
    fishing = 'minecraft:fishing'
    generic = 'minecraft:generic'
    gift = 'minecraft:gift'


class LootTable(JsonDict, MCInteractable):
    typ:	eLootTable
    pools:	List[Pool]

    def interact(self, info: MCActionInfo):
        if 'pools' in self:
            interact_with_subitems(self.pools, info)
