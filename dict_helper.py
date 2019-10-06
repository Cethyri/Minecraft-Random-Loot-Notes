from typing import Callable, List

from loot_table import LootTable
from entry import Entry, eEntry, EItem, ELootTable

def find_structures_with_parent(table: dict, is_match: Callable) -> list:
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


def find_structures(table: dict, is_match: Callable) -> list:
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
	return isinstance(struct, (EItem, ELootTable))


def get_all_entries(table: LootTable) -> list:
	if 'pools' not in table:
		return []

	pools = table.pools
	items = []
	for pool in pools:
		for entry in pool.entries:
			structures = find_structures(
				entry,
				matches_item_or_loot_table
			)

			for structure in structures:
				if isinstance(structure, ELootTable):
					selector = 'loot_table:{}'.format(structure.name.split('/').pop())
				elif isinstance(structure, EItem):
					selector = structure.name.replace('minecraft:', '')

				if selector not in items:
						items.append(selector)
	return items