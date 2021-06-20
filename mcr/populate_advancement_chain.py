from mcr.fix_name import fix_name
from mcr.loot_table_map import AdvItem, LootTableMap, eAdvItemType
from typing import Any, Union

from mcr.interactable import ActionInfo, ActionResult, eActionType
from mcr.mc.data_structures.entry import Entry, ItemEntry, LootTableEntry
from mcr.mc.data_structures.function import eFunction
from mcr.mc.data_structures.loot_table import eLootTable

def create_adv_item(entry: Union[LootTableEntry, ItemEntry], _: dict[str, LootTableMap]) -> AdvItem:
    name = entry.name.replace('minecraft:', '').rsplit('/', 1).pop()
    if isinstance(entry, LootTableEntry):
        return AdvItem(name, eAdvItemType.reference)

    return AdvItem(name, eAdvItemType.item)


def populate_advancement_chain(root_name: str, loot_table_maps: dict[str, LootTableMap]):
    current_map = loot_table_maps[root_name]

    current_map.adv_chain = []
    current_map.adv_branches = {}
    current_map.branch_map = {}
    advancement_chain: list[AdvItem] = current_map.adv_chain
    advancement_branches: dict[str, list[AdvItem]] = current_map.adv_branches
    branch_map: dict[str, int] = current_map.branch_map

    last_link = AdvItem(root_name, eAdvItemType.root)

    fix_name(last_link, current_map)

    advancement_chain.append(last_link)

    count_to_next = 0
    last_branch_name = None
    next_name = root_name
    build_chain = True

    entries: list[Union[ItemEntry, LootTableEntry]]

    def collect(entry: Entry, _: ActionInfo[Any]):
        if isinstance(entry, (ItemEntry, LootTableEntry)) and not any(entry.name == e.name and entry.type_ is e.type_ for e in entries):
            entries.append(entry)
        return ActionResult.NoAction()

    while build_chain:
        entries = []
        current_map.remapped.interact(ActionInfo(
            Entry, collect, eActionType.Get))
        found_link = False

        from_items_link = AdvItem(
            current_map.remap_name, eAdvItemType.root)
        fix_name(from_items_link,
                     loot_table_maps[current_map.remap_name])
        if from_items_link.adv_item_type == eAdvItemType.from_items:
            last_link = from_items_link
            next_name = current_map.remap_name
            found_link = True

        for entry in entries:
            adv_item = create_adv_item(entry, loot_table_maps)
            if entry.name == 'minecraft:book' and isinstance(entry, ItemEntry) and 'functions' in entry and any((func.function is eFunction.enchant_randomly or func.function is eFunction.enchant_with_levels) for func in entry.functions):
                adv_item.name = 'enchanted_book'
                adv_item.item_name = 'enchanted_book'

            if not found_link and adv_item.name == current_map.remap_name and adv_item.adv_item_type is eAdvItemType.item and loot_table_maps[adv_item.name].original.type_ is eLootTable.block:
                last_link = adv_item
                adv_item.adv_item_type = eAdvItemType.block
                fix_name(adv_item, loot_table_maps[adv_item.name])
                next_name = current_map.remap_name
                found_link = True
            else:
                if current_map.name not in advancement_branches:
                    advancement_branches[current_map.name] = []

                    if last_branch_name is not None:
                        branch_map[last_branch_name] = count_to_next
                    count_to_next = 0
                    last_branch_name = current_map.name

                if adv_item.adv_item_type is eAdvItemType.reference:
                    fix_name(adv_item, loot_table_maps[adv_item.name])
                advancement_branches[current_map.name].append(adv_item)

        current_map = loot_table_maps[next_name]
        count_to_next += 1

        if any(adv_link.name == current_map.name for adv_link in advancement_chain) or found_link is False:
            build_chain = False
            if last_branch_name is not None:
                branch_map[last_branch_name] = count_to_next

        if found_link is True:
            if not build_chain:
                loot_table_maps[root_name].is_loop = True
                last_link.adv_item_type = eAdvItemType.loop
                if current_map.name not in advancement_branches:
                    advancement_branches[current_map.name] = []
                advancement_branches[current_map.name].append(last_link)
            else:
                advancement_chain.append(last_link)
