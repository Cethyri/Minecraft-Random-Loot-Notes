from enum import Enum, auto
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
    selector:		str
    item_selector:	str
    adv_item_type:	eAdvItemType
    title:			Optional[str]
    description:	Optional[str]

    def __init__(self, selector: str, adv_item_type: eAdvItemType, item_selector: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None):
        self.selector = selector
        self.adv_item_type = adv_item_type
        self.item_selector = selector if item_selector is None else item_selector
        self.title = title
        self.description = description

    @property
    def frame(self):
        return self.adv_item_type.frame


class LootTableMap():
    remapped:       LootTable
    remap_selector: str
    adv_chain:      list[AdvItem]
    adv_branches:   dict[str, list[AdvItem]]
    branch_map:     dict[str, int]

    selector: str
    path: list[str]
    original: LootTable
    is_loop: bool
    is_sub: bool
    adv_length: float

    def __init__(self, selector: str, path: list[str], loot_table: LootTable):
        self.selector = selector
        self.path = path
        self.original = loot_table

        self.is_loop = False
        self.is_sub = False
        self.adv_length = 0

    @property
    def file_path(self) -> str:
        return '\\'.join(self.path)
