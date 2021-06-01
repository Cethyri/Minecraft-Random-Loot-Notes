from typing import Any
from enum import Enum

from mcr.mc.properties import JsonDict, SpecialInit
from mcr.mc.interactable import MCInteractable

from mcr.mc.data_structures.condition import Condition


class eFunction(str, Enum):
    apply_bonus = 'minecraft:apply_bonus'
    copy_name = 'minecraft:copy_name'
    copy_nbt = 'minecraft:copy_nbt'
    copy_state = 'minecraft:copy_state'
    enchant_randomly = 'minecraft:enchant_randomly'
    enchant_with_levels = 'minecraft:enchant_with_levels'
    exploration_map = 'minecraft:exploration_map'
    explosion_decay = 'minecraft:explosion_decay'
    furnace_smelt = 'minecraft:furnace_smelt'
    fill_player_head = 'minecraft:fill_player_head'
    limit_count = 'minecraft:limit_count'
    looting_enchant = 'minecraft:looting_enchant'
    set_attributes = 'minecraft:set_attributes'
    set_contents = 'minecraft:set_contents'
    set_count = 'minecraft:set_count'
    set_damage = 'minecraft:set_damage'
    set_lore = 'minecraft:set_lore'
    set_name = 'minecraft:set_name'
    set_nbt = 'minecraft:set_nbt'
    set_stew_effect = 'minecraft:set_stew_effect'


class Function(JsonDict, MCInteractable, SpecialInit):
    function:	eFunction
    conditions:	list[Condition]

    @staticmethod
    def create(value: dict[str, Any]):
        return Function(value)
