from mcr.loot_table_map import AdvItem, LootTableMap, eAdvItemType
import warnings

from mcr.helpers.regex import get_upper_name
from mcr.mc.data_structures.loot_table import eLootTable

def fix_advancement_reward_name(adv_link: AdvItem):
    adv_link.item_name = 'chest'
    adv_link.description = 'An Advancement Reward'


def fix_barter_name(adv_link: AdvItem):
    adv_link.item_name = 'gold_ingot'
    adv_link.description = 'Barter With a Piglin'


def fix_block_name(adv_link: AdvItem):
    prev_type = adv_link.adv_item_type
    adv_link.adv_item_type = eAdvItemType.from_items

    if adv_link.name.startswith('potted'):
        adv_link.item_name = adv_link.name.replace('potted_', '')

    if adv_link.name.endswith('_candle_cake'):
        adv_link.item_name = adv_link.name.replace('_cake', '')

    if adv_link.name.endswith('twisting_vine_plant'):
        adv_link.item_name = adv_link.name.replace('twisting_vines', '')

    elif adv_link.name in ['pumpkin_stem', 'attached_pumpkin_stem', 'melon_stem', 'attached_melon_stem']:
        adv_link.item_name = adv_link.name.replace(
            'attached_', '').replace('_stem', '_seeds')

        # TODO comment why this is done
        if adv_link.name.startswith('attached'):
            adv_link.adv_item_type = prev_type

    elif adv_link.name in ['beetroots', 'carrots']:
        adv_link.item_name = adv_link.name[:-1]  # remove the s

    elif adv_link.name == 'potatoes':
        adv_link.item_name = 'potato'

    elif adv_link.name == 'bamboo_sapling':
        adv_link.item_name = 'bamboo'

    elif adv_link.name == 'cocoa':
        adv_link.item_name = 'cocoa_beans'

    elif adv_link.name == 'frosted_ice':
        adv_link.item_name = 'ice'
        adv_link.description = 'Shatter Ice From Frost Walking'
        # TODO comment why this is done
        adv_link.adv_item_type = prev_type

    elif adv_link.name == 'kelp_plant':
        adv_link.item_name = 'kelp'
        adv_link.description = 'Harvest a Kelp Plant'

    # TODO Should I be replicating tall_grass?
    elif adv_link.name == 'powder_snow':
        adv_link.item_name = 'powder_snow_bucket'
        # adv_link.description = 'Break Powder Snow????'
        # # TODO comment why this is done
        # adv_link.adv_item_type = prev_type

    elif adv_link.name == 'redstone_wire':
        adv_link.item_name = 'redstone'

    elif adv_link.name == 'tripwire':
        adv_link.item_name = 'string'

    elif adv_link.name == 'sweet_berry_bush':
        adv_link.item_name = 'sweet_berries'

    elif adv_link.name == 'tall_seagrass':
        adv_link.item_name = 'seagrass'

    # TODO What?
    elif adv_link.name == 'tall_grass':
        pass  # assure tall grass registers as obtainable from items it drops

    else:
        adv_link.adv_item_type = prev_type

    if adv_link.description is None:
        adv_link.description = 'Collect or Break This Block'


def fix_chest_name(adv_link: AdvItem):
    adv_link.item_name = 'chest'
    adv_link.description = f'Find a {get_upper_name(adv_link.name)} Chest'


def fix_empty_name(adv_link: AdvItem, loot_table_map: LootTableMap):
    pass


def fix_entity_name(adv_link: AdvItem, loot_table_map: LootTableMap):
    if adv_link.name == 'sheep' or 'sheep' in loot_table_map.path:
        adv_link.item_name = 'sheep_spawn_egg'
        if adv_link.name != 'sheep':
            adv_link.title = f'{get_upper_name(adv_link.name)} Sheep'
            adv_link.description = f'Kill a {get_upper_name(adv_link.name)} Sheep'
        else:
            adv_link.title = 'The Sheep Loot Table'
            adv_link.description = 'Collect Items From This Loot Table'
            if adv_link.adv_item_type is eAdvItemType.root:
                adv_link.adv_item_type = eAdvItemType.root_table

    elif adv_link.name == 'ender_dragon':
        adv_link.item_name = 'dragon_head'
        adv_link.description = f'Kill the {get_upper_name(adv_link.name)}'

    elif adv_link.name == 'wither':
        adv_link.item_name = 'nether_star'
        adv_link.description = f'Kill the {get_upper_name(adv_link.name)}'

    elif adv_link.name == 'iron_golem':
        adv_link.item_name = 'iron_ingot'

    elif adv_link.name == 'snow_golem':
        adv_link.item_name = 'snowball'

    elif adv_link.name == 'giant':
        adv_link.item_name = 'zombie_spawn_egg'

    elif adv_link.name == 'illusioner':
        adv_link.item_name = 'pillager_spawn_egg'

    elif adv_link.name == 'player':
        adv_link.item_name = 'player_head'

    elif adv_link.name == 'skeleton':
        adv_link.item_name = 'skeleton_skull'

    elif adv_link.name == 'zombie':
        adv_link.item_name = 'zombie_head'

    elif adv_link.name == 'wither_skeleton':
        adv_link.item_name = 'wither_skeleton_skull'

    elif adv_link.name == 'creeper':
        adv_link.item_name = 'creeper_head'

    elif not adv_link.name == 'armor_stand':
        adv_link.item_name = f'{adv_link.name}_spawn_egg'

    if adv_link.name == 'armor_stand':
        adv_link.description = 'Punch an Armor Stand'

    elif adv_link.name == 'player':
        adv_link.description = 'Get Yourself Killed'

    elif adv_link.description is None:
        adv_link.description = f'Kill a {get_upper_name(adv_link.name)}'


def fix_fishing_name(adv_link: AdvItem):
    adv_link.item_name = 'fishing_rod'
    if adv_link.name == 'fishing':
        adv_link.description = 'Go Fishing'
    else:
        adv_link.title = f'The {get_upper_name(adv_link.name)} Loot Table'
        adv_link.description = 'Collect Items From This Loot Table'
        if adv_link.adv_item_type is eAdvItemType.root:
            adv_link.adv_item_type = eAdvItemType.root_table


def fix_generic_name(adv_link: AdvItem):
    adv_link.item_name = 'chest'
    adv_link.description = 'A Generic Loot table'


def fix_gift_name(adv_link: AdvItem):
    if adv_link.name.startswith('armorer'):
        adv_link.item_name = 'blast_furnace'

    elif adv_link.name.startswith('butcher'):
        adv_link.item_name = 'smoker'

    elif adv_link.name.startswith('cartographer'):
        adv_link.item_name = 'cartography_table'

    elif adv_link.name.startswith('cleric'):
        adv_link.item_name = 'brewing_stand'

    elif adv_link.name.startswith('farmer'):
        adv_link.item_name = 'composter'

    elif adv_link.name.startswith('fisherman'):
        adv_link.item_name = 'barrel'

    elif adv_link.name.startswith('fletcher'):
        adv_link.item_name = 'fletching_table'

    elif adv_link.name.startswith('leatherworker'):
        adv_link.item_name = 'cauldron'

    elif adv_link.name.startswith('librarian'):
        adv_link.item_name = 'lectern'

    elif adv_link.name.startswith('mason'):
        adv_link.item_name = 'stonecutter'

    elif adv_link.name.startswith('shepherd'):
        adv_link.item_name = 'loom'

    elif adv_link.name.startswith('toolsmith'):
        adv_link.item_name = 'smithing_table'

    elif adv_link.name.startswith('weaponsmith'):
        adv_link.item_name = 'grindstone'

    else:
        adv_link.item_name = 'string'

    adv_link.description = f'Recieve a {get_upper_name(adv_link.name)}'


def fix_name(adv_link: AdvItem, loot_table_map: LootTableMap):
    if loot_table_map.original.type_ is eLootTable.advancement_reward:
        fix_advancement_reward_name(adv_link)

    elif loot_table_map.original.type_ is eLootTable.barter:
        fix_barter_name(adv_link)

    elif loot_table_map.original.type_ is eLootTable.block:
        fix_block_name(adv_link)

    elif loot_table_map.original.type_ is eLootTable.chest:
        fix_chest_name(adv_link)

    elif loot_table_map.original.type_ is eLootTable.entity:
        fix_entity_name(adv_link, loot_table_map)

    elif loot_table_map.original.type_ is eLootTable.fishing:
        fix_fishing_name(adv_link)

    elif loot_table_map.original.type_ is eLootTable.generic:
        fix_generic_name(adv_link)

    elif loot_table_map.original.type_ is eLootTable.gift:
        fix_gift_name(adv_link)

    else:
        warnings.warn(
            f'Unrecognized loot table type: {loot_table_map.original.type_}, script is probably outdated, download the newest version or yell at the developer for not updating the script!')

    if adv_link.description is None:
        warnings.warn(
            f'Something went wrong, description not set for: {adv_link.name}')
