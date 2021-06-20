import random
from typing import Any

from loot_table_map import LootTableMap
from mcr.interactable import ActionInfo, ActionResult, eActionType
from mcr.mc.data_structures.condition import Condition, eCondition
from mcr.restriction import eRestriction, get_restriction_level


def create_variety(original_conditions: dict[eCondition, list[Condition]]):
    variety_tracker: dict[eCondition, list[int]] = {}
    for type_, conditions in original_conditions.items():
        variety_tracker[type_] = list(range(0, len(conditions)))
        random.shuffle(variety_tracker[type_])
    return variety_tracker


class ValidationInfo():
    variety_tracker: dict[eCondition, list[int]] = {}
    original_condition_count: int = 0
    validate_conditions = {}
    original_conditions: dict[eCondition, list[Condition]]


def collect(condition: Condition, _: ActionInfo[Any]):
    # TODO remove or implement commented code
    # if info.depth not in original_conditions:
    # 	original_conditions
    # if condition.condition not in valid_condition_types:
    # 	all_original_conditions.append(condition)
    if condition.condition not in ValidationInfo.original_conditions:
        ValidationInfo.original_conditions[condition.condition] = []
    ValidationInfo.original_conditions[condition.condition].append(condition)
    ValidationInfo.original_condition_count += 1
    return ActionResult.NoAction()


def validate(condition: Condition, loot_table_map: LootTableMap, condition_maps: list[dict[str, Condition]]):
    restriction_level = get_restriction_level(condition)
    restricted = True

    if restriction_level is eRestriction.none:
        restricted = False

    elif restriction_level is eRestriction.type_specific:
        restricted = not loot_table_map.remapped.type_ == loot_table_map.original.type_

    elif restriction_level is eRestriction.table_specific:
        restricted = not loot_table_map.selector == loot_table_map.remap_selector

    elif restriction_level is eRestriction.dont_validate:
        restricted = False

    condition_type = condition.condition
    condition_type_in_original = condition_type in ValidationInfo.original_conditions

    if not restricted:
        return ActionResult.NoAction()

    if condition_type_in_original:
        if condition in ValidationInfo.original_conditions[condition.condition]:
            return ActionResult.NoAction()

        for condition_map in condition_maps:
            if condition_map['original'] == condition:
                return ActionResult(condition_map['remapped'], eActionType.Set)

    if condition_type not in ValidationInfo.variety_tracker:
        condition_type = random.choice(list(ValidationInfo.variety_tracker))

    condition_index = ValidationInfo.variety_tracker[condition_type].pop()

    if len(ValidationInfo.variety_tracker[condition_type]) == 0:
        del ValidationInfo.variety_tracker[condition_type]

        # TODO: remove list() unneaded?
        if len(list(ValidationInfo.variety_tracker)) == 0:
            ValidationInfo.variety_tracker = create_variety(
                ValidationInfo.original_conditions)

    newCondition = ValidationInfo.original_conditions[condition_type][condition_index]

    condition_maps.append({
        'original': condition,
        'remapped': newCondition
    })

    return ActionResult(newCondition, eActionType.Set)


def validate_conditions(loot_table_map: LootTableMap):
    ValidationInfo.original_conditions = {}
    ValidationInfo.original_condition_count = 0

    loot_table_map.original.interact(ActionInfo(
        Condition, collect, eActionType.Get))

    ValidationInfo.variety_tracker = create_variety(
        ValidationInfo.original_conditions)
    condition_maps: list[dict[str, Condition]] = []

    if ValidationInfo.original_condition_count == 0:
        loot_table_map.remapped.interact(ActionInfo(
            Condition, lambda *_: ActionResult(True, eActionType.Del), eActionType.Del))
    else:
        loot_table_map.remapped.interact(ActionInfo(Condition, lambda condition, _: validate(
            condition, loot_table_map, condition_maps), eActionType.Set))

    # TODO: this might be breaking shit, when its type is checked in the future it'll be fucked up? or this is absolutely correct and I'm dumb, need to find out what remapped and original stand for again
    loot_table_map.remapped.type_ = loot_table_map.original.type_
