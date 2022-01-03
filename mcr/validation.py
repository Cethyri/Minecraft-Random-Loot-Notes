from dataclasses import dataclass
import random
from typing import Any

from mcr.randomizer_template import RandomizerTemplate
from mcr.interactable import ActionInfo, ActionResult, eActionType
from mcr.mc.data_structures.condition import Condition, eCondition
from mcr.mc.data_structures.function import Function, eFunction
from mcr.restriction import eRestriction, get_restriction_level


interactable_union = Condition | Function
interactable_type_union = eCondition | eFunction


def get_interactable_type(interactable: interactable_union):
    match interactable:
        case Condition():
            interactable_type = interactable.condition
        case Function():
            interactable_type = interactable.function
    return interactable_type

def create_variety(original_conditions: dict[interactable_type_union, list[interactable_union]]):
    variety_tracker: dict[interactable_type_union, list[int]] = {}
    for type_, conditions in original_conditions.items():
        variety_tracker[type_] = list(range(0, len(conditions)))
        random.shuffle(variety_tracker[type_])
    return variety_tracker

class InteractableValidationInfo():
    variety_tracker: dict[interactable_type_union, list[int]]
    original_interactable_count: int
    original_interactables: dict[interactable_type_union, list[interactable_union]]

    def get_collection_delegate(self):

        def collect(interactable: interactable_union, _: ActionInfo[Any]):
            # TODO remove or implement commented code
            # if info.depth not in original_conditions:
            # 	original_conditions
            # if condition.condition not in valid_condition_types:
            # 	all_original_conditions.append(condition)
            interactable_type: interactable_type_union

            interactable_type = get_interactable_type(interactable)

            if interactable_type not in self.original_interactables:
                self.original_interactables[interactable_type] = []
            self.original_interactables[interactable_type].append(
                interactable)
            self.original_interactable_count += 1
            return ActionResult.NoAction()

        return collect

@dataclass
class InteractableMap():
    original: interactable_union
    target: interactable_union





def confirm_delete(*_: Any):
    return ActionResult(True, eActionType.Del)


def get_validation_delegate(validation_info: InteractableValidationInfo, loot_table_map: RandomizerTemplate, condition_maps: list[InteractableMap]):

    def validate_condition(condition: Condition, _: Any):
        return validate(validation_info, condition, loot_table_map, condition_maps)

    return validate_condition


def validate_conditions(loot_table_map: RandomizerTemplate):
    for type in [Condition, Function]:
        validation_info: InteractableValidationInfo = InteractableValidationInfo()
        validation_info.original_interactables = {}
        validation_info.original_interactable_count = 0

        loot_table_map.original.interact(
            ActionInfo(type, validation_info.get_collection_delegate(), eActionType.Get))

        validation_info.variety_tracker = create_variety(
            validation_info.original_interactables)

        interactable_maps: list[InteractableMap] = []
        
        # TODO implement a default replacement for certain condition and function types.
        # default_condition = Condition.populate(eCondition.random_chance, {'value': 0.5})
        # default_function = Function.populate(eFunction.set_count, {'value': 1})

        if validation_info.original_interactable_count == 0:
            loot_table_map.target.interact(ActionInfo(
                type, confirm_delete, eActionType.Del))
            # match type:
            #     case Condition():
            #         validation_info.original_interactables[default_condition] # type: ignore
            #     case Function():
            #         validation_info.original_interactables[default_function] # type: ignore

        else:


            loot_table_map.target.interact(ActionInfo(type, get_validation_delegate(
                validation_info, loot_table_map, interactable_maps), eActionType.Set))

        # since we're basing the new loot table on the target table, the target type needs to be set to the original type or the minecraft environment will create issues.
        loot_table_map.target.type_ = loot_table_map.original.type_


def validate(validation_info: InteractableValidationInfo, interactable: interactable_union, loot_table_map: RandomizerTemplate, maps: list[InteractableMap]):
    restriction_level = get_restriction_level(interactable)
    restricted = True

    if restriction_level is eRestriction.none:
        restricted = False

    elif restriction_level is eRestriction.type_specific:
        restricted = not loot_table_map.target.type_ == loot_table_map.original.type_

    elif restriction_level is eRestriction.table_specific:
        restricted = not loot_table_map.name == loot_table_map.target_name

    elif restriction_level is eRestriction.dont_validate:
        restricted = False

    interactable_type = get_interactable_type(interactable)
    interactable_type_in_original = interactable_type in validation_info.original_interactables

    if not restricted:
        return ActionResult.NoAction()

    if interactable_type_in_original:
        if interactable in validation_info.original_interactables[interactable_type]:
            return ActionResult.NoAction()

        for map in maps:
            if map.original == interactable:
                return ActionResult(map.target, eActionType.Set)

    if interactable_type not in validation_info.variety_tracker:
        interactable_type = random.choice(list(validation_info.variety_tracker))

    condition_index = validation_info.variety_tracker[interactable_type].pop()

    if len(validation_info.variety_tracker[interactable_type]) == 0:
        del validation_info.variety_tracker[interactable_type]

        if len(validation_info.variety_tracker) == 0:
            validation_info.variety_tracker = create_variety(
                validation_info.original_interactables)

    newInteractable = validation_info.original_interactables[interactable_type][condition_index]

    maps.append(InteractableMap(interactable, newInteractable))

    return ActionResult(newInteractable, eActionType.Set)
