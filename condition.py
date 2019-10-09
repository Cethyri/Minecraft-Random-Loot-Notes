from typing import List
from enum import Enum

from mc_helper import MCDict, mc_obj, mc_list

from location import Location


class eCondition(str, Enum):
	alternative = 'minecraft:alternative'
	block_state_property = 'minecraft:block_state_property'
	damage_source_properties = 'minecraft:damage_source_properties'
	entity_present = 'minecraft:entity_present'
	entity_properties = 'minecraft:entity_properties'
	entity_scores = 'minecraft:entity_scores'
	inverted = 'minecraft:inverted'
	killed_by_player = 'minecraft:killed_by_player'
	location_check = 'minecraft:location_check'
	match_tool = 'minecraft:match_tool'
	random_chance = 'minecraft:random_chance'
	random_chance_with_looting = 'minecraft:random_chance_with_looting'
	reference = 'minecraft:reference'
	survives_explosion = 'minecraft:survives_explosion'
	table_bonus = 'minecraft:table_bonus'
	tool_enchantment = 'minecraft:tool_enchantment'
	weather_check = 'minecraft:weather_check'

class eEntity(str, Enum):
	this = 'minecraft:this'
	killer = 'minecraft:killer'
	killer_player = 'minecraft:killer_player'


class Condition(MCDict):
	condition: eCondition = mc_obj('condition', eCondition)

	@staticmethod
	def create(json_body):
		condition = json_body['condition']
		if condition == eCondition.alternative:
			return CAlternative(json_body)
		else:
			return Condition(json_body)

class CAlternative(Condition):
	terms: List[Condition] = mc_list('terms', Condition)

class CBlockStateProperty(Condition):
	block:		str		= mc_obj('block', str)
	properties:	dict	= mc_obj('properties', dict)

class CDamageSourceProperty(Condition):
	properties: dict = mc_obj('properties', dict)

class CEntityProperties(Condition):
	entity:		eEntity	= mc_obj('entity', eEntity)
	predicate:	dict	= mc_obj('predicate', dict)

class CEntityScores(Condition):
	entity: eEntity	= mc_obj('entity', eEntity)
	scores: dict	= mc_obj('scores', dict)

class CInverted(Condition):
	term: Condition = mc_obj('term', Condition)

class CKilledByPlayer(Condition):
	inverse: bool = mc_obj('inverse', bool)

class CLocationCheck(Condition):
	predicate: Location = mc_obj('predicate', Location)