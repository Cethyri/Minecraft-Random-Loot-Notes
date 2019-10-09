from typing import Union, List
from enum import Enum

from mc_helper import MCDict, mc_obj, mc_list, mc_multi
from mc_range import IntRange, init_int_or_range

from location import eDimension
from entity import Entity
from item import Item

class eTrigger(str, Enum):
	bred_animals			= 'minecraft:bred_animals'
	brewed_potion			= 'minecraft:brewed_potion'
	changed_dimension		= 'minecraft:changed_dimension'
	channeled_lightning		= 'minecraft:channeled_lightning'
	construct_beacon		= 'minecraft:construct_beacon'
	consume_item			= 'minecraft:consume_item'
	cured_zombie_villager	= 'minecraft:cured_zombie_villager'
	effects_changed			= 'minecraft:effects_changed'
	enchanted_item			= 'minecraft:enchanted_item'
	enter_block				= 'minecraft:enter_block'
	entity_hurt_player		= 'minecraft:entity_hurt_player'
	entity_killed_player	= 'minecraft:entity_killed_player'
	filled_bucket			= 'minecraft:filled_bucket'
	fishing_rod_hooked		= 'minecraft:fishing_rod_hooked'
	hero_of_the_village		= 'minecraft:hero_of_the_village'
	impossible				= 'minecraft:impossible'
	inventory_changed		= 'minecraft:inventory_changed'
	item_durability_changed	= 'minecraft:item_durability_changed'
	killed_by_crossbow		= 'minecraft:killed_by_crossbow'
	levitation				= 'minecraft:levitation'
	location				= 'minecraft:location'
	nether_travel			= 'minecraft:nether_travel'
	placed_block			= 'minecraft:placed_block'
	player_hurt_entity		= 'minecraft:player_hurt_entity'
	player_killed_entity	= 'minecraft:player_killed_entity'
	recipe_unlocked			= 'minecraft:recipe_unlocked'
	shot_crossbow			= 'minecraft:shot_crossbow'
	slept_in_bed			= 'minecraft:slept_in_bed'
	summoned_entity			= 'minecraft:summoned_entity'
	tame_animal				= 'minecraft:tame_animal'
	tick					= 'minecraft:tick'
	used_ender_eye			= 'minecraft:used_ender_eye'
	used_totem				= 'minecraft:used_totem'
	villager_trade			= 'minecraft:villager_trade'
	voluntary_exile			= 'minecraft:voluntary_exile'

class TriggerConditions(MCDict):
	pass

def switch(trigger_type: eTrigger, conditions: dict) -> TriggerConditions:
	if trigger_type == eTrigger.bred_animals:
		return BredAnimals(conditions)

	elif trigger_type == eTrigger.brewed_potion:
		return BrewedPotion(conditions)

	elif trigger_type == eTrigger.changed_dimension:
		return ChangedDimension(conditions)

	elif trigger_type == eTrigger.channeled_lightning:
		return ChanneledLightning(conditions)

	elif trigger_type == eTrigger.construct_beacon:
		return ConstructBeacon(conditions)

	elif trigger_type == eTrigger.consume_item:
		return ConsumeItem(conditions)

	elif trigger_type == eTrigger.cured_zombie_villager:
		return CuredZombieVillager(conditions)

	elif trigger_type == eTrigger.effects_changed:
		return EffectsChanged(conditions)

	elif trigger_type == eTrigger.enchanted_item:
		return EnchantedItem(conditions)

	elif trigger_type == eTrigger.enter_block:
		return EnterBlock(conditions)

	elif trigger_type == eTrigger.entity_hurt_player:
		return EntityHurtPlayer(conditions)

	elif trigger_type == eTrigger.entity_killed_player:
		return EntityKilledPlayer(conditions)

	elif trigger_type == eTrigger.filled_bucket:
		return FilledBucket(conditions)

	# elif trigger_type == eTrigger.fishing_rod_hooked:
	# 	return FishingRodHooked(conditions)

	# elif trigger_type == eTrigger.hero_of_the_village:
	# 	return HeroOfTheVillage(conditions)

	elif trigger_type == eTrigger.impossible:
		return Impossible(conditions)

	elif trigger_type == eTrigger.inventory_changed:
		return InventoryChanged(conditions)

	# elif trigger_type == eTrigger.item_durability_changed:
	# 	return ItemDurabilityChanged(conditions)

	# elif trigger_type == eTrigger.killed_by_crossbow:
	# 	return KilledByCrossbow(conditions)

	# elif trigger_type == eTrigger.levitation:
	# 	return Levitation(conditions)

	# elif trigger_type == eTrigger.location:
	# 	return Location(conditions)

	# elif trigger_type == eTrigger.nether_travel:
	# 	return NetherTravel(conditions)

	# elif trigger_type == eTrigger.placed_block:
	# 	return PlacedBlock(conditions)

	# elif trigger_type == eTrigger.player_hurt_entity:
	# 	return PlayerHurtEntity(conditions)

	# elif trigger_type == eTrigger.player_killed_entity:
	# 	return PlayerKilledEntity(conditions)

	# elif trigger_type == eTrigger.recipe_unlocked:
	# 	return RecipeUnlocked(conditions)

	# elif trigger_type == eTrigger.shot_crossbow:
	# 	return ShotCrossbow(conditions)

	# elif trigger_type == eTrigger.slept_in_bed:
	# 	return SleptInBed(conditions)

	# elif trigger_type == eTrigger.summoned_entity:
	# 	return SummonedEntity(conditions)

	# elif trigger_type == eTrigger.tame_animal:
	# 	return TameAnimal(conditions)

	# elif trigger_type == eTrigger.tick:
	# 	return Tick(conditions)

	# elif trigger_type == eTrigger.used_ender_eye:
	# 	return UsedEnderEye(conditions)

	# elif trigger_type == eTrigger.used_totem:
	# 	return UsedTotem(conditions)

	# elif trigger_type == eTrigger.villager_trade:
	# 	return VillagerTrade(conditions)

	# elif trigger_type == eTrigger.voluntary_exile:
	# 	return VoluntaryExile(conditions)

	else:
		return TriggerConditions(conditions)


class BredAnimals(TriggerConditions):
	child:		dict = mc_obj('child', dict)
	parent:		dict = mc_obj('parent', dict)
	partner:	dict = mc_obj('partner', dict)

class BrewedPotion(TriggerConditions):
	potion: str = mc_obj('potion', str)

class ChangedDimension(TriggerConditions):
	frm:	eDimension = mc_obj('from', eDimension)
	to:		eDimension = mc_obj('to', eDimension)

class ChanneledLightning(TriggerConditions):
	victims: Entity = mc_list('victims', Entity)

class ConstructBeacon(TriggerConditions):
	level: Union[IntRange, int] = mc_multi('level', Union[IntRange, int], init_int_or_range)

class ConsumeItem(TriggerConditions):
	item: Item = mc_obj('item', Item)

class CuredZombieVillager(TriggerConditions):
	villager:	Entity = mc_list('villager', Entity)
	zombie:		Entity = mc_list('zombie', Entity)

class EffectsChanged(TriggerConditions):
	effects: dict = mc_obj('effect', dict)

class EnchantedItem(TriggerConditions):
	item:	Item					= mc_obj('item', Item)
	levels:	Union[IntRange, int]	= mc_multi('levels', Union[IntRange, int], init_int_or_range)

class EnterBlock(TriggerConditions):
	block: str	= mc_obj('block', str)
	state: dict	= mc_obj('state', dict)

class EntityHurtPlayer(TriggerConditions):
	damage: dict = mc_obj('damage', dict)
	
class EntityKilledPlayer(TriggerConditions):
	entity:			Entity = mc_obj('entity', Entity)
	killing_blow:	dict = mc_obj('killing_blow', dict)

class FilledBucket(TriggerConditions):
	item: Item = mc_obj('item', Item)

# class FishingRodHooked(TriggerConditions):
# class HeroOfTheVillage(TriggerConditions):

class Impossible(TriggerConditions):
	pass

class InventoryChanged(TriggerConditions):
	req_items:	List[Item]	= mc_list('items', Item)
	slots:		dict		= mc_obj('slots', dict)

# class ItemDurabilityChanged(TriggerConditions):
# class KilledByCrossbow(TriggerConditions):
# class Levitation(TriggerConditions):
# class Location(TriggerConditions):
# class NetherTravel(TriggerConditions):
# class PlacedBlock(TriggerConditions):
# class PlayerHurtEntity(TriggerConditions):
# class PlayerKilledEntity(TriggerConditions):
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

class Criteria(MCDict):
	trigger_type:	eTrigger	= mc_obj('trigger', eTrigger)
	conditions:		TriggerConditions		= mc_obj('conditions', TriggerConditions)

	@staticmethod
	def create(json_body):
		criteria = Criteria(json_body)
		if 'conditions' in json_body:
			criteria.conditions = switch(criteria.trigger_type, json_body['conditions'])
		return criteria

	@staticmethod
	def populate(trigger_type: eTrigger, conditions: TriggerConditions = None):
		criteria = Criteria()
		criteria.trigger_type = trigger_type
		if conditions is not None:
			criteria.conditions = conditions
			
		return criteria