from typing import List
from enum import Enum

from rl_notes.mc.base import MCDict
from rl_notes.mc.properties import mc_basic, mc_list
from rl_notes.mc.interactable import MCInteractable, MCActionInfo, eItemType, interact_with_items

from rl_notes.mc.data_structures.condition import Condition

class eFunction(str, Enum):
	apply_bonus			= 'minecraft:apply_bonus'
	copy_name			= 'minecraft:copy_name'
	copy_nbt			= 'minecraft:copy_nbt'
	enchant_randomly	= 'minecraft:enchant_randomly'
	enchant_with_levels	= 'minecraft:enchant_with_levels'
	exploration_map		= 'minecraft:exploration_map'
	explosion_decay		= 'minecraft:explosion_decay'
	furnace_smelt		= 'minecraft:furnace_smelt'
	fill_player_head	= 'minecraft:fill_player_head'
	limit_count			= 'minecraft:limit_count'
	looting_enchant		= 'minecraft:looting_enchant'
	set_attributes		= 'minecraft:set_attributes'
	set_contents		= 'minecraft:set_contents'
	set_count			= 'minecraft:set_count'
	set_damage			= 'minecraft:set_damage'
	set_lore			= 'minecraft:set_lore'
	set_name			= 'minecraft:set_name'
	set_nbt				= 'minecraft:set_nbt'
	set_stew_effect		= 'minecraft:set_stew_effect'


class Function(MCDict, MCInteractable):
	function:	eFunction		= mc_basic('function', eFunction)
	conditions:	List[Condition]	= mc_list('conditions', Condition.create)

	def interact(self, info: MCActionInfo):
		if info.item_type == eItemType.Condition and 'conditions' in self:
			interact_with_items(self, 'conditions', info)

	@staticmethod
	def create(json_dict):
		return Function(json_dict)
