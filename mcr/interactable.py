from abc import ABC
from typing import Any, Callable, Generic, TypeVar, Union
from enum import Enum
from dataclasses import dataclass


class eActionType(Enum):
    Get = 0
    Set = 1
    Del = 2


T = TypeVar('T')


@dataclass
class ActionResult(Generic[T]):
    value: Union[None, T, bool]
    result: eActionType

    @staticmethod
    def NoAction():
        return ActionResult[Any](None, eActionType.Get)


@dataclass
class ActionInfo(Generic[T]):
    item_type:      type[T]
    action:         Callable[[Any, 'ActionInfo[Any]'], ActionResult[T]]
    action_type:	eActionType


class Interactable(ABC, dict[str, Any]):
    def interact(self, info: ActionInfo[Any]):
        for key in list(self.keys()):
            interact_with_item(self, key, info)


def interact_with_item(items: Union[dict[str, Any], list[Any]], subscript: Any, info: ActionInfo[Any]) -> bool:
    item = items[subscript]
    if isinstance(item, info.item_type):
        action_result = info.action(items[subscript], info)
        if action_result.result != eActionType.Get:
            if action_result.result == eActionType.Set:
                items[subscript] = action_result.value
            else:
                del items[subscript]
            return False

    if isinstance(item, list):
        interact_with_items(items, subscript, info)

    if isinstance(item, Interactable):
        item.interact(info)

    return True


def interact_with_items(parent: Union[dict[str, list[Any]], list[list[Any]]], subscript: Any, info: ActionInfo[Any]):
    items = parent[subscript].copy()

    for item in items:
        interact_with_item(parent[subscript],
                           parent[subscript].index(item), info)

    if len(parent[subscript]) == 0:
        del parent[subscript]
