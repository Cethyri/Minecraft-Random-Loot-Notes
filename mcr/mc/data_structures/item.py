from typing import Union

from mcr.json_dict import JsonDict
from mcr.mc.data_structures.range import IntRange, init_int_or_range

from mcr.mc.data_structures.enchantment import Enchantment


class Item(JsonDict, overrides={'count': init_int_or_range, 'durability': init_int_or_range}):
    count:			Union[IntRange, int]
    durability:		Union[IntRange, int]
    enchantments:	list[Enchantment]
    item_id:		str
    nbt:			str
    potion:			str
    tag:			str
