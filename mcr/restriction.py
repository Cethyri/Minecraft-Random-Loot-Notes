from enum import Enum
from mcr.mc.data_structures.condition import Condition, eCondition
from mcr.mc.data_structures.function import Function, eFunction

class eRestriction(str, Enum):
    none = 0
    type_specific = 1
    table_specific = 2
    dont_validate = -1
    other = -2

def get_restriction_level(restrictable: Condition | Function):
    match restrictable:
        case Condition():
            get_restriction_level_condition(restrictable)
        case Function():
            get_restriction_level_function(restrictable)


def get_restriction_level_condition(condition: Condition):
    restriction = eRestriction.other

    match condition.condition:

        case eCondition.location_check | eCondition.random_chance | eCondition.table_bonus:
            restriction = eRestriction.none

        case eCondition.block_state_property:
            restriction = eRestriction.table_specific

        case eCondition.damage_source_properties | eCondition.entity_properties | eCondition.killed_by_player | eCondition.match_tool | eCondition.random_chance_with_looting | eCondition.survives_explosion | eCondition.tool_enchantment:
            restriction = eRestriction.type_specific

        case eCondition.alternative | eCondition.entity_scores | eCondition.inverted:
            restriction = eRestriction.dont_validate

        case eCondition.weather_check | eCondition.reference | eCondition.entity_present:
            pass

    return restriction

def get_restriction_level_function(function: Function):
    restriction = eRestriction.other

    match function.function:

        case eFunction.copy_nbt:
            restriction = eRestriction.table_specific

        case eFunction.looting_enchant | eFunction.apply_bonus:
            restriction = eRestriction.type_specific

    return restriction
