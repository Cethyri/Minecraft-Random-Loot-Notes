import os
import random
import io
import zipfile
import json
import sys
import re

from typing import Dict, List

from loot_table_map import LootTableMap, populate_advancement_chain
from loot_table import LootTable
from dict_helper import get_all_entries


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

loot_table_maps: Dict[str, LootTableMap] = {}
remaining_selectors: List[str] = []

def load_table_info():
	for dirpath, _dirnames, filenames in os.walk('loot_tables'):
		for filename in filenames:
			selector = filename.replace('.json', '')
			path = dirpath.replace('loot_tables\\', '').split('\\')
			with open(os.path.join(dirpath, filename)) as json_file:
				json_body = json.load(json_file)
				loot_table = LootTable(json_body)
			loot_table_maps[selector] = LootTableMap(selector, path, loot_table)
			remaining_selectors.append(selector)
load_table_info()


print('Randomizing drops...')

#For Randomization to match Sethbling's the python version must be 3.6+ (For ordered dictionaries)
def randomize():
	for selector in loot_table_maps:
		i = random.randint(0, len(remaining_selectors) - 1)
		loot_table_maps[selector].remapped = loot_table_maps[remaining_selectors[i]].original
		loot_table_maps[selector].remap_selector = remaining_selectors[i]
		del remaining_selectors[i]
randomize()
		

print('Populating Advancement chains...')

for selector in loot_table_maps:
	print('Populating chain for: {}'.format(selector))
	populate_advancement_chain(selector, loot_table_maps)


print('Generating Advancements...')

advancements = {
	'root': {
		'display': {
			'title': {
				'text': 'You Broke Minecraft'
			},
			'description': {
				'text': 'Randomize Your World'
			},
			'icon': {
				'item': 'minecraft:music_disc_11'
			},
			'frame': 'challenge',
			'show_toast': False,
			'announce_to_chat': False,
			'hidden': True,
			'background': 'minecraft:textures/block/grass.png'
		},
		'criteria': {
			'randomize_your_world': {
				'trigger': 'minecraft:impossible'
			}
		}
	}
}

def generate_advancements(loot_table: dict):
	parent = 'root'
	for link_index in range(0, len(loot_table['adv_chain'])):
		selector = loot_table['adv_chain'][link_index]
		name = selector if parent is 'root' else '{}_{}_{}'.format(loot_table['selector'], link_index, selector)
		path = '\\'.join(loot_table['path'])
		id = os.path.join(path, loot_table['selector'], name)
		advancements[selector] = {
			'display': {
				'title': {
					'text': selector
				},
				'description': {
					'text': 'collect: {}'.format(selector)
				},
				'icon': {
					'item': 'minecraft:music_disc_11'
				},
				'frame': 'challenge',
				'show_toast': False,
				'announce_to_chat': False,
				'hidden': True
			},
			'parent': '',
			'criteria': {
				'randomize_your_world': {
					'trigger': 'minecraft:inventory_changed',
					'conditions': {
						'items': [
							{
								'item': 'minecraft:{}'.format(selector)
							}
						]
					}
				}
			}
		}

		if (selector in loot_table['adv_branches']):
			branch = loot_table['adv_branches'][selector]
			for branch_index in range(0, len(branch)):
				selector = loot_table['adv_chain'][link_index]
				name = selector if parent is 'root' else '{}_{}_{}'.format(loot_table['selector'], link_index, selector)
				path = '\\'.join(loot_table['path'])
				id = os.path.join(path, loot_table['selector'], name)
				advancements[selector] = {
					'display': {
						'title': {
							'text': selector
						},
						'description': {
							'text': 'collect: {}'.format(selector)
						},
						'icon': {
							'item': 'minecraft:music_disc_11'
						},
						'frame': 'challenge',
						'show_toast': False,
						'announce_to_chat': False,
						'hidden': True
					},
					'parent': '',
					'criteria': {
						'randomize_your_world': {
							'trigger': 'minecraft:inventory_changed',
							'conditions': {
								'items': [
									{
										'item': 'minecraft:{}'.format(selector)
									}
								]
							}
						}
					}
				}
		parent = id


print(json.dumps(loot_table_maps['player'].__dict__))



# zipbytes = io.BytesIO()
# zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

# for file_name in loot_table_maps:
		
# 	zip.writestr(os.path.join('data/minecraft/', file_dict[from_file]), contents)
	
# zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))

# zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))

# zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Loot table randomizer with advancement tree by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]')
	
# zip.close()
# with open(datapack_filename, 'wb') as file:
# 	file.write(zipbytes.getvalue())
	
# print('Created datapack "{}"'.format(datapack_filename))