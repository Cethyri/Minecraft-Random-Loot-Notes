from typing import Callable, List, TypeVar, Union

from loot_table import LootTable
from entry import Entry, eEntry, ItemEntry, LootTableEntry
from condition import Condition, eCondition


T = TypeVar('T')

def find_type_with_parents(table: dict, typ: T) -> List[T]:
	root = {
		'parent': None,
		'structure': table
	}
	search_queue = [root]
	structures = [root] if isinstance(table, typ) else []

	while(len(search_queue) > 0):
		current = search_queue.pop()

		for value in (current['structure'] if isinstance(current['structure'], list) else current['structure'].values()):
			struc_with_parent = {
				'parent': current,
				'structure': value
			}
			if isinstance(value, typ):
				structures.append(struc_with_parent)

			if isinstance(value, [list, dict]):
				search_queue.append(struc_with_parent)

	return structures

def find_type_in(table: dict, typ: T) -> List[T]:
	search_queue = [table]
	structures = [table] if isinstance(table, typ) else []

	while(len(search_queue) > 0):
		current = search_queue.pop()

		for value in (current if isinstance(current, list) else current.values()):
			if isinstance(value, typ):
				structures.append(value)

			if isinstance(value, (list, dict)):
				search_queue.append(value)

	return structures

def get_all_entries(table: LootTable) -> List[Union[LootTableEntry, ItemEntry]]:
	if 'pools' not in table:
		return []

	pools = table.pools
	entries: List[Entry] = []
	for pool in pools:
		for entry in pool.entries:
			structures = find_type_in(
				entry,
				(ItemEntry, LootTableEntry)
			)

			for structure in structures:
				if not any(e.name == structure.name for e in entries):
					entries.append(structure)
	return entries

def get_all_conditions(table: LootTable) -> List[Condition]:
	if 'pools' not in table:
		return []

	pools = table.pools
	conditions: List[Condition] = []
	for pool in pools:
		structures = find_type_in(
			pool,
			Condition
		)

		for structure in structures:
			if structure not in conditions:
				conditions.append(structure)
				
	return conditions