from mcr.loot_table_map import AdvItem, LootTableMap, eAdvItemType
import warnings

from mcr.helpers.regex import get_upper_selector
from mcr.mc.data_structures.loot_table import eLootTable

def fix_advancement_reward_selector(adv_link: AdvItem):
    adv_link.item_selector = 'chest'
    adv_link.description = 'An Advancement Reward'


def fix_barter_selector(adv_link: AdvItem):
    adv_link.item_selector = 'gold_ingot'
    adv_link.description = 'Barter With a Piglin'


def fix_block_selector(adv_link: AdvItem):
    prev_type = adv_link.adv_item_type
    adv_link.adv_item_type = eAdvItemType.from_items

    if adv_link.selector.startswith('potted'):
        adv_link.item_selector = adv_link.selector.replace('potted_', '')

    if adv_link.selector.endswith('_candle_cake'):
        adv_link.item_selector = adv_link.selector.replace('_cake', '')

    elif adv_link.selector in ['pumpkin_stem', 'attached_pumpkin_stem', 'melon_stem', 'attached_melon_stem']:
        adv_link.item_selector = adv_link.selector.replace(
            'attached_', '').replace('_stem', '_seeds')

        # TODO comment why this is done
        if adv_link.selector.startswith('attached'):
            adv_link.adv_item_type = prev_type

    elif adv_link.selector in ['beetroots', 'carrots']:
        adv_link.item_selector = adv_link.selector[:-1]  # remove the s

    elif adv_link.selector == 'potatoes':
        adv_link.item_selector = 'potato'

    elif adv_link.selector == 'bamboo_sapling':
        adv_link.item_selector = 'bamboo'

    elif adv_link.selector == 'cocoa':
        adv_link.item_selector = 'cocoa_beans'

    elif adv_link.selector == 'frosted_ice':
        adv_link.item_selector = 'ice'
        adv_link.description = 'Shatter Ice From Frost Walking'
        # TODO comment why this is done
        adv_link.adv_item_type = prev_type

    elif adv_link.selector == 'kelp_plant':
        adv_link.item_selector = 'kelp'
        adv_link.description = 'Harvest a Kelp Plant'

    # TODO Should I be replicating tall_grass?
    elif adv_link.selector == 'powder_snow':
        adv_link.item_selector = 'powder_snow_bucket'
        # adv_link.description = 'Break Powder Snow????'
        # # TODO comment why this is done
        # adv_link.adv_item_type = prev_type

    elif adv_link.selector == 'redstone_wire':
        adv_link.item_selector = 'redstone'

    elif adv_link.selector == 'tripwire':
        adv_link.item_selector = 'string'

    elif adv_link.selector == 'sweet_berry_bush':
        adv_link.item_selector = 'sweet_berries'

    elif adv_link.selector == 'tall_seagrass':
        adv_link.item_selector = 'seagrass'

    # TODO What?
    elif adv_link.selector == 'tall_grass':
        pass  # assure tall grass registers as obtainable from items it drops

    else:
        adv_link.adv_item_type = prev_type

    if adv_link.description is None:
        adv_link.description = 'Collect or Break This Block'


def fix_chest_selector(adv_link: AdvItem):
    adv_link.item_selector = 'chest'
    adv_link.description = f'Find a {get_upper_selector(adv_link.selector)} Chest'


def fix_empty_selector(adv_link: AdvItem, loot_table_map: LootTableMap):
    pass


def fix_entity_selector(adv_link: AdvItem, loot_table_map: LootTableMap):
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


def fix_fishing_selector(adv_link: AdvItem):
    adv_link.item_selector = 'fishing_rod'
    if adv_link.selector == 'fishing':
        adv_link.description = 'Go Fishing'
    else:
        adv_link.title = f'The {get_upper_selector(adv_link.selector)} Loot Table'
        adv_link.description = 'Collect Items From This Loot Table'
        if adv_link.adv_item_type is eAdvItemType.root:
            adv_link.adv_item_type = eAdvItemType.root_table


def fix_generic_selector(adv_link: AdvItem):
    adv_link.item_selector = 'chest'
    adv_link.description = 'A Generic Loot table'


def fix_gift_selector(adv_link: AdvItem):
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


def fix_selector(adv_link: AdvItem, loot_table_map: LootTableMap):
    if loot_table_map.original.type_ is eLootTable.advancement_reward:
        fix_advancement_reward_selector(adv_link)

    elif loot_table_map.original.type_ is eLootTable.barter:
        fix_barter_selector(adv_link)

    elif loot_table_map.original.type_ is eLootTable.block:
        fix_block_selector(adv_link)

    elif loot_table_map.original.type_ is eLootTable.chest:
        fix_chest_selector(adv_link)

    elif loot_table_map.original.type_ is eLootTable.entity:
        fix_entity_selector(adv_link, loot_table_map)

    elif loot_table_map.original.type_ is eLootTable.fishing:
        fix_fishing_selector(adv_link)

    elif loot_table_map.original.type_ is eLootTable.generic:
        fix_generic_selector(adv_link)

    elif loot_table_map.original.type_ is eLootTable.gift:
        fix_gift_selector(adv_link)

    else:
        warnings.warn(
            f'Unrecognized loot table type: {loot_table_map.original.type_}, script is probably outdated, download the newest version or yell at the developer for not updating the script!')

    if adv_link.description is None:
        warnings.warn(
            f'Something went wrong, description not set for: {adv_link.selector}')
