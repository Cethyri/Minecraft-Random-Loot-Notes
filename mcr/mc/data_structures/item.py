from typing import Union, List

from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic, mc_list
from mcr.mc.data_structures.range import IntRange, init_int_or_range

from mcr.mc.data_structures.enchantment import Enchantment

class Item(MCDict):
	count:			Union[IntRange, int]	= mc_basic('count', init_int_or_range)
	durability:		Union[IntRange, int]	= mc_basic('durability', init_int_or_range)
	enchantments:	List[Enchantment]		= mc_list('enchantments', Enchantment)
	item_id:		str						= mc_basic('item', str)
	nbt:			str						= mc_basic('nbt', str)
	potion:			str						= mc_basic('potion', str)
	tag:			str						= mc_basic('tag', str)

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