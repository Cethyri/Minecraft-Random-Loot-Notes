from typing import List, Union

from mcr.mc.properties import JsonDict
from mcr.mc.interactable import MCInteractable, MCActionInfo, eItemType, interact_with_subitems, interact_with_items

from mcr.mc.data_structures.entry import Entry
from mcr.mc.data_structures.condition import Condition
from mcr.mc.data_structures.range import IntRange, FloatRange, init_int_or_range, init_float_or_range


class Pool(JsonDict, MCInteractable, overrides={'rolls': init_int_or_range, 'bonus_rolls': init_float_or_range}):
    conditions:		List[Condition]
    rolls:			Union[IntRange, int]
    bonus_rolls:	Union[FloatRange, float]
    entries:		List[Entry]

    def interact(self, info: MCActionInfo):
        if info.item_type == eItemType.Entry and 'entries' in self:
            interact_with_items(self, 'entries', info)

        elif info.item_type == eItemType.Condition:
            if 'conditions' in self:
                interact_with_items(self, 'conditions', info)
            if 'entries' in self:
                interact_with_subitems(self.entries, info)
