from typing import Callable, List
from enum import Enum


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