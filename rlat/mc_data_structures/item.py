from typing import Union, List

from mc_helper import MCDict, mc_property, mc_list_property
from mc_range import IntRange, init_int_or_range

from enchantment import Enchantment

class Item(MCDict):
	count:			Union[IntRange, int]	= mc_property('count', init_int_or_range)
	durability:		Union[IntRange, int]	= mc_property('durability', init_int_or_range)
	enchantments:	List[Enchantment]		= mc_list_property('enchantments', Enchantment)
	item_id:		str						= mc_property('item', str)
	nbt:			str						= mc_property('nbt', str)
	potion:			str						= mc_property('potion', str)
	tag:			str						= mc_property('tag', str)

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