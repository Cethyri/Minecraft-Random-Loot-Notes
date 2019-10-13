from typing import List, Union, Callable
from enum import Enum

from mc_helper import MCDict, mc_property, mc_list_property, MCInteractable, MCActionInfo, eItemType, eActionType, interact_with_items, interact_with_subitems

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


class Entry(MCDict, MCInteractable):
	conditions:	List[Condition]	= mc_list_property('conditions', Condition.create)
	typ:		eEntry			= mc_property('type', eEntry)
	weight:		int				= mc_property('weight', int)
	quality:	int				= mc_property('quality', int)

	def interact(self, info: MCActionInfo):
		if info.item_type == eItemType.Entry and 'children' in self:
			interact_with_items(self, 'children', info)

		elif info.item_type == eItemType.Condition:
			if 'conditions' in self:
				interact_with_items(self, 'conditions', info)
			if 'children' in self:
				interact_with_subitems(self['children'], info)
				if info.action_type is eActionType.Delete and self.typ is eEntry.alternatives and not any('conditions' in child for child in self['children']):
					self.typ = eEntry.group
			if 'functions' in self:
				interact_with_subitems(self['functions'], info)

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
	name:		str				= mc_property('name', str)
	functions:	List[Function]	= mc_list_property('functions', Function.create)

class TagEntry(Entry):
	name:	str		= mc_property('name', str)
	expand:	bool	= mc_property('expand', bool)

class LootTableEntry(Entry):
	name: str = mc_property('name', str)

class GroupEntry(Entry):
	children: List[Entry] = mc_list_property('children', Entry.create)

class AlternativesEntry(Entry):
	children: List[Entry] = mc_list_property('children', Entry.create)

class SequenceEntry(Entry):
	children: List[Entry] = mc_list_property('children', Entry.create)

class DynamicEntry(Entry):
	name: eDynamic = mc_property('name', eDynamic)


a = property()