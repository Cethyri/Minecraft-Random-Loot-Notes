import os
import random
import io
import zipfile
import json
import sys
import re
import math

from typing import Dict, List

from loot_table_map import LootTableMap, populate_advancement_chain, AdvItem, eAdvItemType, validate_conditions
from loot_table import LootTable
from advancement import Advancement, Rewards
from display import Display, Icon, TextComponent
from criteria import Criteria, eTrigger, TriggerConditions, InventoryChanged, Impossible
from item import Item


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
for selector in loot_table_maps:
	# print('Populating chain for: {}'.format(selector))
	populate_advancement_chain(selector, loot_table_maps)
	for adv_item in loot_table_maps[selector].adv_chain:
		if not adv_item.selector == selector:
			loot_table_maps[adv_item.selector].is_sub = not loot_table_maps[adv_item.selector].is_loop

print('Generating Advancements...')

def make_root_adv() -> Advancement:
	criteria = {
		'randomize_your_world': Criteria.populate(eTrigger.impossible)
	}
	display = Display.populate(
		icon		= 'minecraft:music_disc_11',
		title		= 'You Broke Minecraft',
		description	= 'Randomize Your World',
		frame		= eAdvItemType.tab,
		background	= 'minecraft:textures/block/dirt.png',
		show		= False,
		announce	= False,
		hidden		= False
	)
	return Advancement.populate(criteria = criteria, display = display)

def make_subroot_adv() -> Advancement:
	adv = make_root_adv()
	adv.parent = '{}:{}'.format(datapack_name, 'root')
	return adv

def upper(match):
	return match.group(1).replace('_', ' ').upper()

def generate_single_advancement(adv_link: AdvItem, link_index: int, path: str, base: str, parent: str, gen_cond: bool = True, display: bool = False) -> str:
	selector = adv_link.selector
	cap_selector = re.sub(r'((^|_)[a-z])', upper, selector)
	namespaced_selector = 'minecraft:{}'.format(adv_link.valid_selector)
	name = '{}_{}'.format(link_index, selector) if link_index >= 0 else selector
	pathed_selector = os.path.join(path, base, name).replace('\\', '/')

	advancement = Advancement()
	if gen_cond:
		conditions = InventoryChanged()
		conditions.req_items = [
			Item.populate(item_id = namespaced_selector)
		]
		trigger_type = eTrigger.inventory_changed
		advancement.criteria = {
			'interact': Criteria.populate(trigger_type, conditions)
		}
	else:
		advancement.criteria = {
			'randomize_your_world': Criteria.populate(eTrigger.impossible)
		}

	advancement.display = Display.populate(
		icon		= namespaced_selector,
		title		= cap_selector,
		description	= 'Collect {}'.format(cap_selector),
		frame		= adv_link.adv_item_type,
		show		= True,
		announce	= True,
		hidden		= not display
	)
	if parent is not None:
		advancement.parent = '{}:{}'.format(datapack_name, parent)
	else:
		advancement.display.background = 'minecraft:textures/block/dirt.png'
	advancements[pathed_selector] = advancement
	return pathed_selector

def generate_advancements(loot_table_map: LootTableMap, parent: str):
	pathed_parent = parent
	parent_selector = parent
	base = loot_table_map.selector
	path = loot_table_map.file_path
	first_path = ''
	length = 0
	for link_index in range(0, len(loot_table_map.adv_chain)):
		length += 1
		adv_link = loot_table_map.adv_chain[link_index]
		pathed_parent = generate_single_advancement(adv_link, link_index, path, base, pathed_parent)
		if link_index == 0:
			first_path = pathed_parent

		parent_selector = adv_link.selector

		if parent_selector in loot_table_map.adv_branches:
			branch_pathed_parent = pathed_parent
			branch = loot_table_map.adv_branches[parent_selector]
			split = False
			if link_index == len(loot_table_map.adv_chain) - 1:
				if len(branch) > 3:
					split = True
				else:
					length += len(branch)

			column = 0
			for adv_branch in branch:
				branch_pathed_parent = generate_single_advancement(adv_branch, link_index + 1, path, base, branch_pathed_parent)
				if split:
					length += 0.5
					column += 1
					if column >= len(branch) / 2:
						branch_pathed_parent = pathed_parent
						column = 0
	
	if length == 1:
		del advancements[first_path]
	elif length <= 7:
		advancements[first_path].parent = '{}:{}_short'.format(datapack_name, parent)


advancements: Dict[str, Advancement] = {}
generate_single_advancement(AdvItem.populate('blocks',		eAdvItemType.item, 'grass_block'),			-1, '', '', None, False, True)
generate_single_advancement(AdvItem.populate('chests',		eAdvItemType.item, 'chest'),				-1, '', '', None, False, True)
generate_single_advancement(AdvItem.populate('entities',	eAdvItemType.item, 'skeleton_spawn_egg'),	-1, '', '', None, False, True)
generate_single_advancement(AdvItem.populate('gameplay',	eAdvItemType.item, 'wooden_sword'),			-1, '', '', None, False, True)

generate_single_advancement(AdvItem.populate('blocks_short',	eAdvItemType.item, 'grass_block'),			-1, '', '', None, False, True)
generate_single_advancement(AdvItem.populate('chests_short',	eAdvItemType.item, 'chest'),				-1, '', '', None, False, True)
generate_single_advancement(AdvItem.populate('entities_short',	eAdvItemType.item, 'skeleton_spawn_egg'),	-1, '', '', None, False, True)
generate_single_advancement(AdvItem.populate('gameplay_short',	eAdvItemType.item, 'wooden_sword'),			-1, '', '', None, False, True)

for loot_table_map in loot_table_maps.values():
	# print('Generating Advancements for: {}'.format(loot_table_map.selector))
	if not loot_table_map.is_sub:
		if 'blocks' in loot_table_map.path:
			parent = 'blocks'
		elif 'entities' in loot_table_map.path:
			parent = 'entities'
		elif 'chests' in loot_table_map.path:
			parent = 'chests'
		else:
			parent = 'gameplay'
		generate_advancements(loot_table_map, parent)

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
	
zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))

zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))

zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Loot table randomizer with advancement tree by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]')
zip.writestr('data/{}/functions/give_all.mcfunction'.format(datapack_name),
'advancement grant @a from rand_loot_adv_tree_1:blocks\n' +
'advancement grant @a from rand_loot_adv_tree_1:chests\n'+
'advancement grant @a from rand_loot_adv_tree_1:entities\n'+
'advancement grant @a from rand_loot_adv_tree_1:gameplay\n'+
'advancement grant @a from rand_loot_adv_tree_1:blocks_short\n'+
'advancement grant @a from rand_loot_adv_tree_1:chests_short\n'+
'advancement grant @a from rand_loot_adv_tree_1:entities_short\n'+
'advancement grant @a from rand_loot_adv_tree_1:gameplay_short\n')
	
zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())
	
print('Created datapack "{}"'.format(datapack_filename))