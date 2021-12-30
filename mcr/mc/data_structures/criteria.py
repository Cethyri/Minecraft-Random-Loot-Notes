from typing import Any, Union
from enum import Enum

from mcr.json_dict import JsonDict, SpecialInit
from mcr.mc.data_structures.range import IntRange

from mcr.mc.data_structures.location import eDimension
from mcr.mc.data_structures.entity import Entity
from mcr.mc.data_structures.item import Item


class eTrigger(str, Enum):
    bred_animals = 'minecraft:bred_animals'
    brewed_potion = 'minecraft:brewed_potion'
    changed_dimension = 'minecraft:changed_dimension'
    channeled_lightning = 'minecraft:channeled_lightning'
    construct_beacon = 'minecraft:construct_beacon'
    consume_item = 'minecraft:consume_item'
    cured_zombie_villager = 'minecraft:cured_zombie_villager'
    effects_changed = 'minecraft:effects_changed'
    enchanted_item = 'minecraft:enchanted_item'
    enter_block = 'minecraft:enter_block'
    entity_hurt_player = 'minecraft:entity_hurt_player'
    entity_killed_player = 'minecraft:entity_killed_player'
    filled_bucket = 'minecraft:filled_bucket'
    fishing_rod_hooked = 'minecraft:fishing_rod_hooked'
    hero_of_the_village = 'minecraft:hero_of_the_village'
    impossible = 'minecraft:impossible'
    inventory_changed = 'minecraft:inventory_changed'
    item_durability_changed = 'minecraft:item_durability_changed'
    killed_by_crossbow = 'minecraft:killed_by_crossbow'
    levitation = 'minecraft:levitation'
    location = 'minecraft:location'
    nether_travel = 'minecraft:nether_travel'
    placed_block = 'minecraft:placed_block'
    player_hurt_entity = 'minecraft:player_hurt_entity'
    player_killed_entity = 'minecraft:player_killed_entity'
    recipe_unlocked = 'minecraft:recipe_unlocked'
    shot_crossbow = 'minecraft:shot_crossbow'
    slept_in_bed = 'minecraft:slept_in_bed'
    summoned_entity = 'minecraft:summoned_entity'
    tame_animal = 'minecraft:tame_animal'
    tick = 'minecraft:tick'
    used_ender_eye = 'minecraft:used_ender_eye'
    used_totem = 'minecraft:used_totem'
    villager_trade = 'minecraft:villager_trade'
    voluntary_exile = 'minecraft:voluntary_exile'


class TriggerConditions(JsonDict):
    pass


def switch(trigger: eTrigger, conditions: dict[str, Any]) -> TriggerConditions:
    match trigger:
        case eTrigger.bred_animals:
            return BredAnimals(conditions)

        case eTrigger.brewed_potion:
            return BrewedPotion(conditions)

        case eTrigger.changed_dimension:
            return ChangedDimension(conditions)

        case eTrigger.channeled_lightning:
            return ChanneledLightning(conditions)

        case eTrigger.construct_beacon:
            return ConstructBeacon(conditions)

        case eTrigger.consume_item:
            return ConsumeItem(conditions)

        case eTrigger.cured_zombie_villager:
            return CuredZombieVillager(conditions)

        case eTrigger.effects_changed:
            return EffectsChanged(conditions)

        case eTrigger.enchanted_item:
            return EnchantedItem(conditions)

        case eTrigger.enter_block:
            return EnterBlock(conditions)

        case eTrigger.entity_hurt_player:
            return EntityHurtPlayer(conditions)

        case eTrigger.entity_killed_player:
            return EntityKilledPlayer(conditions)

        case eTrigger.filled_bucket:
            return FilledBucket(conditions)

        # case eTrigger.fishing_rod_hooked:
        # 	return FishingRodHooked(conditions)

        # case eTrigger.hero_of_the_village:
        # 	return HeroOfTheVillage(conditions)

        case eTrigger.impossible:
            return Impossible(conditions)

        case eTrigger.inventory_changed:
            return InventoryChanged(conditions)

        # case eTrigger.item_durability_changed:
        # 	return ItemDurabilityChanged(conditions)

        # case eTrigger.killed_by_crossbow:
        # 	return KilledByCrossbow(conditions)

        # case eTrigger.levitation:
        # 	return Levitation(conditions)

        # case eTrigger.location:
        # 	return Location(conditions)

        # case eTrigger.nether_travel:
        # 	return NetherTravel(conditions)

        # case eTrigger.placed_block:
        # 	return PlacedBlock(conditions)

        # case eTrigger.player_hurt_entity:
        # 	return PlayerHurtEntity(conditions)

        # case eTrigger.player_killed_entity:
        # 	return PlayerKilledEntity(conditions)

        # case eTrigger.recipe_unlocked:
        # 	return RecipeUnlocked(conditions)

        # case eTrigger.shot_crossbow:
        # 	return ShotCrossbow(conditions)

        # case eTrigger.slept_in_bed:
        # 	return SleptInBed(conditions)

        # case eTrigger.summoned_entity:
        # 	return SummonedEntity(conditions)

        # case eTrigger.tame_animal:
        # 	return TameAnimal(conditions)

        # case eTrigger.tick:
        # 	return Tick(conditions)

        # case eTrigger.used_ender_eye:
        # 	return UsedEnderEye(conditions)

        # case eTrigger.used_totem:
        # 	return UsedTotem(conditions)

        # case eTrigger.villager_trade:
        # 	return VillagerTrade(conditions)

        # case eTrigger.voluntary_exile:
        # 	return VoluntaryExile(conditions)

        case _:
            return TriggerConditions(conditions)


class BredAnimals(TriggerConditions):
    child:		Entity
    parent:		Entity
    partner:	Entity


class BrewedPotion(TriggerConditions):
    potion: str


class ChangedDimension(TriggerConditions, overrides={'from_': 'from'}):
    from_:	eDimension
    to:		eDimension


class ChanneledLightning(TriggerConditions):
    victims: Entity


class ConstructBeacon(TriggerConditions):
    level: Union[int, IntRange]


class ConsumeItem(TriggerConditions):
    item: Item


class CuredZombieVillager(TriggerConditions):
    villager:	Entity
    zombie:		Entity


class EffectsChanged(TriggerConditions):
    effects: dict


class EnchantedItem(TriggerConditions):
    item:	Item
    levels:	Union[IntRange, int]


class EnterBlock(TriggerConditions):
    block: str
    state: dict


class EntityHurtPlayer(TriggerConditions):
    damage: dict


class EntityKilledPlayer(TriggerConditions):
    entity:			Entity
    killing_blow:	dict


class FilledBucket(TriggerConditions):
    item: Item


class FishingRodHooked(TriggerConditions):
    entity:	Entity
    item:	Item
    rod:	Item


class HeroOfTheVillage(TriggerConditions):
    pass


class Impossible(TriggerConditions):
    pass


class InventoryChanged(TriggerConditions):
    req_items:	list[Item]
    slots:		dict

# class ItemDurabilityChanged(TriggerConditions):
# class KilledByCrossbow(TriggerConditions):
# class Levitation(TriggerConditions):
# class Location(TriggerConditions):
# class NetherTravel(TriggerConditions):
# class PlacedBlock(TriggerConditions):
# class PlayerHurtEntity(TriggerConditions):


class PlayerKilledEntity(TriggerConditions):
    entity:			Entity
    killing_blow:	dict

# class RecipeUnlocked(TriggerConditions):
# class ShotCrossbow(TriggerConditions):
# class SleptInBed(TriggerConditions):
# class SummonedEntity(TriggerConditions):
# class TameAnimal(TriggerConditions):
# class Tick(TriggerConditions):
# class UsedEnderEye(TriggerConditions):
# class UsedTotem(TriggerConditions):
# class VillagerTrade(TriggerConditions):
# class VoluntaryExile(TriggerConditions):


class Criteria(JsonDict, SpecialInit):
    trigger:	eTrigger
    conditions:		TriggerConditions

    @staticmethod
    def create(value: dict[str, Any]):
        trigger = value['trigger']
        condition = value['condition'] if 'condition' in value else None
        return Criteria.populate(trigger, condition)

    @staticmethod
    def populate(trigger: eTrigger, conditions: TriggerConditions | dict[str, Any] | None = None):
        criteria = Criteria()
        criteria.trigger = trigger
        match conditions:
            case TriggerConditions():
                criteria.conditions = conditions
            case dict():
                criteria.conditions = switch(trigger, conditions)
        return criteria
