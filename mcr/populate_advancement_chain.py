from dataclasses import dataclass
from typing import Optional, Union

from mcr.fix_name import create_and_fix_name, fix_name
from mcr.interactable import ActionInfo, ActionResult, eActionType
from mcr.loot_table_map import AdvItem, LootTableMap, eAdvItemType
from mcr.mc.data_structures.entry import Entry, ItemEntry, LootTableEntry
from mcr.mc.data_structures.function import eFunction
from mcr.mc.data_structures.loot_table import eLootTable


def create_adv_item(entry: Union[LootTableEntry, ItemEntry], _: dict[str, LootTableMap]) -> AdvItem:
    name = entry.name.replace('minecraft:', '').rsplit('/', 1).pop()
    if isinstance(entry, LootTableEntry):
        return AdvItem(name, eAdvItemType.reference)

    return AdvItem(name, eAdvItemType.item)


def collect(entry: Entry, entries: list[Union[ItemEntry, LootTableEntry]]):
    if isinstance(entry, (ItemEntry, LootTableEntry)) and not any(entry.name == e.name and entry.type_ is e.type_ for e in entries):
        entries.append(entry)
    return ActionResult.NoAction()


@dataclass
class AdvChainInfo:
    last_link: AdvItem
    last_branch_name: Optional[str]

    next_name: str
    count_to_next: int

    found_link: bool


def populate_advancement_chain(root_name: str, loot_table_maps: dict[str, LootTableMap]):
    root_map: LootTableMap = loot_table_maps[root_name]
    build_chain: bool = True
    entries: list[ItemEntry | LootTableEntry]
    current_map: LootTableMap = root_map

    chain_info = AdvChainInfo(
        last_link = create_and_fix_name(root_name, eAdvItemType.root, loot_table_maps),
        last_branch_name = None,
        next_name = root_name,
        count_to_next = 0,
        found_link = False
    )

    root_map.adv_chain.append(chain_info.last_link)

    while build_chain:
        entries = []
        chain_info.found_link = False

        current_map.target.interact(ActionInfo(
            Entry, lambda entry, _: collect(entry, entries), eActionType.Get))

        from_items_link = create_and_fix_name(current_map.target_name, eAdvItemType.root, loot_table_maps)

        if from_items_link.adv_item_type == eAdvItemType.from_items:
            chain_info.last_link = from_items_link
            chain_info.next_name = current_map.target_name
            chain_info.found_link = True

        for entry in entries:
            handle_adv_item(entry, current_map, root_map, chain_info, loot_table_maps)

        current_map = loot_table_maps[chain_info.next_name]
        chain_info.count_to_next += 1

        if any(adv_link.name == current_map.name for adv_link in current_map.adv_chain) or not chain_info.found_link:
            build_chain = False
            if chain_info.last_branch_name is not None:
                root_map.branch_map[chain_info.last_branch_name] = chain_info.count_to_next

        if chain_info.found_link:
            if build_chain:
                root_map.adv_chain.append(chain_info.last_link)
            else:
                root_map.is_loop = True
                chain_info.last_link.adv_item_type = eAdvItemType.loop
                if current_map.name not in root_map.adv_branches:
                    root_map.adv_branches[current_map.name] = []
                root_map.adv_branches[current_map.name].append(chain_info.last_link)


def handle_adv_item(entry: Union[ItemEntry, LootTableEntry], current_map: LootTableMap, root_map: LootTableMap, chain_info: AdvChainInfo, loot_table_maps: dict[str, LootTableMap]):
    adv_item = create_adv_item(entry, loot_table_maps)
    if entry.name == 'minecraft:book' and isinstance(entry, ItemEntry) and 'functions' in entry and any((func.function is eFunction.enchant_randomly or func.function is eFunction.enchant_with_levels) for func in entry.functions):
        adv_item.name = 'enchanted_book'
        adv_item.item_name = 'enchanted_book'

    if not chain_info.found_link and adv_item.name == current_map.target_name and adv_item.adv_item_type is eAdvItemType.item and loot_table_maps[adv_item.name].original.type_ is eLootTable.block:
        chain_info.last_link = adv_item
        adv_item.adv_item_type = eAdvItemType.block
        fix_name(adv_item, loot_table_maps[adv_item.name])
        chain_info.next_name = current_map.target_name
        chain_info.found_link = True
    else:
        if current_map.name not in root_map.adv_branches:
            root_map.adv_branches[current_map.name] = []

            if chain_info.last_branch_name is not None:
                root_map.branch_map[chain_info.last_branch_name] = chain_info.count_to_next
            chain_info.count_to_next = 0
            chain_info.last_branch_name = current_map.name

        if adv_item.adv_item_type is eAdvItemType.reference:
            fix_name(adv_item, loot_table_maps[adv_item.name])

        root_map.adv_branches[current_map.name].append(adv_item)