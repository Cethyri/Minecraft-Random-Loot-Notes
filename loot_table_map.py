import json

from typing import List, Dict, Union, Iterable
from enum import Enum

from mc_helper import mc_obj
from dict_helper import get_all_entries, get_all_conditions

from loot_table import LootTable, eLootTable
from entry import Entry, ItemEntry, LootTableEntry, eEntry
from display import eFrame
from condition import Condition, eCondition

class eAdvItemType(str, Enum):
	root		= 'task'
	block		= 'task'
	reference	= 'goal'
	loop		= 'goal'
	special		= 'goal'
	item		= 'challenge'
	tab			= 'challenge'


class AdvItem(dict):
	selector:		str				= mc_obj('selector', str)
	valid_selector:	str				= mc_obj('valid_selector', str)
	adv_item_type:	eAdvItemType	= mc_obj('adv_item_type', eAdvItemType)

	@staticmethod
	def populate(selector: str, adv_item_type: eAdvItemType, valid_selector: str = None):
		adv_item = AdvItem()
		adv_item.selector = selector
		adv_item.adv_item_type = adv_item_type
		adv_item.valid_selector = selector if valid_selector is None else valid_selector
		return adv_item

path_sep = '\\'

class LootTableMap():
	def __init__(self, selector: str, path: List[str], loot_table: LootTable):
		self.selector	= selector
		self.path		= path
		self.original	= loot_table
		self.is_loop	= False
		self.is_sub		= False

		self.remapped:			LootTable
		self.remap_selector:	str
		self.adv_chain:			List[AdvItem]
		self.adv_branches:		Dict[str, List[AdvItem]]
		self.branch_map:		Dict[str, int]
		self.valid_conditions:	Dict[eCondition, List[Condition]]

	@property
	def file_path(self) -> str:
		return path_sep.join(self.path)

	@property
	def contents(self) -> str:
		return json.dumps(self.remapped)


def create_adv_item(entry: Union[LootTableEntry, ItemEntry], loot_table_maps) -> AdvItem:
	selector = entry.name.replace('minecraft:', '').rsplit('/', 1).pop()
	if isinstance(entry, LootTableEntry):
		return AdvItem.populate(selector, eAdvItemType.reference)
	else:
		return AdvItem.populate(selector, eAdvItemType.item)


def fix_selector(adv_link: AdvItem, loot_table_map: LootTableMap):
	if loot_table_map.original.typ is eLootTable.block:
		prev_type = adv_link.adv_item_type
		adv_link.adv_item_type = eAdvItemType.special
		if loot_table_map.selector.startswith('potted'):
			adv_link.valid_selector = loot_table_map.selector.replace('potted_', '')		
		elif loot_table_map.selector in ['pumpkin_stem', 'attached_pumpkin_stem', 'melon_stem', 'attached_melon_stem']:
			adv_link.valid_selector = loot_table_map.selector.replace('attached_', '').replace('_stem', '_seeds')
		elif loot_table_map.selector in ['beetroots', 'carrots']:
			adv_link.valid_selector = loot_table_map.selector[:-1]
		elif loot_table_map.selector == 'potatoes':
			adv_link.valid_selector = 'potato'
		elif loot_table_map.selector == 'bamboo_sapling':
			adv_link.valid_selector = 'bamboo'
		elif loot_table_map.selector == 'cocoa':
			adv_link.valid_selector = 'cocoa_beans'
		elif loot_table_map.selector == 'frosted_ice':
			adv_link.valid_selector = 'ice'
		elif loot_table_map.selector == 'kelp_plant':
			adv_link.valid_selector = 'kelp'
		elif loot_table_map.selector == 'redstone_wire':
			adv_link.valid_selector = 'redstone'
		elif loot_table_map.selector == 'tripwire':
			adv_link.valid_selector = 'string'
		elif loot_table_map.selector == 'sweet_berry_bush':
			adv_link.valid_selector = 'sweet_berries'
		elif loot_table_map.selector == 'tall_seagrass':
			adv_link.valid_selector = 'seagrass'
		else:
			adv_link.adv_item_type = prev_type
	elif loot_table_map.original.typ is eLootTable.entity:
		if loot_table_map.selector == 'sheep' or 'sheep' in loot_table_map.path:
			adv_link.valid_selector = 'sheep_spawn_egg'
		elif loot_table_map.selector == 'ender_dragon':
			adv_link.valid_selector = 'dragon_head'
		elif loot_table_map.selector == 'giant':
			adv_link.valid_selector = 'zombie_head'
		elif loot_table_map.selector == 'illusioner':
			adv_link.valid_selector = 'pillager_spawn_egg'
		elif loot_table_map.selector == 'iron_golem':
			adv_link.valid_selector = 'pumpkin'
		elif loot_table_map.selector == 'snow_golem':
			adv_link.valid_selector = 'pumpkin'
		elif loot_table_map.selector == 'player':
			adv_link.valid_selector = 'player_head'
		elif loot_table_map.selector == 'wither':
			adv_link.valid_selector = 'wither_skeleton_skull'
		elif not loot_table_map.selector == 'armor_stand':
			adv_link.valid_selector = '{}_spawn_egg'.format(adv_link.selector)
	elif loot_table_map.original.typ is eLootTable.chest:
		adv_link.valid_selector = 'chest'
	elif loot_table_map.original.typ is eLootTable.fishing:
		adv_link.valid_selector = 'fishing_rod'
	elif loot_table_map.original.typ is eLootTable.advancement_reward:
		adv_link.valid_selector = 'entity'
	elif loot_table_map.original.typ is eLootTable.generic:
		adv_link.valid_selector = 'grass_block'
	elif loot_table_map.original.typ is eLootTable.gift:
		adv_link.valid_selector = 'poppy'


def populate_advancement_chain(root_selector: str, loot_table_maps: Dict[str, LootTableMap]):
	current_map = loot_table_maps[root_selector]

	current_map.adv_chain = []
	current_map.adv_branches = {}
	current_map.branch_map = {}
	advancement_chain = current_map.adv_chain
	advancement_branches = current_map.adv_branches
	branch_map = current_map.branch_map

	last_link = AdvItem.populate(root_selector, eAdvItemType.root)
	
	fix_selector(last_link, current_map)

	advancement_chain.append(last_link)

	count_to_next = 0
	last_branch_selector = None
	next_selector = root_selector
	build_chain = True
	while build_chain:
		entries = get_all_entries(current_map.remapped)
		found_link = False

		special_link = AdvItem.populate(current_map.remap_selector, eAdvItemType.block)
		fix_selector(special_link, loot_table_maps[current_map.remap_selector])
		if special_link.adv_item_type == eAdvItemType.special:
			last_link = special_link
			next_selector = current_map.remap_selector
			found_link = True

		for entry in entries:
			adv_item = create_adv_item(entry, loot_table_maps)
			if not found_link and adv_item.selector == current_map.remap_selector and adv_item.adv_item_type is eAdvItemType.item:
				last_link = adv_item
				adv_item.adv_item_type = eAdvItemType.block
				next_selector = current_map.remap_selector
				found_link = True
			else:
				if current_map.selector not in advancement_branches:
					advancement_branches[current_map.selector] = []

					if last_branch_selector is not None:
						branch_map[last_branch_selector] = count_to_next
					count_to_next = 0
					last_branch_selector = current_map.selector

				if adv_item.adv_item_type is eAdvItemType.reference:
					fix_selector(adv_item, loot_table_maps[adv_item.selector])
				advancement_branches[current_map.selector].append(adv_item)

		current_map = loot_table_maps[next_selector]
		count_to_next += 1

		if any(adv_link.selector == current_map.selector for adv_link in advancement_chain) or found_link is False:
			build_chain = False
			if last_branch_selector is not None:
				branch_map[last_branch_selector] = count_to_next

		if found_link is True:
			if build_chain == False:
				loot_table_maps[root_selector].is_loop = True
				last_link.adv_item_type = eAdvItemType.loop
			advancement_chain.append(last_link)


def validate_conditions(loot_table_map: LootTableMap):
	loot_table_map.valid_conditions = {}
	all_valid_conditions = get_all_conditions(loot_table_map.original)
	for valid in all_valid_conditions:
		loot_table_map.valid_conditions[valid.condition]
	all_remapped_conditions = get_all_conditions(loot_table_map.original)


