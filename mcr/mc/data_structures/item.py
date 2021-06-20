from typing import Union

from mcr.json_dict import JsonDict
from mcr.mc.data_structures.range import IntRange

from mcr.mc.data_structures.enchantment import Enchantment


class Item(JsonDict):
    count:			Union[int, IntRange]
    durability:		Union[int, IntRange]
    enchantments:	list[Enchantment]
    item_id:		str
    nbt:			str
    potion:			str
    tag:			str
