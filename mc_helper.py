from typing import Callable, List
from enum import Enum

def _dynamic_getter(key: str):
	def getter(self):
		return self[key]

	return getter

def _dynamic_setter(key: str):
	def setter(self, value):
		self[key] = value
	
	return setter


def _dynamic_deleter(key: str):
	def deleter(self):
		del self[key]
	
	return deleter

class _MCProperty(property):
	def __init__(self, key: str, init: Callable, getter: Callable, setter: Callable, deleter: Callable):
		super().__init__(getter, setter, deleter)
		self.key = key
		self.init = init

def mc_property(key: str, init: Callable) -> property:
	return _MCProperty(key, init, _dynamic_getter(key), _dynamic_setter(key), _dynamic_deleter(key))


def mc_list_property(key: str, init: Callable) -> property:
	list_init = lambda list_val: [init(v) for v in list_val]

	return _MCProperty(key, list_init, _dynamic_getter(key), _dynamic_setter(key), _dynamic_deleter(key))


def mc_dict_property(key: str, init: Callable) -> property:
	dict_init = lambda dict_val: { k: init(v) for k, v in dict_val.items() }

	return _MCProperty(key, dict_init, _dynamic_getter(key), _dynamic_setter(key), _dynamic_deleter(key))


class MCDict(dict):
	def __init__(self, json_dict: dict = None):
		if json_dict is None:
			return
			
		auto = []
		for value in self.__class__.__dict__.values():
			if isinstance(value, _MCProperty):
				if value.key in json_dict:
					self[value.key] = value.init(json_dict[value.key])
					auto.append(value.key)

		for value in self.__class__.__base__.__dict__.values():
			if isinstance(value, _MCProperty):
				if value.key in json_dict:
					self[value.key] = value.init(json_dict[value.key])
					auto.append(value.key)

		manual = []
		for key, value in json_dict.items():
			if key not in self:
				self[key] = value
				manual.append(key)

		pass


class eActionType(Enum):
	Interact = 0
	Set = 1
	Delete = 2

class eItemType(Enum):
	Entry = 0
	Condition = 1

class MCActionInfo():
	def __init__(self, item_type: eItemType, action: Callable, action_type: eActionType):
	 self.item_type:	eItemType	= item_type
	 self.action:		Callable	= action
	 self.action_type:	eActionType	= action_type
	 self.depth = 0
	 self.short_curcuit = False

class MCInteractable():
	def interact(self, info: MCActionInfo):
		pass

def interact_with_item(items, subscript, info):
	if info.short_curcuit == True:
		return
	action_result = info.action(items[subscript], info)
	if info.action_type == eActionType.Set and action_result:
		items[subscript] = action_result
		return False
	elif info.action_type == eActionType.Delete and action_result:
		del items[subscript]
		return False
		
	return True

def interact_with_items(parent, subscript, info: MCActionInfo):
	if info.short_curcuit == True:
		return
	items = parent[subscript]
	i = 0
	while i < len(items):
		interaction_result = interact_with_item(items, i, info)
		if info.short_curcuit == True:
			return
		if info.action_type != eActionType.Delete or interaction_result:
			if interaction_result:
				info.depth += 1
				items[i].interact(info)
				if info.short_curcuit == True:
					return
				info.depth -= 1
			i += 1
			
	if len(items) == 0:
		del parent[subscript]


def interact_with_subitems(items: List[MCInteractable], info: MCActionInfo):
	if info.short_curcuit == True:
		return
	for item in items:
		info.depth += 1
		item.interact(info)
		if info.short_curcuit == True:
			return
		info.depth -= 1




