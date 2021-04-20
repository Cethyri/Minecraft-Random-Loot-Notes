import json
import random

from typing import List, Dict, Union, Iterable
from enum import Enum

from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic
from mcr.mc.interactable import MCActionInfo, eItemType, eActionType

from mcr.mc.data_structures.loot_table import LootTable, eLootTable
from mcr.mc.data_structures.entry import Entry, ItemEntry, LootTableEntry, eEntry
from mcr.mc.data_structures.display import eFrame
from mcr.mc.data_structures.condition import Condition, eCondition, eRestriction, get_restriction_level
from mcr.mc.data_structures.display import eFrame
from mcr.mc.data_structures.function import eFunction

from mcr.helpers.regex import get_upper_selector

class eAdvItemType(str, Enum):
    root		= 'root'
    block		= 'block'
    root_table	= 'root_table'
    reference	= 'reference'
    loop		= 'loop'
    from_items	= 'from_items'
    item		= 'item'
    tab			= 'tab'

    def get_frame(self):
        if self is eAdvItemType.root or self is eAdvItemType.block:
            return eFrame.task
        if self is eAdvItemType.root_table or self is eAdvItemType.reference or self is eAdvItemType.loop or self is eAdvItemType.from_items:
            return eFrame.goal
        if self is eAdvItemType.item or self is eAdvItemType.tab:
            return eFrame.challenge



class AdvItem(dict):
    selector:		str				= mc_basic('selector', str)
    item_selector:	str				= mc_basic('item_selector', str)
    adv_item_type:	eAdvItemType	= mc_basic('adv_item_type', eAdvItemType)
    title:			str				= mc_basic('title', str)
    description:	str				= mc_basic('description', str)

    @staticmethod
    def populate(selector: str, adv_item_type: eAdvItemType, item_selector: str = None, title: str = None, description: str = None):
        adv_item = AdvItem()
        adv_item.selector = selector
        adv_item.adv_item_type = adv_item_type
        adv_item.item_selector = selector if item_selector is None else item_selector
        adv_item.title = title
        adv_item.description = description
        return adv_item

path_sep = '\\'

class LootTableMap():
    def __init__(self, selector: str, path: List[str], loot_table: LootTable):
        self.selector	= selector
        self.path		= path
        self.original	= loot_table
        self.is_loop	= False
        self.is_sub		= False
        self.adv_length = 0

        self.remapped:			LootTable
        self.remap_selector:	str
        self.adv_chain:			List[AdvItem]
        self.adv_branches:		Dict[str, List[AdvItem]]
        self.branch_map:		Dict[str, int]

    @property
    def file_path(self) -> str:
        return path_sep.join(self.path)

    @property
    def contents(self) -> str:
        return json.dumps(self.remapped)


def create_adv_item(entry: Union[LootTableEntry, ItemEntry], loot_table_maps) -> AdvItem:
    selector = entry.name.replace('minecraft:', '').rsplit('/', 1).pop()
    if isinstance(entry, LootTableEntry):
        return AdvItem.populate(selector, eAdvItemType.reference)
    else:
        return AdvItem.populate(selector, eAdvItemType.item)


def fix_selector(adv_link: AdvItem, loot_table_map: LootTableMap):
    if loot_table_map.original.typ is eLootTable.block:
        prev_type = adv_link.adv_item_type
        adv_link.adv_item_type = eAdvItemType.from_items

        if adv_link.selector.startswith('potted'):
            adv_link.item_selector = adv_link.selector.replace('potted_', '')

        elif adv_link.selector in ['pumpkin_stem', 'attached_pumpkin_stem', 'melon_stem', 'attached_melon_stem']:
            adv_link.item_selector = adv_link.selector.replace('attached_', '').replace('_stem', '_seeds')
            if adv_link.selector.startswith('attached'):
                adv_link.adv_item_type = prev_type

        elif adv_link.selector in ['beetroots', 'carrots']:
            adv_link.item_selector = adv_link.selector[:-1]

        elif adv_link.selector == 'potatoes':
            adv_link.item_selector = 'potato'

        elif adv_link.selector == 'bamboo_sapling':
            adv_link.item_selector = 'bamboo'

        elif adv_link.selector == 'cocoa':
            adv_link.item_selector = 'cocoa_beans'

        elif adv_link.selector == 'frosted_ice':
            adv_link.item_selector = 'ice'
            adv_link.description = 'Shatter Ice From Frost Walking'
            adv_link.adv_item_type = prev_type

        elif adv_link.selector == 'kelp_plant':
            adv_link.item_selector = 'kelp'
            adv_link.description = 'Harvest a Kelp Plant'

        elif adv_link.selector == 'redstone_wire':
            adv_link.item_selector = 'redstone'

        elif adv_link.selector == 'tripwire':
            adv_link.item_selector = 'string'

        elif adv_link.selector == 'sweet_berry_bush':
            adv_link.item_selector = 'sweet_berries'

        elif adv_link.selector == 'tall_seagrass':
            adv_link.item_selector = 'seagrass'

        elif adv_link.selector == 'tall_grass':
            pass #assure tall grass registers as obtainable from items it drops

        else:
            adv_link.adv_item_type = prev_type

        if adv_link.description is None:
            adv_link.description = 'Collect or Break This Block'

    elif loot_table_map.original.typ is eLootTable.entity:
        if adv_link.selector == 'sheep' or 'sheep' in loot_table_map.path:
            adv_link.item_selector = 'sheep_spawn_egg'
            if adv_link.selector != 'sheep':
                adv_link.title = f'{get_upper_selector(adv_link.selector)} Sheep'
                adv_link.description = f'Kill a {get_upper_selector(adv_link.selector)} Sheep'
            else:
                adv_link.title = 'The Sheep Loot Table'
                adv_link.description = 'Collect Items From This Loot Table'
                if adv_link.adv_item_type is eAdvItemType.root:
                    adv_link.adv_item_type = eAdvItemType.root_table

        elif adv_link.selector == 'ender_dragon':
            adv_link.item_selector = 'dragon_head'
            adv_link.description = f'Kill the {get_upper_selector(adv_link.selector)}'

        elif adv_link.selector == 'wither':
            adv_link.item_selector = 'nether_star'
            adv_link.description = f'Kill the {get_upper_selector(adv_link.selector)}'

        elif adv_link.selector == 'iron_golem':
            adv_link.item_selector = 'iron_ingot'

        elif adv_link.selector == 'snow_golem':
            adv_link.item_selector = 'snowball'

        elif adv_link.selector == 'giant':
            adv_link.item_selector = 'zombie_spawn_egg'

        elif adv_link.selector == 'illusioner':
            adv_link.item_selector = 'pillager_spawn_egg'

        elif adv_link.selector == 'player':
            adv_link.item_selector = 'player_head'

        elif adv_link.selector == 'skeleton':
            adv_link.item_selector = 'skeleton_skull'

        elif adv_link.selector == 'zombie':
            adv_link.item_selector = 'zombie_head'

        elif adv_link.selector == 'wither_skeleton':
            adv_link.item_selector = 'wither_skeleton_skull'

        elif adv_link.selector == 'creeper':
            adv_link.item_selector = 'creeper_head'

        elif not adv_link.selector == 'armor_stand':
            adv_link.item_selector = f'{adv_link.selector}_spawn_egg'

        if adv_link.selector == 'armor_stand':
            adv_link.description = 'Punch an Armor Stand'
        
        elif adv_link.selector == 'player':
            adv_link.description = 'Get Yourself Killed'
            
        elif adv_link.description is None:
            adv_link.description = f'Kill a {get_upper_selector(adv_link.selector)}'

    elif loot_table_map.original.typ is eLootTable.chest:
        adv_link.item_selector = 'chest'
        adv_link.description = f'Find a {get_upper_selector(adv_link.selector)} Chest'

    elif loot_table_map.original.typ is eLootTable.fishing:
        adv_link.item_selector = 'fishing_rod'
        if adv_link.selector == 'fishing':
            adv_link.description = 'Go Fishing'
        else:
            adv_link.title = f'The {get_upper_selector(adv_link.selector)} Loot Table'
            adv_link.description = 'Collect Items From This Loot Table'
            if adv_link.adv_item_type is eAdvItemType.root:
                adv_link.adv_item_type = eAdvItemType.root_table


    elif loot_table_map.original.typ is eLootTable.advancement_reward:
        adv_link.item_selector = 'chest'
        adv_link.description = 'An Advancement Reward'

    elif loot_table_map.original.typ is eLootTable.generic:
        adv_link.item_selector = 'chest'
        adv_link.description = 'A Generic Loot table'

    elif loot_table_map.original.typ is eLootTable.gift:
        if adv_link.selector.startswith('armorer'):
            adv_link.item_selector = 'blast_furnace'

        elif adv_link.selector.startswith('butcher'):
            adv_link.item_selector = 'smoker'

        elif adv_link.selector.startswith('cartographer'):
            adv_link.item_selector = 'cartography_table'

        elif adv_link.selector.startswith('cleric'):
            adv_link.item_selector = 'brewing_stand'

        elif adv_link.selector.startswith('farmer'):
            adv_link.item_selector = 'composter'

        elif adv_link.selector.startswith('fisherman'):
            adv_link.item_selector = 'barrel'

        elif adv_link.selector.startswith('fletcher'):
            adv_link.item_selector = 'fletching_table'

        elif adv_link.selector.startswith('leatherworker'):
            adv_link.item_selector = 'cauldron'

        elif adv_link.selector.startswith('librarian'):
            adv_link.item_selector = 'lectern'

        elif adv_link.selector.startswith('mason'):
            adv_link.item_selector = 'stonecutter'

        elif adv_link.selector.startswith('shepherd'):
            adv_link.item_selector = 'loom'

        elif adv_link.selector.startswith('toolsmith'):
            adv_link.item_selector = 'smithing_table'

        elif adv_link.selector.startswith('weaponsmith'):
            adv_link.item_selector = 'grindstone'

        else:
            adv_link.item_selector = 'string'

        adv_link.description = f'Recieve a {get_upper_selector(adv_link.selector)}'

    else:
        print('Warning: unrecognized loot table type, script is probably outdated, download the newest version or yell at the developer for not updating the script!')
    
    if adv_link.description is None:
        print(f'Warning something went wrong, description not set for: {adv_link.selector}')


def populate_advancement_chain(root_selector: str, loot_table_maps: Dict[str, LootTableMap]):
    current_map = loot_table_maps[root_selector]

    current_map.adv_chain = []
    current_map.adv_branches = {}
    current_map.branch_map = {}
    advancement_chain = current_map.adv_chain
    advancement_branches = current_map.adv_branches
    branch_map = current_map.branch_map

    last_link = AdvItem.populate(root_selector, eAdvItemType.root)
    
    fix_selector(last_link, current_map)

    advancement_chain.append(last_link)

    count_to_next = 0
    last_branch_selector = None
    next_selector = root_selector
    build_chain = True

    entries: list

    def collect(entry: Entry, info: MCActionInfo):
        if isinstance(entry, (ItemEntry, LootTableEntry)) and not any(entry.name == e.name and entry.typ is e.typ for e in entries):
            entries.append(entry)
                
    while build_chain:
        entries = []
        current_map.remapped.interact(MCActionInfo(eItemType.Entry, collect, eActionType.Interact))
        found_link = False

        from_items_link = AdvItem.populate(current_map.remap_selector, eAdvItemType.root)
        fix_selector(from_items_link, loot_table_maps[current_map.remap_selector])
        if from_items_link.adv_item_type == eAdvItemType.from_items:
            last_link = from_items_link
            next_selector = current_map.remap_selector
            found_link = True

        for entry in entries:
            adv_item = create_adv_item(entry, loot_table_maps)
            if entry.name == 'minecraft:book' and 'functions' in entry and any(func.function is eFunction.enchant_randomly or func.function is eFunction.enchant_with_levels for func in entry.functions):
                adv_item.selector = 'enchanted_book'
                adv_item.item_selector = 'enchanted_book'
            
            if not found_link and adv_item.selector == current_map.remap_selector and adv_item.adv_item_type is eAdvItemType.item and loot_table_maps[adv_item.selector].original.typ is eLootTable.block:
                last_link = adv_item
                adv_item.adv_item_type = eAdvItemType.block
                fix_selector(adv_item, loot_table_maps[adv_item.selector])
                next_selector = current_map.remap_selector
                found_link = True
            else:
                if current_map.selector not in advancement_branches:
                    advancement_branches[current_map.selector] = []

                    if last_branch_selector is not None:
                        branch_map[last_branch_selector] = count_to_next
                    count_to_next = 0
                    last_branch_selector = current_map.selector

                if adv_item.adv_item_type is eAdvItemType.reference:
                    fix_selector(adv_item, loot_table_maps[adv_item.selector])
                advancement_branches[current_map.selector].append(adv_item)

        current_map = loot_table_maps[next_selector]
        count_to_next += 1

        if any(adv_link.selector == current_map.selector for adv_link in advancement_chain) or found_link is False:
            build_chain = False
            if last_branch_selector is not None:
                branch_map[last_branch_selector] = count_to_next

        if found_link is True:
            if build_chain == False:
                loot_table_maps[root_selector].is_loop = True
                last_link.adv_item_type = eAdvItemType.loop
                if current_map.selector not in advancement_branches:
                    advancement_branches[current_map.selector] = []
                advancement_branches[current_map.selector].append(last_link)
            else:
                advancement_chain.append(last_link)

def create_variety(original_conditions: Dict[eCondition, List[Condition]]):
    variety_tracker = {}
    for typ, conditions in original_conditions.items():
        variety_tracker[typ] = list(range(0, len(conditions)))
        random.shuffle(variety_tracker[typ])
    return variety_tracker


class Ref():
    variety_tracker = {}
    original_condition_count = 0
    validate_conditions = {}

def validate_conditions(loot_table_map: LootTableMap):
    Ref.original_conditions = {}
    Ref.original_condition_count = 0

    def collect(condition: Condition, info: MCActionInfo):
        # if info.depth not in original_conditions:
        # 	original_conditions
        # if condition.condition not in valid_condition_types:
        # 	all_original_conditions.append(condition)
        if condition.condition not in Ref.original_conditions:
            Ref.original_conditions[condition.condition] = []
        Ref.original_conditions[condition.condition].append(condition)
        Ref.original_condition_count += 1

    loot_table_map.original.interact(MCActionInfo(eItemType.Condition, collect, eActionType.Interact))
    
    Ref.variety_tracker = create_variety(Ref.original_conditions)
    condition_maps = []

    def validate(condition: Condition, info) -> Condition:
        restriction_level = get_restriction_level(condition)
        restricted = True

        if restriction_level is eRestriction.none:
            restricted = False

        elif restriction_level is eRestriction.type_specific:
            restricted = not loot_table_map.remapped.typ == loot_table_map.original.typ

        elif restriction_level is eRestriction.table_specific:
            restricted = not loot_table_map.selector == loot_table_map.remap_selector

        elif restriction_level is eRestriction.dont_validate:
            restricted = False

        condition_type = condition.condition
        condition_type_in_original = condition_type in Ref.original_conditions

        if not restricted:
            return None

        elif condition_type_in_original:
            if condition in Ref.original_conditions[condition.condition]:
                return None

            else:
                for condition_map in condition_maps:
                    if condition_map['original'] == condition:
                        return condition_map['remapped']

        if condition_type not in Ref.variety_tracker:
            condition_type = random.choice(list(Ref.variety_tracker))
        
        condition_index = Ref.variety_tracker[condition_type].pop()

        if len(Ref.variety_tracker[condition_type]) == 0:
            del Ref.variety_tracker[condition_type]

            if len(list(Ref.variety_tracker)) == 0:
                Ref.variety_tracker = create_variety(Ref.original_conditions)

        newCondition = Ref.original_conditions[condition_type][condition_index]

        condition_maps.append({
            'original': condition,
            'remapped': newCondition
        })

        return newCondition

    if Ref.original_condition_count == 0:
        loot_table_map.remapped.interact(MCActionInfo(eItemType.Condition, lambda condition, info: True, eActionType.Delete))
    else:
        loot_table_map.remapped.interact(MCActionInfo(eItemType.Condition, validate, eActionType.Set))

    loot_table_map.remapped.typ = loot_table_map.original.typ
