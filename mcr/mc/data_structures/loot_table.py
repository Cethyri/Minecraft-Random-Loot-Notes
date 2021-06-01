from enum import Enum

from mcr.mc.properties import JsonDict
from mcr.mc.interactable import MCInteractable

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


class LootTable(JsonDict, MCInteractable, overrides={'type_': 'type'}):
    type_:	eLootTable
    pools:	list[Pool]
