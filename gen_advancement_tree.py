import os
import random
import io
import zipfile
import json
import sys
import re

if len(sys.argv) >= 2:
	try:
		seed = int(sys.argv[1])
	except Exception:
		print('The seed "{}" is not an integer.'.format(sys.argv[1]))
		exit()
	random.seed(seed)
	datapack_name = 'random_loot_advancement_tree_{}'.format(seed)
	datapack_desc = 'Loot Table Randomizer Advancement Tree, Seed: {}'.format(seed)
else:
	print('If you want to use a specific randomizer seed integer, use: "python randomize.py <seed>"')
	datapack_name = 'random_loot_advancement_tree'
	datapack_desc = 'Loot Table Randomizer Advancement Tree'
	
datapack_filename = datapack_name + '.zip'


print('Generating datapack...')

loot_tables = {}
remaining_selectors = []

def load_table_info():
	for dirpath, _dirnames, filenames in os.walk('loot_tables'):
		for filename in filenames:

			selector = filename.replace('.json', '')

			with open(os.path.join(dirpath, filename)) as json_file:
				loot_table = {
					'selector': selector,
					'path': dirpath.replace('loot_tables\\', '').split('\\'),
					'original': json.load(json_file),
					#'remapped': dict,
					#'remap_selector': str,
					#'adv_chain': list,
					#'adv_branches': dict
				}
			
			loot_tables[selector] = loot_table
			remaining_selectors.append(selector)
load_table_info()

print('Randomizing drops...')

#For Randomization to match Sethbling's the python version must be 3.6+ (For ordered dictionaries)
def randomize():
	for selector in loot_tables:
		i = random.randint(0, len(remaining_selectors) - 1)
		loot_tables[selector]['remapped'] = loot_tables[remaining_selectors[i]]['original']
		loot_tables[selector]['remap_selector'] = remaining_selectors[i]
		del remaining_selectors[i]
randomize()

def find_structures_with_parent(table: dict, is_match) -> list:
	root = {
		'parent': None,
		'structure': table
	}
	search_queue = [root]
	structures = [root] if is_match(table) else []

	while(len(search_queue) > 0):
		current = search_queue.pop()

		for value in (current['structure'] if isinstance(current['structure'], list) else current['structure'].values()):
			struc_with_parent = {
				'parent': current,
				'structure': value
			}
			if is_match(value):
				structures.append(struc_with_parent)

			if isinstance(value, [list, dict]):
				search_queue.append(struc_with_parent)

	return structures


def find_structures(table: dict, is_match) -> list:
	search_queue = [table]
	structures = [table] if is_match(table) else []

	while(len(search_queue) > 0):
		current = search_queue.pop()

		for value in (current if isinstance(current, list) else current.values()):
			if is_match(value):
				structures.append(value)

			if isinstance(value, (list, dict)):
				search_queue.append(value)

	return structures


def matches_item_or_loot_table(struct) -> bool:
	return (
		isinstance(struct, dict) and
		(
			'name' in struct and
			'type' in struct and
			(
				struct['type'] == 'minecraft:item' or
				struct['type'] == 'minecraft:loot_table'
			)
		)
	)


def get_all_item_drops(table: dict) -> list:
	if 'pools' not in table:
		return []

	pools = table['pools']
	items = []
	for pool in pools:
		for entry in pool['entries']:
			structures = find_structures(
				entry,
				matches_item_or_loot_table
			)

			for structure in structures:
				if structure['type'] == 'minecraft:loot_table':
					selector = 'loot_table:{}'.format(structure['name'].split('/').pop())
				else:
					selector = structure['name'].replace('minecraft:', '')

				if selector not in items:
						items.append(selector)
	return items

def populate_advancement_chain(selector: str):
	loot_table: dict = loot_tables[selector]
	loot_table['adv_chain'] = []
	loot_table['adv_branches'] = {}
	advancement_chain: list = loot_table['adv_chain']
	advancement_branches: dict = loot_table['adv_branches']
	next_selector = selector
	while True:
		advancement_chain.append(next_selector)
		items = get_all_item_drops(loot_table['remapped'])

		if loot_tables[loot_table['remap_selector']]['original']['type'] != 'minecraft:block':
			advancement_chain.append('loot_table:{}'.format(loot_table['remap_selector']))
		else:
			for i in range(len(items)):
				if isinstance(items[i], str) and items[i] == loot_table['remap_selector']:
					next_selector = items[i]
					del items[i]
					break

		advancement_branches[loot_table['selector']] = items

		loot_table = loot_tables[next_selector]

		if loot_table['selector'] in advancement_chain:
			break
		


print('Populating Advancement chains...')

# for selector in loot_tables:
# 	print('Populating chain for: {}'.format(selector))
# 	populate_advancement_chain(selector)
populate_advancement_chain('player')

print (loot_tables['player'])

# zipbytes = io.BytesIO()
# zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

# for from_file in file_dict:
# 	with open(from_file) as file:
# 		contents = file.read()
		
# 	zip.writestr(os.path.join('data/minecraft/', file_dict[from_file]), contents)
	
# zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))

# zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))

# zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Loot table randomizer with advancement tree by Cethyrion, adapted from SethBling's Loot table randomizer","color":"green"}]')
	
# zip.close()
# with open(datapack_filename, 'wb') as file:
# 	file.write(zipbytes.getvalue())
	
# print('Created datapack "{}"'.format(datapack_filename))