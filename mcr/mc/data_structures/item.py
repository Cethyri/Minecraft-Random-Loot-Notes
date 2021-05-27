from typing import Union, List

from mcr.mc.properties import JsonDict
from mcr.mc.data_structures.range import IntRange, init_int_or_range

from mcr.mc.data_structures.enchantment import Enchantment


class Item(JsonDict, overrides={'count': init_int_or_range, 'durability': init_int_or_range}):
    count:			Union[IntRange, int]
    durability:		Union[IntRange, int]
    enchantments:	List[Enchantment]
    item_id:		str
    nbt:			str
    potion:			str
    tag:			str

    @staticmethod
    def populate(count: Union[IntRange, int] = None, durability: Union[IntRange, int] = None, enchantments: List[Enchantment] = None, item_id: str = None, nbt: str = None, potion: str = None, tag: str = None):
        item = Item()
        if count is not None:
            item.count = count
        if durability is not None:
            item.durability = durability
        if enchantments is not None:
            item.enchantments = enchantments
        if item is not None:
            item.item_id = item_id
        if nbt is not None:
            item.nbt = nbt
        if potion is not None:
            item.potion = potion
        if tag is not None:
            item.tag = tag

        return item
