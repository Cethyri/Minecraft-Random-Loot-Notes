from typing import List, Dict

from loot_table import LootTable

from dict_helper import get_all_entries


class LootTableMap():
	def __init__(self, selector: str, path: List[str], loot_table: LootTable):
		self.selector = selector
		self.path = path
		self.original = loot_table

		self.remapped:			LootTable
		self.remap_selector:	str
		self.adv_chain:			List[str]
		self.adv_branches:		Dict[str]


def populate_advancement_chain(selector: str, loot_table_maps: Dict[str, LootTableMap]):
	loot_table_map = loot_table_maps[selector]
	next_selector = selector
	loot_table_map.adv_chain = []
	loot_table_map.adv_branches = {}
	advancement_chain: list = loot_table_map.adv_chain
	advancement_branches: dict = loot_table_map.adv_branches
	while True:
		advancement_chain.append(next_selector)
		items = get_all_entries(loot_table_map.remapped)

		if loot_table_maps[loot_table_map.remap_selector].original.typ != 'minecraft:block':
			advancement_chain.append('loot_table:{}'.format(loot_table_map.remap_selector))
		else:
			for i in range(len(items)):
				if isinstance(items[i], str) and items[i] == loot_table_map.remap_selector:
					next_selector = items[i]
					del items[i]
					break

		if len(items) > 0:
			advancement_branches[loot_table_map.selector] = items

		loot_table_map = loot_table_maps[next_selector]

		if loot_table_map.selector in advancement_chain:
			break

