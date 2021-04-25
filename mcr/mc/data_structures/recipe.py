from enum import Enum
from typing import List, Callable, Dict, Union

from mcr.mc.base import JsonDict
from mcr.mc.properties import json_basic, json_list, json_dict


class eRecipe(str, Enum):
	blasting							= 'minecraft:blasting'
	campfire_cooking					= 'minecraft:campfire_cooking'
	smelting							= 'minecraft:smelting'
	smoking 							= 'minecraft:smoking'
	stonecutting						= 'minecraft:stonecutting'
	crafting_shaped						= 'minecraft:crafting_shaped'
	crafting_shapeless					= 'minecraft:crafting_shapeless'
	crafting_special_armordye			= 'minecraft:crafting_special_armordye'
	crafting_special_bannerduplicate	= 'minecraft:crafting_special_bannerduplicate'
	crafting_special_bookcloning		= 'minecraft:crafting_special_bookcloning'
	crafting_special_firework_rocket	= 'minecraft:crafting_special_firework_rocket'
	crafting_special_firework_star		= 'minecraft:crafting_special_firework_star'
	crafting_special_firework_star_fade	= 'minecraft:crafting_special_firework_star_fade'
	crafting_special_mapcloning			= 'minecraft:crafting_special_mapcloning'
	crafting_special_mapextending		= 'minecraft:crafting_special_mapextending'
	crafting_special_repairitem			= 'minecraft:crafting_special_repairitem'
	crafting_special_shielddecoration	= 'minecraft:crafting_special_shielddecoration'
	crafting_special_shulkerboxcoloring	= 'minecraft:crafting_special_shulkerboxcoloring'
	crafting_special_tippedarrow		= 'minecraft:crafting_special_tippedarrow'
	crafting_special_suspiciousstew		= 'minecraft:crafting_special_suspiciousstew'

class Result(JsonDict):
	count:	int	= json_basic('count', int)
	item:	str	= json_basic('item', str)

class Ingredient(JsonDict):
	item:	str = json_basic('item', str)
	tag:	str = json_basic('tag', str)

def init_ingredient_or_list(json_dict: Union[dict, List[dict]]):
	if isinstance(json_dict, dict):
		return Ingredient(json_dict)
	elif isinstance(json_dict, list):
		ingredient_list = []
		for ingredient in json_dict:
			ingredient_list.append(Ingredient(ingredient))
		return ingredient_list


class Recipe(JsonDict):
	typ: 	eRecipe	= json_basic('type', eRecipe)
	group: 	str		= json_basic('group', str)

class CraftingShaped(Recipe):
	pattern:	List[str]										= json_list('pattern', str)
	key:		Dict[str, Union[Ingredient, List[Ingredient]]]	= json_dict('key', init_ingredient_or_list)
	result:		Result											= json_basic('result', Result)