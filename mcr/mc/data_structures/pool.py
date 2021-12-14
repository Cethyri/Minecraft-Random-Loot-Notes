from typing import Union

from mcr.json_dict import JsonDict
from mcr.interactable import Interactable

from mcr.mc.data_structures.entry import Entry
from mcr.mc.data_structures.condition import Condition
from mcr.mc.data_structures.function import Function
from mcr.mc.data_structures.range import IntRange, FloatRange


class Pool(JsonDict, Interactable):
    conditions:		list[Condition]
    rolls:			Union[int, IntRange]
    bonus_rolls:	Union[float, FloatRange]
    entries:		list[Entry]
    functions:      list[Function]
