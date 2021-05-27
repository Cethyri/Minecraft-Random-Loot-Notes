from typing import Any, List
from enum import Enum

from mcr.mc.properties import JsonDict, SpecialInit
from mcr.mc.interactable import MCInteractable, MCActionInfo, eItemType, eActionType, interact_with_items, interact_with_subitems

from mcr.mc.data_structures.condition import Condition
from mcr.mc.data_structures.function import Function


class eEntry(str, Enum):
    item = 'minecraft:item'
    tag = 'minecraft:tag'
    loot_table = 'minecraft:loot_table'
    group = 'minecraft:group'
    alternatives = 'minecraft:alternatives'
    sequence = 'minecraft:sequence'
    dynamic = 'minecraft:dynamic'
    empty = 'minecraft:empty'


class eDynamic(str, Enum):
    contents = 'minecraft:contents'
    self_ = 'minecraft:self'


class Entry(JsonDict, MCInteractable, SpecialInit, overrides={'type_': 'type'}):
    conditions:	List[Condition]
    type_:		eEntry
    weight:		int
    quality:	int

    def interact(self, info: MCActionInfo):
        if info.item_type == eItemType.Entry and 'children' in self:
            interact_with_items(self, 'children', info)

        elif info.item_type == eItemType.Condition:
            if 'conditions' in self:
                interact_with_items(self, 'conditions', info)
            if 'children' in self:
                interact_with_subitems(self['children'], info)
                if info.action_type is eActionType.Delete and self.type_ is eEntry.alternatives and not any('conditions' in child for child in self['children']):
                    self.type_ = eEntry.group
            if 'functions' in self:
                interact_with_subitems(self['functions'], info)

    @staticmethod
    def create(value: dict[str, Any]):
        type_ = value['type']

        if type_ == eEntry.item:
            return ItemEntry(value)

        elif type_ == eEntry.tag:
            return TagEntry(value)

        elif type_ == eEntry.loot_table:
            return LootTableEntry(value)

        elif type_ == eEntry.group:
            return GroupEntry(value)

        elif type_ == eEntry.alternatives:
            return AlternativesEntry(value)

        elif type_ == eEntry.sequence:
            return SequenceEntry(value)

        elif type_ == eEntry.dynamic:
            return DynamicEntry(value)

        else:
            return Entry(value)


class ItemEntry(Entry):
    name:		str
    functions:	List[Function]


class TagEntry(Entry):
    name:	str
    expand:	bool


class LootTableEntry(Entry):
    name: str


class GroupEntry(Entry):
    children: List[Entry]


class AlternativesEntry(Entry):
    children: List[Entry]


class SequenceEntry(Entry):
    children: List[Entry]


class DynamicEntry(Entry):
    name: eDynamic
