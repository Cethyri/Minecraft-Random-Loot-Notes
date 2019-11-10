from typing import List, Callable
from enum import Enum

from rln.mc.base import MCDict
from rln.mc.properties import mc_basic, mc_list
from rln.mc.interactable import MCInteractable, MCActionInfo, eItemType, interact_with_items, interact_with_item

from rln.mc.data_structures.location import Location

class eCondition(str, Enum):
	alternative					= 'minecraft:alternative'
	block_state_property		= 'minecraft:block_state_property'
	damage_source_properties	= 'minecraft:damage_source_properties'
	entity_present				= 'minecraft:entity_present'
	entity_properties			= 'minecraft:entity_properties'
	entity_scores				= 'minecraft:entity_scores'
	inverted					= 'minecraft:inverted'
	killed_by_player			= 'minecraft:killed_by_player'
	location_check				= 'minecraft:location_check'
	match_tool					= 'minecraft:match_tool'
	random_chance				= 'minecraft:random_chance'
	random_chance_with_looting	= 'minecraft:random_chance_with_looting'
	reference					= 'minecraft:reference'
	survives_explosion			= 'minecraft:survives_explosion'
	table_bonus					= 'minecraft:table_bonus'
	tool_enchantment			= 'minecraft:tool_enchantment'
	weather_check				= 'minecraft:weather_check'

class eEntity(str, Enum):
	this			= 'this'
	killer			= 'killer'
	killer_player	= 'killer_player'

class Condition(MCDict, MCInteractable):
	condition: eCondition = mc_basic('condition', eCondition)

	def interact(self, info: MCActionInfo):
		if info.item_type == eItemType.Condition and 'terms' in self:
			interact_with_items(self, 'terms', info)

		if info.item_type == eItemType.Condition and 'term' in self:
			interact_with_item(self, 'term', info)

	@staticmethod
	def create(json_dict):
		condition = json_dict['condition']
		if condition == eCondition.alternative:
			return Alternative(json_dict)

		elif condition == eCondition.block_state_property:
			return BlockStateProperty(json_dict)

		elif condition == eCondition.damage_source_properties:
			return DamageSourceProperties(json_dict)

		elif condition == eCondition.entity_present:
			return EntityPresent(json_dict)

		elif condition == eCondition.entity_properties:
			return EntityProperties(json_dict)

		elif condition == eCondition.entity_scores:
			return EntityScores(json_dict)

		elif condition == eCondition.inverted:
			return Inverted(json_dict)

		elif condition == eCondition.killed_by_player:
			return KilledByPlayer(json_dict)

		elif condition == eCondition.location_check:
			return LocationCheck(json_dict)

		elif condition == eCondition.match_tool:
			return MatchTool(json_dict)

		elif condition == eCondition.random_chance:
			return RandomChance(json_dict)

		elif condition == eCondition.random_chance_with_looting:
			return RandomChanceWithLooting(json_dict)

		elif condition == eCondition.reference:
			return Reference(json_dict)

		elif condition == eCondition.survives_explosion:
			return SurvivesExplosion(json_dict)

		elif condition == eCondition.table_bonus:
			return TableBonus(json_dict)

		elif condition == eCondition.tool_enchantment:
			return ToolEnchantment(json_dict)

		elif condition == eCondition.weather_check:
			return WeatherCheck(json_dict)

		else:
			return Condition(json_dict)

class Alternative(Condition):
	terms: List[Condition] = mc_list('terms', Condition.create)

class BlockStateProperty(Condition):
	block:		str		= mc_basic('block', str)
	properties:	dict	= mc_basic('properties', dict)

class DamageSourceProperties(Condition):
	properties: dict = mc_basic('properties', dict)

class EntityPresent(Condition):
	__init__ = Condition.__init__

class EntityProperties(Condition):
	entity:		eEntity	= mc_basic('entity', eEntity)
	predicate:	dict	= mc_basic('predicate', dict)

class EntityScores(Condition):
	entity: eEntity	= mc_basic('entity', eEntity)
	scores: dict	= mc_basic('scores', dict)

class Inverted(Condition):
	term: Condition = mc_basic('term', Condition.create)

class KilledByPlayer(Condition):
	inverse: bool = mc_basic('inverse', bool)

class LocationCheck(Condition):
	predicate: Location = mc_basic('predicate', Location)

class MatchTool(Condition):
	predicate:	dict	= mc_basic('predicate', dict)

class RandomChance(Condition):
	pass

class RandomChanceWithLooting(Condition):
	pass

class Reference(Condition):
	pass

class SurvivesExplosion(Condition):
	pass

class TableBonus(Condition):
	pass

class ToolEnchantment(Condition):
	pass

class WeatherCheck(Condition):
	pass


class eRestriction(str, Enum):
	none			= 0
	type_specific	= 1
	table_specific	= 2
	dont_validate	= -1
	other			= -2

def get_restriction_level(condition: Condition):
	restriction = eRestriction.other

	if condition.condition == eCondition.alternative:
		restriction = eRestriction.dont_validate

	elif condition.condition == eCondition.block_state_property:
		restriction = eRestriction.table_specific

	elif condition.condition == eCondition.damage_source_properties:
		restriction = eRestriction.type_specific

	elif condition.condition == eCondition.entity_present:
		pass

	elif condition.condition == eCondition.entity_properties:
		restriction = eRestriction.type_specific

	elif condition.condition == eCondition.entity_scores:
		restriction = eRestriction.dont_validate

	elif condition.condition == eCondition.inverted:
		restriction = eRestriction.dont_validate

	elif condition.condition == eCondition.killed_by_player:
		restriction = eRestriction.type_specific

	elif condition.condition == eCondition.location_check:
		restriction = eRestriction.none

	elif condition.condition == eCondition.match_tool:
		restriction = eRestriction.type_specific

	elif condition.condition == eCondition.random_chance:
		restriction = eRestriction.none

	elif condition.condition == eCondition.random_chance_with_looting:
		restriction = eRestriction.none

	elif condition.condition == eCondition.reference:
		pass

	elif condition.condition == eCondition.survives_explosion:
		restriction = eRestriction.type_specific

	elif condition.condition == eCondition.table_bonus:
		restriction = eRestriction.none

	elif condition.condition == eCondition.tool_enchantment:
		restriction = eRestriction.type_specific

	elif condition.condition == eCondition.weather_check:
		pass

	return restriction