import os
import random
import io
import zipfile
import json
import sys
import math

from enum import Enum
from typing import Dict, List, Callable

from loot_table_map import LootTableMap, populate_advancement_chain, AdvItem, eAdvItemType, validate_conditions
from loot_table import LootTable, eLootTable
from advancement import Advancement, Rewards
from condition import Condition, eCondition, eRestriction, get_restriction_level
from display import Display, Icon, TextComponent
from criteria import Criteria, eTrigger, InventoryChanged, Impossible, PlayerKilledEntity, EntityKilledPlayer, FishingRodHooked
from item import Item
from entity import Entity

from re_helper import fix_a_an, get_upper_selector, shorten_selector
from mc_helper import MCActionInfo, eItemType, eActionType

requires_cheats = [
	'giant',
	'illusioner'
]

flags = {
	'hardcore': False,
	'no-cheats': False,
	'no-dead-ends': False,
	#'fill-dead-ends': False,
	#'hints': False,
	#'loot-hints': False,
	#'empty-loot-hints': False,
	'save-seed': False,
	'hide-seed': False
}

if len(sys.argv) > 1:
	argstart = 1
	seed_given = False
	if not sys.argv[1].startswith('--'):
		argstart = 2
		try:
			seed = int(sys.argv[1])
			seed_given = True
		except Exception:
			print('The seed "{}" is not an integer.'.format(sys.argv[1]))
			exit()

	for i in range(argstart, len(sys.argv)):
		arg = sys.argv[i].replace('--', '', 1)
		if arg in flags:
			flags[arg] = True
		else:
			print('{} is not a recognized flag, ignoring...'.format(arg))

if seed_given:	
	random.seed(seed)
	datapack_name = 'rand_loot_adv_tree_{}'.format(seed)
	datapack_desc = 'Loot Table Randomizer Advancement Tree, Seed: {}'.format(seed)
else:
	if not seed_given:
		seed = random.randint(-sys.maxsize, sys.maxsize)
		if not flags['save-seed']:
			print('If you want to use a specific randomizer seed integer, use: "python randomize.py <seed>".')

	if (seed_given and not flags['hide-seed']) or (flags['save-seed'] and not seed_given):
		datapack_name = 'rand_loot_adv_tree_{}'.format(seed)
		datapack_desc = 'Loot Table Randomizer Advancement Tree, Seed: {}'.format(seed)
	else:
		datapack_name = 'rand_loot_adv_tree'
		datapack_desc = 'Loot Table Randomizer Advancement Tree'

if all(not flags[key] for key in flags):
	print('Customization is available through flags. If you would like to see a list of flags use: "python rlat_help.py')
	
datapack_filename = datapack_name + '.zip'


print(flags)


print('Generating datapack...')

loot_table_maps: Dict[str, LootTableMap] = {}
remaining_selectors: List[str] = []


update_pre_randomized = os.path.exists('randomized')
if update_pre_randomized:
	datapack_name = '{}_upd'.format(datapack_name)
	datapack_desc = '{}_upd'.format(datapack_desc)
	datapack_filename = datapack_name + '.zip'

selectors_to_remapped = {}
original_to_selector = {}


print('Loading Tables...')

def load_table_info():
	if update_pre_randomized:
		for dirpath, _dirnames, filenames in os.walk('randomized'):
			for filename in filenames:
				selector = filename.replace('.json', '')

				with open(os.path.join(dirpath, filename)) as json_file:
					selectors_to_remapped[selector] = json_file.read().replace('\n', '')

	for dirpath, _dirnames, filenames in os.walk('loot_tables'):
		for filename in filenames:
			selector = filename.replace('.json', '')
			path = dirpath.replace('loot_tables\\', '').split('\\')

			if update_pre_randomized and selector not in selectors_to_remapped:
				continue

			if selector == 'player' and flags['hardcore']:
				continue

			if selector in requires_cheats and flags['no-cheats']:
				continue

			with open(os.path.join(dirpath, filename)) as json_file:
				json_text = json_file.read().replace('\n', '')
				original_to_selector[json_text] = selector
				json_dict = json.loads(json_text)
				loot_table = LootTable(json_dict)

			if ('pools' not in loot_table or len(loot_table.pools) == 0) and flags['no-dead-ends']:
				continue

			loot_table_maps[selector] = LootTableMap(selector, path, loot_table)
			remaining_selectors.append(selector)
load_table_info()


if update_pre_randomized:
	print('Maping pre-randomized tables...')
else:
	print('Randomizing drops...')

def is_killed_by_player(condition: Condition, info: MCActionInfo):
	return condition.condition == eCondition.killed_by_player

#For Randomization to match Sethbling's the python version must be 3.6+ (For ordered dictionaries)
def randomize():
	if update_pre_randomized:
		outdated = {}

		for selector in loot_table_maps:
			remapped_json = selectors_to_remapped[selector]

			if remapped_json not in original_to_selector:
				print('checking if {} remapped is outdated version of a current loot_table'.format(selector))
				for ood_remapped_selector in loot_table_maps:
					if ood_remapped_selector not in outdated:
						original_table = loot_table_maps[ood_remapped_selector].original

						outdated[ood_remapped_selector] = {
							'new_table': LootTable(json.loads(json.dumps(original_table))), #Deep Copy
							'out_of_date_table': LootTable(json.loads(remapped_json))
						}
						
						outdated[ood_remapped_selector]['new_table'].interact(MCActionInfo(eItemType.Condition, is_killed_by_player, eActionType.Delete))

					if outdated[ood_remapped_selector]['out_of_date_table'] == outdated[ood_remapped_selector]['new_table']:
						remapped_selector = ood_remapped_selector
						remapped_table = original_table
						break
			else:
				remapped_selector = original_to_selector[remapped_json]
				remapped_table = loot_table_maps[remapped_selector].original

			if remapped_selector and remapped_table:
				loot_table_maps[selector].remap_selector = remapped_selector
				loot_table_maps[selector].remapped = LootTable(json.loads(json.dumps(remapped_table))) #Deep Copy
			else:
				print('failed to find matching table for {}'.format(selector))

	else:
		for selector in loot_table_maps:
			i = random.randrange(0, len(remaining_selectors))
			remapped_table = loot_table_maps[remaining_selectors[i]].original
			loot_table_maps[selector].remap_selector = remaining_selectors[i]
			loot_table_maps[selector].remapped = LootTable(json.loads(json.dumps(remapped_table))) #Deep Copy
			del remaining_selectors[i]
randomize()


print('Validating loot tables...')

conditions = {
	eRestriction.none: [],
	eRestriction.type_specific: [],
	eRestriction.table_specific: [],
	eRestriction.dont_validate: [],
	eRestriction.other: []
}

def collect_conditions(condition: Condition, info: MCActionInfo):
	restriction = get_restriction_level(condition)

	if condition not in conditions[restriction]:
		conditions[restriction].append(condition)

def validate():
	for selector in loot_table_maps:
		# print('Validating: {}'.format(selector))
		loot_table_maps[selector].remapped.interact(MCActionInfo(eItemType.Condition, collect_conditions, eActionType.Interact))
		validate_conditions(loot_table_maps[selector], conditions)
validate()
		

print('Populating Advancement chains...')

def populate():
	for selector in loot_table_maps:
		# print('Populating chain for: {}'.format(selector))
		populate_advancement_chain(selector, loot_table_maps)
		for adv_item in loot_table_maps[selector].adv_chain:
			if adv_item.selector != selector:
				loot_table_maps[adv_item.selector].is_sub = not loot_table_maps[adv_item.selector].is_loop
populate()


print('Generating Advancements...')

with open('double_tall_blocks.json') as json_file:
	double_tall_blocks = json.load(json_file)
		
tabs_possible_images: Dict[str, List[str]] = {}
tabs: List[str] = []
advancements: Dict[str, Advancement] = {}

objective_num = 0
functions: Dict[str, List[str]] = {}

reset_function_list = [
	'tellraw @a ["",{"text":"Loot table randomizer with advancement tree by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]',
	'scoreboard objectives add incomplete dummy',
	'scoreboard objectives add complete dummy',
	'scoreboard objectives add ref_complete dummy'
]
remove_function_list = []
tick_function_list = []

def get_namespaced_selector(pathed_selector: str, additional: str = None):
	return '{}:{}{}'.format(datapack_name, pathed_selector, additional if additional is not None else '')

def sheep_color_to_number(color: str):
	if color == 'white':
		return 0
	if color == 'orange':
		return 1
	if color == 'magenta':
		return 2
	if color == 'light_blue':
		return 3
	if color == 'yellow':
		return 4
	if color == 'lime':
		return 5
	if color == 'pink':
		return 6
	if color == 'gray':
		return 7
	if color == 'light_gray':
		return 8
	if color == 'cyan':
		return 9
	if color == 'purple':
		return 10
	if color == 'blue':
		return 11
	if color == 'brown':
		return 12
	if color == 'green':
		return 13
	if color == 'red':
		return 14
	if color == 'black':
		return 15
	else:
		print('SHEEP COLOR BROKEN! {}'.format(color))

def get_pathed_selector(selector: str, path: str, base: str, link_index: int):
	name = '{}-{}'.format(link_index, selector) if link_index >= 0 else selector
	return os.path.join(path, base, name).replace('\\', '/')

def generate_children_functions(pathed_selector: str, start_link: AdvItem, path: str, base: str, child_index: int, execute_conditions_list: List[Callable]):
	
	functions[pathed_selector].append('scoreboard players set @s incomplete 0')
	functions[pathed_selector].append('scoreboard players set @s complete 0')
			
	references = []
	search_queue = [start_link]
	reference_namespaced_selectors = {}

	cur_link = AdvItem
	current_map: LootTableMap
	
	is_reference = False

	while len(search_queue) > 0:
		cur_link = search_queue.pop()
		current_map = loot_table_maps[cur_link.selector]

		if is_reference:
			functions[pathed_selector].append('scoreboard players set @s ref_complete 0')

		references.append(current_map.selector)
		if start_link.selector == 'buried_treasure':
			pass

		branches = []
		if cur_link.selector in current_map.adv_branches:
			branches.extend(current_map.adv_branches[cur_link.selector])
		if len(current_map.adv_chain) > 1 and current_map.adv_chain[1].adv_item_type is not eAdvItemType.from_items:
			branches.append(current_map.adv_chain[1])

		for adv_child in branches:
			child_pathed_selector = get_pathed_selector(adv_child.selector, path, base, 1 if is_reference else child_index)

			if adv_child.adv_item_type is not eAdvItemType.item and adv_child.adv_item_type is not eAdvItemType.reference and adv_child.adv_item_type is not eAdvItemType.block and adv_child.adv_item_type is not eAdvItemType.loop:
				print('Warning: unknown child advancement type... {}'.format(adv_child.selector))
				print('Parent Selector: {}'.format(current_map.selector))

			namespaced_selector = get_namespaced_selector(child_pathed_selector)
			if adv_child.adv_item_type is not eAdvItemType.reference and adv_child.selector == adv_child.item_selector:
				for execute_conditions in execute_conditions_list:
					functions[pathed_selector].append('execute {} run advancement grant @s only {}'.format(execute_conditions(adv_child), namespaced_selector))
				functions[pathed_selector].append('scoreboard players add @s[advancements = {{ {} = true }}] complete 1'.format(namespaced_selector))
				functions[pathed_selector].append('scoreboard players add @s[advancements = {{ {} = false }}] incomplete 1'.format(namespaced_selector))
				
				if is_reference:
					functions[pathed_selector].append('scoreboard players add @s[advancements = {{ {} = true }}] ref_complete 1'.format(namespaced_selector))

			elif adv_child.adv_item_type is eAdvItemType.reference and adv_child.selector not in references:
				search_queue.append(adv_child)
				reference_namespaced_selectors[adv_child.selector] = namespaced_selector

		if is_reference:
			root_namespaced_selector = get_namespaced_selector(get_pathed_selector(cur_link.selector, path, base, 0))
			functions[pathed_selector].append('advancement grant @s[scores = {{ ref_complete = 1.. }}] only {}'.format(reference_namespaced_selectors[cur_link.selector]))
			functions[pathed_selector].append('advancement grant @s[scores = {{ ref_complete = 1.. }}] only {}'.format(root_namespaced_selector))
		else:
			is_reference = True

def generate_conditions(pathed_selector: str, adv_link: AdvItem, path: str, base: str, link_index: int):
	global objective_num

	if pathed_selector in functions:
		print('Warning: duplicate function!')

	loot_table_map = loot_table_maps[adv_link.selector]

	helper_selector = "helper/{}".format(pathed_selector)
	namespaced_helper = get_namespaced_selector(helper_selector)
	namespaced_selector = get_namespaced_selector(pathed_selector)
	
	functions[pathed_selector] = []

	objective_name = '{}_r{}'.format(shorten_selector(adv_link.selector), objective_num)
	if len(objective_name) > 16:
		print(objective_name)
	objective_num += 1
	objective_criteria = 'dummy'
	use_helper = False
	reset_objective = False
	execute_conditions_list = []
	grant_target_selector = '[scores = { incomplete = 0 }]'
	child_index = link_index + 1

	if adv_link.selector == 'sheep' or 'fishing' in loot_table_map.path:
		return
	
	elif adv_link.selector == 'armor_stand':
		tick_function_list.append('execute as @a[scores = {{ {} = 0.. }}] at @s at @e[distance = ..8, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item: {{ id:"minecraft:armor_stand" }}}}] run function {}'.format(objective_name, namespaced_selector))

		execute_conditions_list = [
			lambda adv_child: 'if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_child.item_selector)
		]

		grant_target_selector = ''
		
	elif adv_link.selector in double_tall_blocks:
		for i in range(10):
			score = i + 1
			distance = score / 2
			tick_function_list.append('execute as @a[scores = {{ {0} = 0 }}] at @s anchored eyes if block ^ ^ ^{1} minecraft:{2} run scoreboard players set @s {0} {3}'.format(objective_name, distance, adv_link.selector, score))
			tick_function_list.append('execute as @a[scores = {{ {0} = {3} }}] at @s anchored eyes unless block ^ ^ ^{1} minecraft:{2} positioned ^ ^ ^{1} run function {4}'.format(objective_name, distance, adv_link.selector, score, namespaced_selector))
			
		execute_conditions_list = [
			lambda adv_child: 'unless block ~ ~ ~ minecraft:{} if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_link.selector, adv_child.item_selector)
		]
		
		reset_objective = True
		grant_target_selector = ''

	elif loot_table_map.original.typ is eLootTable.block:
		objective_criteria = 'minecraft.mined:minecraft.{}'.format(adv_link.selector)

		tick_function_list.append('execute as @a[scores = {{ {} = 1.. }}] at @s run function {}'.format(objective_name, namespaced_selector))

		execute_conditions_list = [
			lambda adv_child: 'if entity @e[distance = ..8, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_child.item_selector)
		]

		reset_objective = True
		grant_target_selector = ''
		
	elif loot_table_map.original.typ is eLootTable.chest:
		loot_table_pathed_selector = get_pathed_selector(adv_link.selector, path, '', -1)

		for i in range(10):
			score = i + 1
			distance = score / 2
			tick_function_list.append('execute as @a[scores = {{ {0} = 0 }}] at @s anchored eyes if block ^ ^ ^{1} minecraft:chest{{ LootTable: "minecraft:{2}" }} run scoreboard players set @s {0} {3}'.format(objective_name, distance, loot_table_pathed_selector, score))
			tick_function_list.append('execute as @a[scores = {{ {0} = {3} }}] at @s anchored eyes unless block ^ ^ ^{1} minecraft:chest{{ LootTable: "minecraft:{2}" }} positioned ^ ^ ^{1} run function {4}'.format(objective_name, distance, loot_table_pathed_selector, score, namespaced_selector))
			
		execute_conditions_list = [
			lambda adv_child: 'if block ~ ~ ~ minecraft:chest{{ Items: [{{ id: "minecraft:{}" }}] }}'.format(adv_child.item_selector)
		]
		
		reset_objective = True

	elif loot_table_map.original.typ is eLootTable.gift and 'hero_of_the_village' in loot_table_map.path:
		villager_type = adv_link.selector.replace('_gift', '')

		tick_function_list.append('execute as @a[scores = {{ {} = 0.. }}, nbt = {{ ActiveEffects: [{{ Id: 32b }}] }}] at @s at @e[distance = ..8, type = minecraft:villager, nbt = {{ VillagerData: {{ profession:"minecraft:{}" }} }}] run function {}'.format(objective_name, villager_type, namespaced_selector))
		
		execute_conditions_list = [
			lambda adv_child: 'if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_child.item_selector)
		]

	elif adv_link.selector == 'cat_morning_gift':
		objective_name = 'sleeping'
		objective_num -= 1

		tick_function_list.append('execute as @a[scores = { sleeping = 0.. }] store result score @s sleeping run data get entity @s SleepTimer')
		tick_function_list.append('execute as @a[scores = {{ sleeping = 101 }}] at @s at @e[distance = ..16, type = minecraft:cat] run function {}'.format(namespaced_selector))

		execute_conditions_list = [
			lambda adv_child: 'if entity @e[distance = ..4, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_child.item_selector),
			lambda adv_child: 'as @s[nbt = {{ Inventory: [{{ id: "minecraft:{}" }}] }}]'.format(adv_child.item_selector)
		]

	elif loot_table_map.original.typ is eLootTable.entity:
		use_helper = True

		if adv_link.selector == 'player':
			conditions = EntityKilledPlayer()
			killed_trigger_type = eTrigger.entity_killed_player
		else:
			conditions = PlayerKilledEntity()
			conditions.entity = Entity()
			if 'sheep' in loot_table_maps[adv_link.selector].path:
				conditions.entity.typ = 'minecraft:sheep'
				conditions.entity['Color'] = sheep_color_to_number(adv_link.selector)
			else:
				conditions.entity.typ = 'minecraft:{}'.format(adv_link.selector)
			killed_trigger_type = eTrigger.player_killed_entity

		advancements[helper_selector] = Advancement()
		advancements[helper_selector].criteria = {
			'kill': Criteria.populate(killed_trigger_type, conditions)
		}

		advancements[helper_selector].rewards = Rewards()
		advancements[helper_selector].rewards.function = namespaced_helper
		functions[helper_selector] = ['scoreboard players set @a {} 1'.format(objective_name)]
		
		tick_function_list.append('execute as @a[scores = {{ {} = 1.. }}] at @s run function {}'.format(objective_name, namespaced_selector))

		execute_conditions_list = [
			lambda adv_child: 'if entity @e[distance = ..64, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_child.item_selector)
		]

		reset_objective = True
		grant_target_selector = ''

	elif adv_link.selector == 'fishing':
		use_helper = True

		conditions = FishingRodHooked()

		advancements[helper_selector] = Advancement()
		advancements[helper_selector].criteria = {
			'fish': Criteria.populate(eTrigger.fishing_rod_hooked, conditions)
		}

		advancements[helper_selector].rewards = Rewards()
		advancements[helper_selector].rewards.function = namespaced_helper
		functions[helper_selector] = ['scoreboard players set @a {} 1'.format(objective_name)]

		tick_function_list.append('execute as @a[scores = {{ {} = 1.. }}] at @s run function {}'.format(objective_name, namespaced_selector))
				
		parent_name = get_upper_selector(adv_link.selector)
		advancements[pathed_selector].display.description = "{} Loot Table Reference".format(parent_name)

		execute_conditions_list = [
			lambda adv_child: 'if entity @e[distance = ..64, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item:{{ id:"minecraft:{}" }}}}]'.format(adv_child.item_selector)
		]

		reset_objective = True
		grant_target_selector = ''

	else:
		print("No problem!")
		print("...{}".format(adv_link))
		print("Didn't Work!")

	generate_children_functions(pathed_selector, adv_link, path, base, child_index, execute_conditions_list)

	reset_function_list.append('scoreboard objectives add {} {}'.format(objective_name, objective_criteria))
	reset_function_list.append('scoreboard players set @a {} 0'.format(objective_name))
	if reset_objective:
		functions[pathed_selector].append('scoreboard players set @s {} 0'.format(objective_name))
	if use_helper:
		functions[pathed_selector].append('advancement revoke @s[scores = {{ incomplete = 1.. }}] only {}'.format(namespaced_helper))

	functions[pathed_selector].append('advancement grant @s{} only {}'.format(grant_target_selector, namespaced_selector))
	functions[pathed_selector].append('scoreboard players reset @s[scores = {{ incomplete = 0 }}] {}'.format(objective_name))
	functions[pathed_selector].append('say @s triggered {} : because {}'.format(namespaced_selector, objective_name))
	functions[pathed_selector].append('execute as @s[scores = {{ complete = 1.. }}] run say @s got {}'.format(namespaced_selector))

def generate_single_advancement(adv_link: AdvItem, pathed_selector: str, namespaced_parent_selector: str, hidden: bool = True, gen_base_criteria: bool = True):
	selector = adv_link.selector
	cap_name = get_upper_selector(selector)
	item_selector = 'minecraft:{}'.format(adv_link.item_selector)

	advancement = Advancement()

	advancement.display = Display.populate(
		icon		= item_selector,
		title		= adv_link.title if adv_link.title is not None else cap_name,
		description = adv_link.description if (adv_link.description is not None) else 'No Description',
		frame		= adv_link.adv_item_type.get_frame(),
		show		= True,
		announce	= True,
		hidden		= False #hidden
	)

	if namespaced_parent_selector is not None:
		advancement.parent = namespaced_parent_selector
	else:
		advancement.display.background = 'minecraft:textures/block/dirt.png'
	advancements[pathed_selector] = advancement

	if gen_base_criteria:
		if (adv_link.adv_item_type is eAdvItemType.block or adv_link.adv_item_type is eAdvItemType.from_items or adv_link.selector == 'armor_stand') and adv_link.selector == adv_link.item_selector:
			conditions = InventoryChanged()
			conditions.req_items = [ Item.populate(item_id = item_selector) ]
			advancement.criteria = { 'collect': Criteria.populate(eTrigger.inventory_changed, conditions) }
		else:
			advancement.criteria = { 'get': Criteria.populate(eTrigger.impossible) }

def get_parent_tab(loot_table_map: LootTableMap):
	if loot_table_map.original.typ is eLootTable.advancement_reward:
		return 'advancement_reward'
	elif loot_table_map.original.typ is eLootTable.block:
		return 'blocks'
	elif loot_table_map.original.typ is eLootTable.chest:
		if 'village' in loot_table_map.path:
			return 'village_chests'
		else:
			return 'chests'
	elif loot_table_map.original.typ is eLootTable.empty:
		return 'no_parent'
	elif loot_table_map.original.typ is eLootTable.entity:
		if 'sheep' in loot_table_map.path or loot_table_map.selector == 'sheep':
			return 'sheep'
		else:
			return 'entities'
	elif loot_table_map.original.typ is eLootTable.fishing:
		return 'fishing'
	elif loot_table_map.original.typ is eLootTable.generic:
		return 'generic_tables'
	elif loot_table_map.original.typ is eLootTable.gift:
		return 'gifts'
	else:
		return 'no_parent'

def set_child_description(adv_link: AdvItem, adv_child: AdvItem):
	link_name = adv_link.title if adv_link.title is not None else get_upper_selector(adv_link.selector)
	child_name = get_upper_selector(adv_child.selector)

	loot_table_map = loot_table_maps[adv_link.selector]
	
	if adv_child.adv_item_type is eAdvItemType.item or adv_child.adv_item_type is eAdvItemType.loop:
		item = 'This Item'
	elif adv_child.adv_item_type is eAdvItemType.reference:
		item = 'a {} Item'.format(child_name)

	if adv_link.selector == 'sheep' or 'fishing' in loot_table_map.path:
		action = 'Collect'
		origin = 'From This Loot Table'

	elif adv_link.selector == 'armor_stand':
		action = 'Collect'
		origin = 'From an Armor Stand'

	elif adv_link.selector == 'player':
		action = 'Drop'
		origin = 'When You Die'

	elif loot_table_map.original.typ is eLootTable.entity:
		action = 'Collect'
		origin = 'From a {}'.format(link_name)

	elif adv_link.selector == 'fishing':
		action = 'Hook'
		origin = 'While Fishing'

	elif loot_table_map.original.typ is eLootTable.block:
		action = 'Collect'
		origin = 'From {}'.format(link_name)

	elif loot_table_map.original.typ is eLootTable.chest:
		action = 'Find'
		origin = 'in a {}'.format(link_name)

	elif loot_table_map.original.typ is eLootTable.gift and 'hero_of_the_village' in loot_table_map.path:
		action = 'Recieve'
		origin = 'as a {}'.format(link_name)

	elif adv_link.selector == 'cat_morning_gift':
		action = 'Recieve'
		origin = 'From Your Cat'

	else:
		print('Warning: unknown parent advancement type... {}'.format(adv_link))
		action = 'Get'
		origin = 'From {}'.format(link_name)
	
	adv_child.description = '{} {} {}'.format(action, item, origin)

def generate_advancements(loot_table_map: LootTableMap):
	parent = get_parent_tab(loot_table_map)
	pathed_parent = get_namespaced_selector(parent)
	parent_selector = parent

	base = loot_table_map.selector
	path = loot_table_map.file_path

	first_path = get_pathed_selector(loot_table_map.selector, path, base, 0)
	pathed_selector = first_path

	from_items_length = 0
	child_pathed_parent = None

	for link_index in range(0, len(loot_table_map.adv_chain)):
		loot_table_map.adv_length += 1

		adv_link = loot_table_map.adv_chain[link_index]

		if adv_link.adv_item_type is eAdvItemType.from_items and child_pathed_parent is not None:
			loot_table_map.adv_length += from_items_length
			from_items_length = 0
			pathed_parent = child_pathed_parent

		pathed_selector = get_pathed_selector(adv_link.selector, path, base, link_index)
		generate_single_advancement(adv_link, pathed_selector, pathed_parent)
		
		parent_selector = adv_link.selector
		pathed_parent = get_namespaced_selector(pathed_selector)

		if parent_selector in loot_table_map.adv_branches:
			child_pathed_parent = pathed_parent
			branch = loot_table_map.adv_branches[parent_selector]
			split = False
			branch_length = len(branch)
			if link_index == len(loot_table_map.adv_chain) - 1:
				split = branch_length > 6
				column = 0
				if not split:
					loot_table_map.adv_length += branch_length

			for adv_child in branch:
				if adv_child.selector == 'attached_pumpkin_stem':
					print(adv_link)
					print(adv_child)
				set_child_description(adv_link, adv_child)
				child_pathed_selector = get_pathed_selector(adv_child.selector, path, base, link_index + 1)
				generate_single_advancement(adv_child, child_pathed_selector, child_pathed_parent)

				child_pathed_parent = get_namespaced_selector(child_pathed_selector)
				from_items_length += 1
				if split:
					column += 1
					loot_table_map.adv_length += 0.5
					if column >= branch_length / 2:
						child_pathed_parent = pathed_parent
						column = 0
		
		generate_conditions(pathed_selector, adv_link, path, base, link_index)

	if parent != 'fishing':
		if loot_table_map.adv_length == 1:
			advancements[first_path].parent = get_namespaced_selector('no_drops')
		elif loot_table_map.adv_length < 8:
			advancements[first_path].parent = get_namespaced_selector(parent, '_short')
		elif loot_table_map.adv_length < 16 and parent == 'entities':
			advancements[first_path].parent = get_namespaced_selector(parent, '_medium_short')
		elif loot_table_map.adv_length >= 24 and parent == 'entities':
			advancements[first_path].parent = get_namespaced_selector(parent, '_long')
	
	tab_name = advancements[first_path].parent.replace('{}:'.format(datapack_name), '')
	if tab_name not in tabs:
		tabs.append(tab_name)
		tabs_possible_images[tab_name] = []

	tabs_possible_images[tab_name].append(loot_table_map.adv_chain[0].item_selector)

count = 0
for loot_table_map in loot_table_maps.values():
	# print('Generating Advancements for: {}'.format(loot_table_map.selector))
	if not loot_table_map.is_sub:
		generate_advancements(loot_table_map)
		count += 1
# print('{} trees'.format(count))

debug_function_list = ['advancement revoke @a everything']
for tab in tabs:
	tab_selector = get_pathed_selector(tab, '', '', -1)
	adv_tab = AdvItem.populate(tab, eAdvItemType.tab, random.choice(tabs_possible_images[tab]))
	generate_single_advancement(adv_tab, tab_selector, None, False, False)
	advancements[tab_selector].criteria = {'randomize_your_world': Criteria.populate(eTrigger.impossible)}
	debug_function_list.append('advancement grant @a from rand_loot_adv_tree_1:{}'.format(tab))

print('Writing Files...')
# Create Files

zipbytes = io.BytesIO()
zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

for file_name, loot_table_map in loot_table_maps.items():
	# print('Writing Loot Table for: {}'.format(file_name))
	zip.writestr(os.path.join('data/minecraft/loot_tables', loot_table_map.file_path, '{}.json'.format(file_name)), loot_table_map.contents)

for full_path, advancement in advancements.items():
	# print('Writing Advancement for: {}'.format(full_path))
	zip.writestr(os.path.join('data/{}/advancements'.format(datapack_name), '{}.json'.format(full_path)), json.dumps(advancement))

for full_path, function_list in functions.items():
	# print('Writing Advancement for: {}'.format(full_path))
	zip.writestr(os.path.join('data/{}/functions'.format(datapack_name), '{}.mcfunction'.format(full_path)), "\n".join(function_list))
	
zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))

zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))
zip.writestr('data/minecraft/tags/functions/tick.json', json.dumps({'values':['{}:tick'.format(datapack_name)]}))

zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), "\n".join(reset_function_list))
zip.writestr('data/{}/functions/remove.mcfunction'.format(datapack_name), "\n".join(remove_function_list))
zip.writestr('data/{}/functions/tick.mcfunction'.format(datapack_name), "\n".join(tick_function_list))
zip.writestr('data/{}/functions/debug.mcfunction'.format(datapack_name), "\n".join(debug_function_list))
	
zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())

# for key in conditions:
# 	with open(os.path.join('restrictions', '{}.json'.format(key.name)), 'wt') as file:
# 		file.write(json.dumps(conditions[key]))
		
print('Created datapack "{}"'.format(datapack_filename))