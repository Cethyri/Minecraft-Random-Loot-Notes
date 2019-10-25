import os
import random
import io
import zipfile
import json
import sys
import math

from typing import Dict, List, Callable

from loot_table_map import LootTableMap, populate_advancement_chain, AdvItem, eAdvItemType, validate_conditions
from loot_table import LootTable, eLootTable
from advancement import Advancement, Rewards
from display import Display, Icon, TextComponent
from criteria import Criteria, eTrigger, InventoryChanged, Impossible, PlayerKilledEntity, EntityKilledPlayer, FishingRodHooked
from item import Item
from entity import Entity

from re_helper import fix_a_an, get_upper_selector, shorten_selector

if len(sys.argv) >= 2:
	try:
		seed = int(sys.argv[1])
	except Exception:
		print('The seed "{}" is not an integer.'.format(sys.argv[1]))
		exit()
	random.seed(seed)
	datapack_name = 'rand_loot_adv_tree_{}'.format(seed)
	datapack_desc = 'Loot Table Randomizer Advancement Tree, Seed: {}'.format(seed)
else:
	print('If you want to use a specific randomizer seed integer, use: "python randomize.py <seed>"')
	datapack_name = 'rand_loot_adv_tree'
	datapack_desc = 'Loot Table Randomizer Advancement Tree'
	
datapack_filename = datapack_name + '.zip'


print('Generating datapack...')

loot_table_maps: Dict[str, LootTableMap] = {}
remaining_selectors: List[str] = []

def load_table_info():
	for dirpath, _dirnames, filenames in os.walk('loot_tables'):
		for filename in filenames:
			selector = filename.replace('.json', '')
			path = dirpath.replace('loot_tables\\', '').split('\\')
			with open(os.path.join(dirpath, filename)) as json_file:
				json_dict = json.load(json_file)
				if selector == 'guardian':
					pass
				loot_table = LootTable(json_dict)
			loot_table_maps[selector] = LootTableMap(selector, path, loot_table)
			remaining_selectors.append(selector)
load_table_info()


print('Randomizing drops...')

#For Randomization to match Sethbling's the python version must be 3.6+ (For ordered dictionaries)
def randomize():
	for selector in loot_table_maps:
		i = random.randrange(0, len(remaining_selectors))
		loot_table_maps[selector].remapped = LootTable(json.loads(json.dumps(loot_table_maps[remaining_selectors[i]].original)))
		loot_table_maps[selector].remap_selector = remaining_selectors[i]
		del remaining_selectors[i]
randomize()


print('Validating loot tables...')

def validate():
	for selector in loot_table_maps:
		# print('Validating: {}'.format(selector))
		validate_conditions(loot_table_maps[selector])
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
		
tabs_possible_images: Dict[str, List[str]] = {}
tabs: List[str] = []
advancements: Dict[str, Advancement] = {}

objective_num = 0
functions: Dict[str, List[str]] = {}

reset_function_list = [
	'tellraw @a ["",{"text":"Loot table randomizer with advancement tree by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]',
	'scoreboard objectives add incomplete dummy'
	'scoreboard objectives add complete dummy'
	'scoreboard objectives add reference_complete dummy'
]
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

def generate_descriptions_and_children_functions(pathed_selector: str, start_link: AdvItem, callback: Callable):
			
	references = []
	search_queue = [start_link]
	adv_link = start_link
	current_map = loot_table_maps[adv_link.selector]

	while True:
		adv_link = search_queue.pop()
		current_map = loot_table_maps[adv_link.selector]
		if current_map.selector in references:
			break

		references.append(current_map.selector)

		if adv_link.selector in current_map.adv_branches:
			for adv_child in current_map.adv_branches[adv_link.selector]:
				callback(adv_link, adv_child, adv_link == start_link)
				if adv_child.adv_item_type == eAdvItemType.reference:
					search_queue.append(adv_child)

def generate_conditions(pathed_selector: str, adv_link: AdvItem, path: str, base: str, link_index: int):
	global objective_num

	if pathed_selector in functions:
		print('Warning: duplicate function!')

	loot_table_map = loot_table_maps[adv_link.selector]

	helper_selector = "helper/{}".format(pathed_selector)
	namespaced_helper = get_namespaced_selector(helper_selector)
	namespaced_selector = get_namespaced_selector(pathed_selector)
	
	functions[pathed_selector] = []

	objective_name = 'rand_obj_{}'.format(objective_num)
	objective_num += 1
	child_index = link_index + 1

	if adv_link.selector == 'sheep' or 'fishing' in loot_table_map.path:
		return
	
	elif adv_link.selector == 'armor_stand':
		reset_function_list.append('scoreboard objectives add {} dummy'.format(objective_name))
		reset_function_list.append('scoreboard players set @a {} 1'.format(objective_name))
		
		tick_function_list.append('execute as @a[scores = {{ {} = 1.. }}] at @e[distance = ..8, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:armor_stand" }}}}] run function {}'.format(objective_name, pathed_selector))
		
		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, objective_name))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))
		functions[pathed_selector].append('scoreboard players set @s {} 0'.format(objective_name))

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
		functions[pathed_selector].append('scoreboard players set @s complete 0')
		
		references = []
		search_queue = [adv_link]
		reference_namespaced_selectors = {}
		cur_link = AdvItem
		current_map: LootTableMap
		is_reference = False

		while len(search_queue) > 0:
			cur_link = search_queue.pop()
			current_map = loot_table_maps[cur_link.selector]

			if is_reference:
				functions[pathed_selector].append('scoreboard players set @s reference_complete 0')

			references.append(current_map.selector)

			if cur_link.selector in current_map.adv_branches:
				for adv_child in current_map.adv_branches[cur_link.selector]:
					child_pathed_selector = get_pathed_selector(adv_child.selector, path, base, 1 if is_reference else child_index)

					if child_pathed_selector not in advancements:
						print('Oops, that is not an advancement...{} using path: {}'.format(adv_child, child_pathed_selector))

					namespaced_selector = get_namespaced_selector(child_pathed_selector)
					if adv_child.adv_item_type is eAdvItemType.item:
						functions[pathed_selector].append('execute if entity @e[distance = ..2, type = minecraft:item, limit = 1, nbt = {{ Age:0s, Item:{{ id:"minecraft:{}" }}}}] run advancement grant @s only {} got_parent'.format(adv_child.item_selector, namespaced_selector))
						functions[pathed_selector].append('scoreboard players add @s[advancement = {{ {} = true }}] complete'.format(namespaced_selector))
						functions[pathed_selector].append('scoreboard players add @s[advancement = {{ {} = false }}] incomplete'.format(namespaced_selector))
						
						if is_reference:
							functions[pathed_selector].append('scoreboard players add @s[advancement = {{ {} = true }}] reference_complete'.format(namespaced_selector))

					elif adv_child.selector not in references:
						search_queue.append(adv_child)
						reference_namespaced_selectors[adv_child.selector] = namespaced_selector

			if is_reference:
				root_namespaced_selector = get_namespaced_selector(get_pathed_selector(cur_link.selector, path, base, 0))
				functions[pathed_selector].append('advancement grant @s[score = {{ reference_complete = 1.. }}] {}'.format(reference_namespaced_selectors[cur_link.selector]))
				functions[pathed_selector].append('advancement grant @s[score = {{ reference_complete = 1.. }}] {}'.format(root_namespaced_selector))
			else:
				is_reference = True

		functions[pathed_selector].append('scoreboard players reset @s[score = {{ incomplete = 0 }}] {}'.format(objective_name))

	elif loot_table_map.original.typ is eLootTable.entity:
		if adv_link.selector == 'player':
			conditions = EntityKilledPlayer()
			killed_trigger_type = eTrigger.entity_killed_player
		else:
			conditions = PlayerKilledEntity()
			conditions.entity = Entity()
			if 'sheep' in loot_table_maps[adv_link.selector].path:
				conditions.entity.typ = 'minecraft:sheep'
				conditions.entity['color'] = sheep_color_to_number(adv_link.selector)
			else:
				conditions.entity.typ = 'minecraft:{}'.format(adv_link.selector)
			killed_trigger_type = eTrigger.player_killed_entity

		advancements[helper_selector] = Advancement()
		advancements[helper_selector].criteria = {
			'kill': Criteria.populate(killed_trigger_type, conditions)
		}

		advancements[helper_selector].rewards = Rewards()
		advancements[helper_selector].rewards.function = namespaced_selector

		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, helper_selector))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
		
		#add children

		functions[pathed_selector].append('advancement revoke @s[score = {{ incomplete = 1.. }}] {}'.format(namespaced_helper))

	elif adv_link.selector == 'fishing':
		conditions = FishingRodHooked()

		advancements[helper_selector] = Advancement()
		advancements[helper_selector].criteria = {
			'fish': Criteria.populate(eTrigger.fishing_rod_hooked, conditions)
		}

		advancements[helper_selector].rewards = Rewards()
		advancements[helper_selector].rewards.function = namespaced_selector

		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, helper_selector))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
				
		parent_name = get_upper_selector(adv_link.selector)
		advancements[pathed_selector].display.description = "{} Loot Table Reference".format(parent_name)

		#add children

		functions[pathed_selector].append('advancement revoke @s[score = {{ incomplete = 1.. }}] {}'.format(namespaced_helper))

	elif loot_table_map.original.typ is eLootTable.block:
		reset_function_list.append('scoreboard objectives add {} minecraft.mined:minecraft.{}'.format(objective_name, adv_link.selector))
		reset_function_list.append('scoreboard players set @a {} 0'.format(objective_name))

		tick_function_list.append('execute as @a[scores = {{ {} = 1.. }}] run function {}'.format(objective_name, namespaced_selector))

		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, objective_name))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))
		functions[pathed_selector].append('scoreboard players set @s {} 0'.format(objective_name))

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
		
		#add children

		functions[pathed_selector].append('scoreboard players reset @s[score = {{ incomplete = 0 }}] {}'.format(objective_name))

	elif loot_table_map.original.typ is eLootTable.chest:
		reset_function_list.append('scoreboard objectives add {} dummy'.format(objective_name))
		reset_function_list.append('scoreboard players set @a {} 0'.format(objective_name))

		for double in range(1, 10):
			distance = double / 2
			tick_function_list.append('execute as @a[scores = {{ {} = 0 }}] at @s anchored eyes if		block ^ ^ ^{} minecraft:chest {{ LootTable: "minecraft:{}" }} run scoreboard players set @s {0} 1'.format(objective_name, distance, pathed_selector))
			tick_function_list.append('execute as @a[scores = {{ {} = 1 }}] at @s anchored eyes unless	block ^ ^ ^{} minecraft:chest {{ LootTable: "minecraft:{}" }} run execute positioned ^ ^ ^{1} function {}'.format(objective_name, distance, pathed_selector, namespaced_selector))
		
		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, objective_name))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))
		functions[pathed_selector].append('scoreboard players set @s {} 0'.format(objective_name))

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
		
		#add children

		functions[pathed_selector].append('scoreboard players reset @s[score = {{ incomplete = 0 }}] {}'.format(objective_name))

	elif loot_table_map.original.typ is eLootTable.gift and 'hero_of_the_village' in loot_table_map.path:
		reset_function_list.append('scoreboard objectives add {} dummy'.format(objective_name))
		reset_function_list.append('scoreboard players set @a {} 1'.format(objective_name))

		villager_type = adv_link.selector.replace('_gift', '')

		tick_function_list.append('execute as @a[scores = {{ {} = 1.. }}, nbt = {{ ActiveEffects: [{{ Id: 32b }}] }}] at @e[distance = ..8, type = minecraft: villager, nbt = {{ VillagerData: {{ profession:"minecraft: {}" }} }}] run function {}'.format(objective_name, distance, pathed_selector, ))
		
		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, objective_name))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))
		functions[pathed_selector].append('scoreboard players set @s {} 0'.format(objective_name))

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
		
		#add children

		functions[pathed_selector].append('scoreboard players reset @s[score = {{ incomplete = 0 }}] {}'.format(objective_name))

	elif adv_link.selector == 'cat_morning_gift':
		reset_function_list.append('scoreboard objectives add sleeping dummy')
		reset_function_list.append('scoreboard players set @a sleeping 0')
		reset_function_list.append('scoreboard objectives add sleepTimer dummy')
		reset_function_list.append('scoreboard players set @a sleepTimer 0')

		tick_function_list.append('execute as @a[scores = {{ sleeping = 0.. }}] store result score @s sleeptimer run data get entity @s SleepTimer')
		tick_function_list.append('execute as @a[scores = {{ sleeping = 0, sleeptimer = 1.. }}] run scoreboard players set @s sleeping 1')
		tick_function_list.append('execute as @a[scores = {{ sleeping = 1, sleeptimer = 0 }}] run function {}'.format(namespaced_selector))

		functions[pathed_selector].append('say @s triggered {} : got {} : because {}'.format(pathed_selector, adv_link.selector, objective_name))
		functions[pathed_selector].append('advancement grant @s only {}'.format(namespaced_selector))
		functions[pathed_selector].append('scoreboard players set @s sleeping 0')

		functions[pathed_selector].append('scoreboard players set @s incomplete 0')
		
		#add children
		'execute as @a[scores={sleeping=1..}] at entity @e[distance=8.., type=minecraft:cat] run say got it!'

		functions[pathed_selector].append('scoreboard players reset @s[score = {{ incomplete = 0 }}] {}'.format(objective_name))

	else:
		print("No problem!")
		print("...{}".format(adv_link))
		print("Didn't Work!")


def generate_single_advancement(adv_link: AdvItem, pathed_selector: str, namespaced_parent_selector: str, hidden: bool = True, gen_base_criteria: bool = True):
	selector = adv_link.selector
	cap_name = get_upper_selector(selector)
	item_selector = 'minecraft:{}'.format(adv_link.item_selector)

	advancement = Advancement()

	advancement.display = Display.populate(
		icon		= item_selector,
		title		= adv_link.title if (adv_link.title is not None) else cap_name,
		description = adv_link.description,
		frame		= adv_link.adv_item_type,
		show		= True,#adv_link.adv_item_type == eAdvItemType.block or adv_link.adv_item_type == eAdvItemType.root or adv_link.adv_item_type == eAdvItemType.root_table,
		announce	= True,#False,
		hidden		= hidden and adv_link.adv_item_type != eAdvItemType.root and adv_link.adv_item_type != eAdvItemType.root_table
	)

	if namespaced_parent_selector is not None:
		advancement.parent = namespaced_parent_selector
	else:
		advancement.display.background = 'minecraft:textures/block/dirt.png'
	advancements[pathed_selector] = advancement

	if gen_base_criteria:
		if adv_link.adv_item_type is eAdvItemType.block or adv_link.adv_item_type is eAdvItemType.special and adv_link.selector == adv_link.item_selector:
			conditions = InventoryChanged()
			conditions.req_items = [
				Item.populate(item_id = item_selector)
			]
			advancement.criteria = {
				'collect': Criteria.populate(eTrigger.inventory_changed, conditions)
			}
		else:
			advancement.criteria = {
				'get': Criteria.populate(eTrigger.impossible)
			}

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
	link_name = get_upper_selector(adv_link.selector)
	child_name = get_upper_selector(adv_child.selector)
	
	if adv_child.adv_item_type is eAdvItemType.item:
		item = 'a {}'.format(child_name)
	elif adv_child.adv_item_type is eAdvItemType.reference:
		item = 'Items in the {} Loot Table'.format(child_name)

	if adv_link.selector == 'sheep' or 'fishing' in loot_table_map.path:
		action = 'Collect'
		origin = 'From the {} Loot Table'.format(link_name)

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
		origin = 'in a {} Chest'.format(link_name)

	elif loot_table_map.original.typ is eLootTable.gift and 'hero_of_the_village' in loot_table_map.path:
		action = 'Recieve'
		origin = 'as a {}'.format(link_name)

	elif adv_link.selector == 'cat_morning_gift':
		action = 'Wake up to'
		origin = 'From Your Cat'

	else:
		print('Warning: unknown child advancement type... {}'.format(adv_link))
		action: 'Get'
		origin: 'From {}'.format(link_name)
	
	adv_child.description = '{} {} {}'.format(action, item, origin)

def generate_advancements(loot_table_map: LootTableMap):
	parent = get_parent_tab(loot_table_map)
	pathed_parent = get_namespaced_selector(parent)
	parent_selector = parent

	base = loot_table_map.selector
	path = loot_table_map.file_path

	first_path = get_pathed_selector(loot_table_map.selector, path, base, 0)
	pathed_selector = first_path

	special_length = 0
	child_pathed_parent = None

	for link_index in range(0, len(loot_table_map.adv_chain)):
		loot_table_map.adv_length += 1

		adv_link = loot_table_map.adv_chain[link_index]

		if adv_link.adv_item_type is eAdvItemType.special:
			loot_table_map.adv_length += special_length
			special_length = 0
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
				if not split:
					loot_table_map.adv_length += branch_length

			for adv_child in branch:
				set_child_description(adv_link, adv_child)
				child_pathed_selector = get_pathed_selector(adv_child.selector, path, base, link_index + 1)
				generate_single_advancement(adv_child, child_pathed_selector, child_pathed_parent)

				child_pathed_parent = get_namespaced_selector(child_pathed_selector)
				special_length += 1
				if split:
					loot_table_map.adv_length += 0.5
					if loot_table_map.adv_length == branch_length / 2:
						child_pathed_parent = pathed_parent
		
		generate_conditions(pathed_selector, adv_link, path, base, link_index)

	if loot_table_map.adv_length == 1:
		del advancements[first_path]
		del functions[first_path]
		del functions[first_path]
	else:
		if parent != 'fishing':
			if loot_table_map.adv_length < 8:
				advancements[first_path].parent = get_namespaced_selector(parent, '_short')
			elif loot_table_map.adv_length < 16 and parent == 'entities':
				advancements[first_path].parent = get_namespaced_selector(parent, '_medium_short')
			elif loot_table_map.adv_length >= 24 and parent == 'entities':
				advancements[first_path].parent = get_namespaced_selector(parent, '_long')
		
		tab_name = advancements[first_path].parent.replace('{}:'.format(datapack_name), '')
		if advancements[first_path].parent not in tabs:
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
zip.writestr('data/{}/functions/tick.mcfunction'.format(datapack_name), "\n".join(tick_function_list))
zip.writestr('data/{}/functions/debug.mcfunction'.format(datapack_name), "\n".join(debug_function_list))
	
zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())
	
print('Created datapack "{}"'.format(datapack_filename))