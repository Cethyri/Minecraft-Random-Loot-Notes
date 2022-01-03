from enum import Enum, auto
import os
from typing import Optional

from mcr.json_dict import JsonDict
from mcr.mc.data_structures.display import eFrame
from mcr.mc.data_structures.loot_table import LootTable


class eAdvItemType(Enum):
    root = auto()
    block = auto()
    root_table = auto()
    reference = auto()
    loop = auto()
    from_items = auto()
    item = auto()
    tab = auto()

    @property
    def frame(self) -> eFrame:
        if self in [eAdvItemType.root, eAdvItemType.block]:
            return eFrame.task
        if self in [eAdvItemType.root_table, eAdvItemType.reference, eAdvItemType.loop, eAdvItemType.from_items]:
            return eFrame.goal
        if self in [eAdvItemType.item, eAdvItemType.tab]:
            return eFrame.challenge

        raise Exception('Item type does not have a corresponding frame.')


class AdvItem(JsonDict):
    name:		    str
    item_name:	    str
    adv_item_type:	eAdvItemType
    title:			Optional[str]
    description:	Optional[str]

    def __init__(self, name: str, adv_item_type: eAdvItemType, item_name: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None):
        self.name = name
        self.adv_item_type = adv_item_type
        self.item_name = name if item_name is None else item_name
        self.title = title
        self.description = description

    @property
    def frame(self):
        return self.adv_item_type.frame


class RandomizerTemplate():
    path:       list[str]
    """A list of directories that make up the filepath of the original loot table"""
    
    original:   LootTable
    """the original contents of the file"""
    name:       str
    target:         LootTable
    target_name:    str

    adv_chain:      list[AdvItem]
    adv_branches:   dict[str, list[AdvItem]]
    branch_map:     dict[str, int]

    is_loop:    bool = False
    is_sub:     bool = False
    adv_length: float = 0

    def __init__(self, name: str, path: list[str], loot_table: LootTable):
        self.adv_chain = []
        self.adv_branches = {}
        self.branch_map = {}
        self.name = name
        self.path = path
        self.original = loot_table

    @property
    def file_path(self) -> str:
        return os.path.sep.join(self.path)
