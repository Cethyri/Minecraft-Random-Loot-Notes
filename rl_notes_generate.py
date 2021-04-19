import os
import random
import io
import zipfile
import json
import sys
import math

from enum import Enum
from typing import Dict, List, Callable

from rln.loot_table_map import LootTableMap, populate_advancement_chain, AdvItem, eAdvItemType, validate_conditions

from rln.helpers.regex import fix_a_an, get_upper_selector, shorten_selector, remove_initial_dashes

from rln.mc.interactable import MCActionInfo, eItemType, eActionType

from rln.mc.data_structures.loot_table import LootTable, eLootTable
from rln.mc.data_structures.advancement import Advancement, Rewards
from rln.mc.data_structures.condition import Condition, eCondition, eRestriction, get_restriction_level
from rln.mc.data_structures.display import Display, Icon, TextComponent
from rln.mc.data_structures.criteria import Criteria, eTrigger, InventoryChanged, Impossible, PlayerKilledEntity, EntityKilledPlayer, FishingRodHooked
from rln.mc.data_structures.item import Item
from rln.mc.data_structures.entity import Entity
from rln.mc.data_structures.recipe import CraftingShaped, eRecipe, Ingredient, Result

print('Checking flags and setting up...')

with open('rln/data/flags.json') as json_file:
	flags_from_json = json.load(json_file)
	flags = {}
	for flag in flags_from_json:
		flags[flag] = False

seed_given = False
flags_used = False
if len(sys.argv) > 1:
	argstart = 1
	if not sys.argv[1].startswith('-'):
		argstart = 2
		seed = sys.argv[1]
		seed_given = True
		print(f'Using {seed} as the seed')

	for i in range(argstart, len(sys.argv)):
		arg = remove_initial_dashes(sys.argv[i])
		if arg in flags:
			flags[arg] = True
			flags_used = True
		else:
			print(f'{sys.argv[i]} is not a recognized flag, ignoring...')

if not seed_given:	
	seed = random.randint(-sys.maxsize, sys.maxsize)
	if not flags['save-seed']:
		print('If you want to use a specific randomizer seed, use: "python randomize.py <seed>".')

if (seed_given and not flags['hide-seed']) or (flags['save-seed'] and not seed_given):
	datapack_name = f'rl_notes_{seed}'
else:
	datapack_name = 'rl_notes'

random.seed(seed)
datapack_desc = f'Loot Table Randomizer With Notes, Seed: "{seed}"'

if not flags_used:
	print('Customization is available through flags. If you would like to see a list of flags use: "python rl_notes_help.py"')
	
datapack_filename = datapack_name + '.zip'

print(flags)

notesGrantSelector = '@s'
if (flags['co-op']):
	notesGrantSelector = '@a'


print('Generating datapack...')

loot_table_maps: Dict[str, LootTableMap] = {}
remaining_selectors: List[str] = []

update_pre_randomized = os.path.exists('randomized') and flags['update']
if update_pre_randomized:
	datapack_name = f'{datapack_name}_upd'
	datapack_desc = f'{datapack_desc}_upd'
	datapack_filename = datapack_name + '.zip'

selectors_to_remapped = {}
original_to_selector = {}


print('Loading Tables...')

with open('rln/mc/data/requires_cheats.json') as json_file:
	requires_cheats = json.load(json_file)

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
				#print(f'checking if {selector} remapped is outdated version of a current loot_table')
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
				print(f'failed to find matching table for {selector}')

	else:
		for selector in loot_table_maps:
			i = random.randrange(0, len(remaining_selectors))
			remapped_table = loot_table_maps[remaining_selectors[i]].original
			loot_table_maps[selector].remap_selector = remaining_selectors[i]
			loot_table_maps[selector].remapped = LootTable(json.loads(json.dumps(remapped_table))) #Deep Copy
			del remaining_selectors[i]
randomize()


print('Validating loot tables...')

def validate():
	for selector in loot_table_maps:
		# print(f'Validating: {selector}')
		validate_conditions(loot_table_maps[selector])
validate()
		

print('Populating Advancement chains...')

def populate():
	for selector in loot_table_maps:
		# print(f'Populating chain for: {selector}')
		populate_advancement_chain(selector, loot_table_maps)
		for adv_item in loot_table_maps[selector].adv_chain:
			if adv_item.selector != selector:
				loot_table_maps[adv_item.selector].is_sub = not loot_table_maps[adv_item.selector].is_loop
populate()


print('Generating Advancements...')

with open('rln/mc/data/double_tall_blocks.json') as json_file:
	double_tall_blocks = json.load(json_file)

tabs: List[str] = []
advancements: Dict[str, Advancement] = {}

rl_notes_item = 'writable_book'
current_advs_and_recipes = []
tabbed_advs_and_recipes = {}
recipes: Dict[str, CraftingShaped] = {}

objective_num = 0
functions: Dict[str, List[str]] = {}
functions['load'] = [
	f'execute unless score debug rln_loaded = 1 run function {datapack_name}:add',
	'scoreboard objectives add rln_loaded dummy',
	'scoreboard players set debug rln_loaded 1',
	'scoreboard objectives add show_debug trigger ["",{"text":"Debug"}]',
	'tellraw @a ["",{"text":"Loot table randomizer with notes, by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]',
]
functions['add'] = [
	'scoreboard objectives add rln_setup dummy',
	'scoreboard objectives add rln_complete dummy',
	'scoreboard objectives add rln_incomplete dummy',
	'scoreboard objectives add rln_ref_complete dummy',
]
functions['tick'] = [
	f'execute as @a unless score @s rln_setup = 1 run function {datapack_name}:setup'
]
functions['setup'] = [
	'scoreboard players set @s rln_setup 1',
	'tellraw @s ["",{"selector":"say rln_setup @s\'s RLNotes","color":"green"}]',
]
functions['debug'] = [
	f'function {datapack_name}:reset',
]
functions['reset'] = [
	'scoreboard players set debug rln_loaded 0'
	f'function {datapack_name}:remove',
	f'function {datapack_name}:load',
]
functions['remove'] = [
	'scoreboard objectives remove rln_setup',
	'scoreboard objectives remove rln_complete',
	'scoreboard objectives remove rln_incomplete',
	'scoreboard objectives remove rln_ref_complete',
]
functions['uninstall'] = [
	f'function {datapack_name}:remove',
	'scoreboard objectives remove rln_loaded',
	'scoreboard objectives remove show_debug',
]

def get_minecraft_selector(selector: str):
	return f'minecraft:{selector}'

def get_namespaced_selector(pathed_selector: str, additional: str = None):
	return f'{datapack_name}:{pathed_selector}{additional if additional is not None else ""}'

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
		print(f'SHEEP COLOR BROKEN! {color}')

def get_pathed_selector(selector: str, path: str, base: str, link_index: int):
	name = f'{link_index}-{selector}' if link_index >= 0 else selector
	return os.path.join(path, base, name).replace('\\', '/')

def generate_recipe(pathed_selector: str, parent_item_selector: str, parent_item_is_correct: bool, child_item_selector: str, child_item_is_correct: bool, group_selector: str):
	recipe = CraftingShaped()
	recipe.typ = eRecipe.crafting_shaped
	recipe.group = f'rl_notes_{group_selector}'
	recipe.pattern = [
		f'{" " if parent_item_is_correct and child_item_is_correct else "B"}I',
		'PK'
	]

	knowledge_book = Ingredient()
	knowledge_book.item = 'minecraft:knowledge_book'
	parent = Ingredient()
	parent.item = parent_item_selector
	child = Ingredient()
	child.item = child_item_selector
	barrier = Ingredient()
	barrier.item = 'minecraft:barrier'

	recipe.key = {
		'I': child,
		'P': parent,
		'K': knowledge_book,
		'B': barrier
	}
	if parent_item_is_correct and child_item_is_correct:
		del recipe.key['B']
	
	recipe.result = Result()
	recipe.result.count = 1
	recipe.result.item = child_item_selector

	recipes[pathed_selector] = recipe
	current_advs_and_recipes.append(recipe)

def generate_children_functions(pathed_selector: str, start_link: AdvItem, path: str, base: str, child_index: int, execute_conditions_list: List[Callable]):
	
	functions[pathed_selector].append('scoreboard players set @s rln_incomplete 0')
	functions[pathed_selector].append('scoreboard players set @s rln_complete 0')
			
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
			functions[pathed_selector].append('scoreboard players set @s rln_ref_complete 0')

		references.append(current_map.selector)

		branches = []
		if cur_link.selector in current_map.adv_branches:
			branches.extend(current_map.adv_branches[cur_link.selector])
		if len(current_map.adv_chain) > 1 and current_map.adv_chain[1].adv_item_type is not eAdvItemType.from_items:
			branches.append(current_map.adv_chain[1])

		for adv_child in branches:
			child_pathed_selector = get_pathed_selector(adv_child.selector, path, base, 1 if is_reference else child_index)

			namespaced_selector = get_namespaced_selector(child_pathed_selector)
			if adv_child.adv_item_type is not eAdvItemType.reference and adv_child.selector == adv_child.item_selector:
				for execute_conditions in execute_conditions_list:
					functions[pathed_selector].append(f'execute {execute_conditions(adv_child)} run advancement grant @s only {namespaced_selector}')
				functions[pathed_selector].append(f'recipe give @s[advancements = {{ {namespaced_selector} = true }}] {namespaced_selector}')
				functions[pathed_selector].append(f'scoreboard players add @s[advancements = {{ {namespaced_selector} = true }}] rln_complete 1')
				functions[pathed_selector].append(f'scoreboard players add @s[advancements = {{ {namespaced_selector} = false }}] rln_incomplete 1')
				
				if is_reference:
					functions[pathed_selector].append(f'scoreboard players add @s[advancements = {{ {namespaced_selector} = true }}] rln_ref_complete 1')

			elif adv_child.adv_item_type is eAdvItemType.reference and adv_child.selector not in references:
				search_queue.append(adv_child)
				reference_namespaced_selectors[adv_child.selector] = namespaced_selector

		if is_reference:
			root_namespaced_selector = get_namespaced_selector(get_pathed_selector(cur_link.selector, path, base, 0))
			functions[pathed_selector].append(f'advancement grant @s[scores = {{ rln_ref_complete = 1.. }}] only {reference_namespaced_selectors[cur_link.selector]}')
			functions[pathed_selector].append(f'advancement grant @s[scores = {{ rln_ref_complete = 1.. }}] only {root_namespaced_selector}')
		else:
			is_reference = True

def generate_conditions(pathed_selector: str, adv_link: AdvItem, path: str, base: str, link_index: int):
	global objective_num

	if pathed_selector in functions:
		print('Warning: duplicate function!')

	loot_table_map = loot_table_maps[adv_link.selector]

	helper_selector = f'helper/{pathed_selector}'
	namespaced_helper = get_namespaced_selector(helper_selector)
	namespaced_selector = get_namespaced_selector(pathed_selector)
	
	functions[pathed_selector] = []

	objective_name = f'{shorten_selector(adv_link.selector)}_r{objective_num}'
	if len(objective_name) > 16:
		print(objective_name)
	objective_num += 1
	objective_criteria = 'dummy'
	use_helper = False
	reset_objective = False
	execute_conditions_list = []
	grant_target_selector = '[scores = { rln_incomplete = 0 }]'
	child_index = link_index + 1

	if adv_link.selector == 'sheep' or 'fishing' in loot_table_map.path:
		return
	
	elif adv_link.selector == 'armor_stand':
		functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 0.. }}] at @s at @e[distance = ..8, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item: {{ id:"minecraft:armor_stand" }} }}] run function {namespaced_selector}')

		execute_conditions_list = [
			lambda adv_child: f'if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]'
		]

		grant_target_selector = ''
		
	elif adv_link.selector in double_tall_blocks:
		for i in range(10):
			score = i + 1
			distance = score / 2
			functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 0 }}] at @s anchored eyes if block ^ ^ ^{distance} minecraft:{adv_link.selector} run scoreboard players set @s {objective_name} {score}')
			functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = {score} }}] at @s anchored eyes unless block ^ ^ ^{distance} minecraft:{adv_link.selector} positioned ^ ^ ^{distance} run function {namespaced_selector}')
			
		execute_conditions_list = [
			lambda adv_child: f'unless block ~ ~ ~ minecraft:{adv_link.selector} if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]'
		]
		
		reset_objective = True
		grant_target_selector = ''

	elif loot_table_map.original.typ is eLootTable.block:
		objective_criteria = f'minecraft.mined:minecraft.{adv_link.selector}'

		functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 1.. }}] at @s run function {namespaced_selector}')

		execute_conditions_list = [
			lambda adv_child: f'if entity @e[distance = ..8, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]'
		]

		reset_objective = True
		grant_target_selector = ''
		
	elif loot_table_map.original.typ is eLootTable.chest:
		loot_table_pathed_selector = get_pathed_selector(adv_link.selector, path, '', -1)

		for i in range(10):
			score = i + 1
			distance = score / 2
			functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 0 }}] at @s anchored eyes if block ^ ^ ^{distance} minecraft:chest{{ LootTable: "minecraft:{loot_table_pathed_selector}" }} run scoreboard players set @s {objective_name} {score}')
			functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = {score} }}] at @s anchored eyes unless block ^ ^ ^{distance} minecraft:chest{{ LootTable: "minecraft:{loot_table_pathed_selector}" }} positioned ^ ^ ^{distance} run function {namespaced_selector}')
			
		execute_conditions_list = [
			lambda adv_child: f'if block ~ ~ ~ minecraft:chest{{ Items: [{{ id: "minecraft:{adv_child.item_selector}" }}] }}'
		]
		
		reset_objective = True

	elif loot_table_map.original.typ is eLootTable.gift and 'hero_of_the_village' in loot_table_map.path:
		villager_type = adv_link.selector.replace('_gift', '')

		functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 0.. }}, nbt = {{ ActiveEffects: [{{ Id: 32b }}] }}] at @s at @e[distance = ..8, type = minecraft:villager, nbt = {{ VillagerData: {{ profession:"minecraft:{villager_type}" }} }}] run function {namespaced_selector}')
		
		execute_conditions_list = [
			lambda adv_child: f'if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]'
		]

	elif adv_link.selector == 'cat_morning_gift':
		objective_name = 'sleeping'
		objective_num -= 1

		functions['tick'].append('execute as @a[scores = { sleeping = 0.. }] store result score @s sleeping run data get entity @s SleepTimer')
		functions['tick'].append(f'execute as @a[scores = {{ sleeping = 101 }}] at @s at @e[distance = ..16, type = minecraft:cat] run function {namespaced_selector}')

		execute_conditions_list = [
			lambda adv_child: f'if entity @e[distance = ..4, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]',
			lambda adv_child: f'as @s[nbt = {{ Inventory: [{{ id: "minecraft:{adv_child.item_selector}" }}] }}]'
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
				conditions.entity.typ = get_minecraft_selector(adv_link.selector)
			killed_trigger_type = eTrigger.player_killed_entity

		advancements[helper_selector] = Advancement()
		advancements[helper_selector].criteria = {
			'kill': Criteria.populate(killed_trigger_type, conditions)
		}

		advancements[helper_selector].rewards = Rewards()
		advancements[helper_selector].rewards.function = namespaced_helper
		functions[helper_selector] = [f'scoreboard players set @a {objective_name} 1']
		
		functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 1.. }}] at @s run function {namespaced_selector}')

		execute_conditions_list = [
			lambda adv_child: f'if entity @e[distance = ..64, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]'
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
		functions[helper_selector] = [f'scoreboard players set @a {objective_name} 1']

		functions['tick'].append(f'execute as @a[scores = {{ {objective_name} = 1.. }}] at @s run function {namespaced_selector}')
				
		parent_name = get_upper_selector(adv_link.selector)
		advancements[pathed_selector].display.description = f'{parent_name} Loot Table Reference'

		execute_conditions_list = [
			lambda adv_child: f'if entity @e[distance = ..64, type = minecraft:item, limit = 1, nbt = {{ Age: 0s, Item:{{ id:"minecraft:{adv_child.item_selector}" }} }}]'
		]

		reset_objective = True
		grant_target_selector = ''

	else:
		print('No problem!')
		print(adv_link)
		print('Didn\'t Work!')

	generate_children_functions(pathed_selector, adv_link, path, base, child_index, execute_conditions_list)

	functions['reset'].append(f'scoreboard objectives add {objective_name} {objective_criteria}')
	functions['setup'].append(f'scoreboard players set @s {objective_name} 0')
	functions['remove'].append(f'scoreboard objectives remove {objective_name}')

	if reset_objective:
		functions[pathed_selector].append(f'scoreboard players set @s {objective_name} 0')
	if use_helper:
		functions[pathed_selector].append(f'advancement revoke @s[scores = {{ rln_incomplete = 1.. }}] only {namespaced_helper}')

	functions[pathed_selector].append(f'advancement grant @s{grant_target_selector} only {namespaced_selector}')
	functions[pathed_selector].append(f'scoreboard players reset @s[scores = {{ rln_incomplete = 0 }}] {objective_name}')
	
	functions[pathed_selector].append(f'execute if @s show_debug = 1 run tell @s @s triggered {namespaced_selector} : obj {objective_name}')
	functions[pathed_selector].append('execute if @s show_debug = 1 run tellraw @s [{ "text": "complete:"}, { "score": { "name": "@s", "objective": "rln_complete" } }, { "text": ", rln_incomplete:" },{ "score": { "name": "@s", "objective": "incomplete" } }]')

def generate_single_advancement(adv_link: AdvItem, pathed_selector: str, namespaced_parent_selector: str, parent_item_selector: str = None, parent_item_is_correct: bool = False, hidden: bool = True, gen_base_criteria: bool = True, show: bool = True, announce: bool = True):
	selector = adv_link.selector
	cap_name = get_upper_selector(selector)
	item_selector = get_minecraft_selector(adv_link.item_selector)

	if parent_item_selector is not None:
		generate_recipe(pathed_selector, parent_item_selector, parent_item_is_correct, item_selector, adv_link.selector == adv_link.item_selector, adv_link.selector)

	advancement = Advancement()
	if adv_link.adv_item_type is eAdvItemType.root or adv_link.adv_item_type is eAdvItemType.root_table:
		advancement.rewards = Rewards()
		advancement.rewards.recipes = [get_namespaced_selector(pathed_selector)]

	advancement.display = Display.populate(
		icon		= item_selector,
		title		= adv_link.title if adv_link.title is not None else cap_name,
		description = 'No Description',
		frame		= adv_link.adv_item_type.get_frame(),
		show		= show,
		announce	= announce,
		hidden		= hidden
	)

	if namespaced_parent_selector is not None:
		advancement.parent = namespaced_parent_selector
	else:
		advancement.display.background = 'minecraft:textures/block/dirt.png'

	if gen_base_criteria:
		advancement.criteria = { 'get': Criteria.populate(eTrigger.impossible) }
	
	advancements[pathed_selector] = advancement
	current_advs_and_recipes.append(advancement)

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
	elif loot_table_map.original.typ is eLootTable.empty:
		return 'no_parent'
	else:
		return 'no_parent'

def generate_advancements(loot_table_map: LootTableMap):
	parent = get_parent_tab(loot_table_map)
	pathed_parent = get_namespaced_selector(parent)
	parent_selector = parent
	parent_item_selector = get_minecraft_selector(rl_notes_item)
	parent_item_is_correct = False

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
		generate_single_advancement(adv_link, pathed_selector, pathed_parent, parent_item_selector, parent_item_is_correct)
		
		parent_selector = adv_link.selector
		parent_item_selector = f'minecraft:{adv_link.item_selector}'
		parent_item_is_correct = adv_link.item_selector == adv_link.selector
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
				child_pathed_selector = get_pathed_selector(adv_child.selector, path, base, link_index + 1)
				generate_single_advancement(adv_child, child_pathed_selector, child_pathed_parent, parent_item_selector, parent_item_is_correct)
				child_pathed_parent = get_namespaced_selector(child_pathed_selector)
				from_items_length += 1
				if split:
					column += 1
					loot_table_map.adv_length += 0.5
					if column >= branch_length / 2:
						child_pathed_parent = pathed_parent
						column = 0
		
		generate_conditions(pathed_selector, adv_link, path, base, link_index)

	tab_name = parent
	if parent != 'fishing':
		if loot_table_map.adv_length == 1:
			tab_name = 'no_drops'
		elif loot_table_map.adv_length < 8:
			tab_name = f'{parent}_short'
		elif loot_table_map.adv_length < 16 and parent == 'entities':
			tab_name = f'{parent}_medium_short'
		elif loot_table_map.adv_length >= 24 and parent == 'entities':
			tab_name = f'{parent}_long'

		advancements[first_path].parent = get_namespaced_selector(tab_name)
	
	if tab_name not in tabs:
		tabs.append(tab_name)

	if tab_name not in tabbed_advs_and_recipes:
		tabbed_advs_and_recipes[tab_name] = []
	tabbed_advs_and_recipes[tab_name].extend(current_advs_and_recipes)

count = 0
for loot_table_map in loot_table_maps.values():
	# print(f'Generating Advancements for: {loot_table_map.selector}')
	if not loot_table_map.is_sub:
		current_advs_and_recipes = []
		generate_advancements(loot_table_map)
		count += 1
# print(f'{count} trees')

page = 0
for tab in tabs:
	page += 1

	parent = f'rlnotes_tab_{page}'

	for stuff in tabbed_advs_and_recipes[tab]:
		if isinstance(stuff, Advancement):
			stuff.display.description = f'On RLNotes Tab {page}'
			stuff.parent = parent
		elif isinstance(stuff, CraftingShaped):
			stuff.result.count = page

	tab_selector = get_pathed_selector(parent, '', '', -1)

	title = f'RLNotes Tab {page}'
	adv_tab = AdvItem.populate(parent, eAdvItemType.tab, rl_notes_item, title, 'An RLNotes Tab')
	generate_single_advancement(adv_tab, tab_selector, None, hidden = False, gen_base_criteria = False, show = False, announce = False)
	advancements[tab_selector].criteria = {'take_notes': Criteria.populate(eTrigger.impossible)}
	functions['debug'].append(f'advancement grant @a from {datapack_name}:{tab_selector}')


print('Writing Files...')

zipbytes = io.BytesIO()
zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

for file_name, loot_table_map in loot_table_maps.items():
	# print(f'Writing Loot Table for: {file_name}')
	zip.writestr(os.path.join('data/minecraft/loot_tables', loot_table_map.file_path, f'{file_name}.json'), loot_table_map.contents)

for full_path, advancement in advancements.items():
	# print(f'Writing Advancement for: {full_path}')
	zip.writestr(os.path.join(f'data/{datapack_name}/advancements', f'{full_path}.json'), json.dumps(advancement))

for full_path, function_list in functions.items():
	# print(f'Writing Functions for: {full_path}')
	zip.writestr(os.path.join(f'data/{datapack_name}/functions', f'{full_path}.mcfunction'), '\n'.join(function_list))

for full_path, recipe in recipes.items():
	# print(f'Writing Recipe for: {full_path}')
	zip.writestr(os.path.join(f'data/{datapack_name}/recipes', f'{full_path}.json'), json.dumps(recipe))
	
zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))

zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':[f'{datapack_name}:load']}))
zip.writestr('data/minecraft/tags/functions/tick.json', json.dumps({'values':[f'{datapack_name}:tick']}))
	
zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())
		
print(f'Created datapack "{datapack_filename}"')