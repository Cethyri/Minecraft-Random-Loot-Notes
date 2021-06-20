from enum import Enum
from mcr.mc.data_structures.condition import Condition, eCondition

class eRestriction(str, Enum):
    none = 0
    type_specific = 1
    table_specific = 2
    dont_validate = -1
    other = -2


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
        restriction = eRestriction.type_specific

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
