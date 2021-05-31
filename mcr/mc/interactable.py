from abc import ABC, abstractmethod
from re import sub
from typing import Any, Callable, Generic, List, TypeVar, Union, overload
from enum import Enum


class eActionType(Enum):
    Get = 0
    Set = 1
    Del = 2

T = TypeVar('T')

class MCActionInfo(Generic[T]):
    def __init__(self, item_type: type[T], action: Callable[[Any, 'MCActionInfo[Any]'], T], action_type: eActionType):
        self.item_type:     type[T] = item_type
        self.action:        Callable[[Any, 'MCActionInfo[Any]'], Any] = action
        self.action_type:	eActionType = action_type
        self.depth:         int = 0
        self.short_circuit: bool = False


class MCInteractable(ABC):
    @abstractmethod
    def interact(self, info: MCActionInfo[Any]):
        pass

def _get(parent: Union[list[T], dict[str, T]], subscript: Union[int, str]) -> T:
    if (isinstance(parent, list) and isinstance(subscript, int)):
        return parent[subscript]
    elif (isinstance(parent, dict) and isinstance(subscript, str)):
        return parent[subscript]
    else:
        raise Exception('Subscript does not match parent type.')

def _set(parent: Union[list[T], dict[str, T]], subscript: Union[int, str], value: T):
    if (isinstance(parent, list) and isinstance(subscript, int)):
        parent[subscript] = value
    elif (isinstance(parent, dict) and isinstance(subscript, str)):
        parent[subscript] = value
    else:
        raise Exception('Subscript does not match parent type.')

def _del(parent: Union[list[T], dict[str, T]], subscript: Union[int, str]):
    if (isinstance(parent, list) and isinstance(subscript, int)):
        del parent[subscript]
    elif (isinstance(parent, dict) and isinstance(subscript, str)):
        del parent[subscript]
    else:
        raise Exception('Subscript does not match parent type.')

interactable = TypeVar('interactable', bound=MCInteractable)

@overload
def interact_with_item(items: list[MCInteractable], subscript: int, info: MCActionInfo[Any]):
    pass

@overload
def interact_with_item(items: dict[str, MCInteractable], subscript: str, info: MCActionInfo[Any]):
    pass

def interact_with_item(items: Union[list[MCInteractable], dict[str, MCInteractable]], subscript: Union[int, str], info: MCActionInfo[Any]):
    if info.short_circuit:
        return
    action_result = info.action(_get(items, subscript), info)
    if info.action_type == eActionType.Set and action_result:
        _set(items, subscript, action_result)
        return False
    elif info.action_type == eActionType.Del and action_result:
        _del(items, subscript)
        return False

    return True

@overload
def interact_with_items(parent: dict[str, list[MCInteractable]], subscript: str, info: MCActionInfo[Any]):
    pass

@overload
def interact_with_items(parent: list[list[MCInteractable]], subscript: int, info: MCActionInfo[Any]):
    pass

def interact_with_items(parent: Union[list[list[MCInteractable]], dict[str, list[MCInteractable]]], subscript: Union[int, str], info: MCActionInfo[Any]):
    # if info.short_circuit:
    #     return

    items = _get(parent, subscript)

    i = 0
    while i < len(items):
        interaction_result = interact_with_item(items, i, info)
        # if info.short_circuit:
        #     return
        if info.action_type != eActionType.Del or interaction_result:
            if interaction_result:
                info.depth += 1
                items[i].interact(info)
                # if info.short_circuit:
                #     return
                info.depth -= 1
            i += 1

    if len(items) == 0:
        _del(parent, subscript)


def interact_with_subitems(items: List[interactable], info: MCActionInfo[Any]):
    # if info.short_circuit:
    #     return
    for item in items:
        info.depth += 1
        item.interact(info)
        # if info.short_circuit:
        #     return
        info.depth -= 1
