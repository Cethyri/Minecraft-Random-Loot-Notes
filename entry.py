from typing import List, Union, NewType
from enum import Enum

from mc_helper import MCDict, mc_obj, mc_list, mc_multi_list

from condition import Condition
from function import Function

class eEntry(str, Enum):
	item			= 'minecraft:item'
	tag				= 'minecraft:tag'
	loot_table		= 'minecraft:loot_table'
	group			= 'minecraft:group'
	alternatives	= 'minecraft:alternatives'
	sequence		= 'minecraft:sequence'
	dynamic			= 'minecraft:dynamic'
	empty			= 'minecraft:empty'

class eDynamic(str, Enum):
	contents = 'minecraft:contents'
	dyn_self = 'minecraft:self'


class Entry(MCDict):
	conditions:	List[Condition]	= mc_multi_list('conditions', Condition, Condition.create)
	typ:		eEntry			= mc_obj('type', eEntry)
	weight:		int				= mc_obj('weight', int)
	quality:	int				= mc_obj('quality', int)

	@staticmethod
	def create(json_body):
		typ = json_body['type']

		if typ == eEntry.item:
			return ItemEntry(json_body)

		elif typ == eEntry.tag:
			return TagEntry(json_body)

		elif typ == eEntry.loot_table:
			return LootTableEntry(json_body)

		elif typ == eEntry.group:
			return GroupEntry(json_body)

		elif typ == eEntry.alternatives:
			return AlternativesEntry(json_body)

		elif typ == eEntry.sequence:
			return SequenceEntry(json_body)

		elif typ == eEntry.dynamic:
			return DynamicEntry(json_body)

		else:
			return Entry(json_body)


class ItemEntry(Entry):
	name:		str				= mc_obj('name', str)
	functions:	List[Function]	= mc_multi_list('functions', Function, Function.create)

class TagEntry(Entry):
	name:	str		= mc_obj('name', str)
	expand:	bool	= mc_obj('expand', bool)

class LootTableEntry(Entry):
	name: str = mc_obj('name', str)

class GroupEntry(Entry):
	children: List[Entry] = mc_multi_list('children', Entry, Entry.create)

class AlternativesEntry(Entry):
	children: List[Entry] = mc_multi_list('children', Entry, Entry.create)

class SequenceEntry(Entry):
	children: List[Entry] = mc_multi_list('children', Entry, Entry.create)

class DynamicEntry(Entry):
	name: eDynamic = mc_obj('name', eDynamic)