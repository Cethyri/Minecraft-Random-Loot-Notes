from typing import Union, List

from mc_helper import MCDict, mc_obj, mc_list, mc_multi
from mc_range import IntRange, init_int_or_range

from enchantment import Enchantment

class Item(MCDict):
	count: Union[IntRange, int] = mc_multi('count', Union[IntRange, int], init_int_or_range)
	durability: Union[IntRange, int] = mc_multi('durability', Union[IntRange, int], init_int_or_range)
	enchantments: List[Enchantment] = mc_list('enchantments', Enchantment)
	item_id: str = mc_obj('item', str)
	nbt: str = mc_obj('nbt', str)
	potion: str = mc_obj('potion', str)
	tag: str = mc_obj('tag', str)

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