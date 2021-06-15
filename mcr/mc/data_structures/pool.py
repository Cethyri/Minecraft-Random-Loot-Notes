from typing import List, Union

from mcr.json_dict import JsonDict
from mcr.interactable import Interactable

from mcr.mc.data_structures.entry import Entry
from mcr.mc.data_structures.condition import Condition
from mcr.mc.data_structures.range import IntRange, FloatRange, init_int_or_range, init_float_or_range


class Pool(JsonDict, Interactable, overrides={'rolls': init_int_or_range, 'bonus_rolls': init_float_or_range}):
    conditions:		List[Condition]
    rolls:			Union[IntRange, int]
    bonus_rolls:	Union[FloatRange, float]
    entries:		List[Entry]
