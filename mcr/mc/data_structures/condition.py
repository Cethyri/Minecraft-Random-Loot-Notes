from typing import Any
from enum import Enum

from mcr.json_dict import JsonDict, SpecialInit
from mcr.interactable import Interactable

from mcr.mc.data_structures.location import Location


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
    this = 'this'
    killer = 'killer'
    killer_player = 'killer_player'


class Condition(JsonDict, Interactable, SpecialInit):
    condition: eCondition

    @staticmethod
    def create(value: dict[str, Any]):
        condition = value['condition']
        return Condition.populate(condition, value)

    @staticmethod
    def populate(condition: eCondition, value: dict[str, Any]):
        value['condition'] = condition
        match condition:
            case eCondition.alternative:
                return Alternative(value)

            case eCondition.block_state_property:
                return BlockStateProperty(value)

            case eCondition.damage_source_properties:
                return DamageSourceProperties(value)

            case eCondition.entity_present:
                return EntityPresent(value)

            case eCondition.entity_properties:
                return EntityProperties(value)

            case eCondition.entity_scores:
                return EntityScores(value)

            case eCondition.inverted:
                return Inverted(value)

            case eCondition.killed_by_player:
                return KilledByPlayer(value)

            case eCondition.location_check:
                return LocationCheck(value)

            case eCondition.match_tool:
                return MatchTool(value)

            case eCondition.random_chance:
                return RandomChance(value)

            case eCondition.random_chance_with_looting:
                return RandomChanceWithLooting(value)

            case eCondition.reference:
                return Reference(value)

            case eCondition.survives_explosion:
                return SurvivesExplosion(value)

            case eCondition.table_bonus:
                return TableBonus(value)

            case eCondition.tool_enchantment:
                return ToolEnchantment(value)

            case eCondition.weather_check:
                return WeatherCheck(value)

            case _:
                return Condition(value)


class Alternative(Condition):
    terms: list[Condition]


class BlockStateProperty(Condition):
    block:		str
    properties:	dict


class DamageSourceProperties(Condition):
    properties: dict


class EntityPresent(Condition):
    pass


class EntityProperties(Condition):
    entity:		eEntity
    predicate:	dict


class EntityScores(Condition):
    entity: eEntity
    scores: dict


class Inverted(Condition):
    term: Condition


class KilledByPlayer(Condition):
    inverse: bool


class LocationCheck(Condition):
    predicate: Location


class MatchTool(Condition):
    predicate:	dict


class RandomChance(Condition):
    value: float


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