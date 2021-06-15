from enum import Enum

from mcr.json_dict import JsonDict
from mcr.interactable import Interactable

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


class LootTable(JsonDict, Interactable, overrides={'type_': 'type'}):
    type_:	eLootTable
    pools:	list[Pool]
