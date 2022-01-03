from mcr.randomizer_template import AdvItem, RandomizerTemplate, eAdvItemType
import warnings

from mcr.helpers.regex import get_upper_name
from mcr.mc.data_structures.loot_table import eLootTable

def fix_advancement_reward_name(adv_item: AdvItem):
    adv_item.item_name = 'chest'
    adv_item.description = 'An Advancement Reward'


def fix_barter_name(adv_item: AdvItem):
    adv_item.item_name = 'gold_ingot'
    adv_item.description = 'Barter With a Piglin'


def fix_block_name(adv_item: AdvItem):
    prev_type = adv_item.adv_item_type
    adv_item.adv_item_type = eAdvItemType.from_items
    # denotes that this item can be created from the items it drops and thus continues the current randomizer branch.
    # change this back to previous type to only correct the name of a block to it's item name.
    split_name = adv_item.name.split('_')

    match split_name:
        case ['potted', *_]:
            adv_item.item_name = adv_item.item_name.replace('potted_', '')

            match split_name:
                case [*_, 'azalea', 'bush']:
                    adv_item.item_name = adv_item.item_name.replace('_bush', '')

        case [*_, 'candle', 'cake']:
            adv_item.item_name = adv_item.item_name.replace('_cake', '')

        case [*_, 'pumpkin' | 'melon' as fruit, 'stem']:
            adv_item.item_name = f'{fruit}_seeds'

            # TODO comment why this is done
            if adv_item.name.startswith('attached'):
                adv_item.adv_item_type = prev_type

        case ['twisting' | 'weeping', 'vines', 'plant']:
            adv_item.item_name = adv_item.item_name.replace('_plant', '')

        case ['beetroots' | 'carrots']:
            adv_item.item_name = adv_item.item_name[:-1]  # remove the s

        case ['potatoes']:
            adv_item.item_name = 'potato'

        case ['bamboo', 'sapling']:
            adv_item.item_name = 'bamboo'

        case ['cocoa']:
            adv_item.item_name = 'cocoa_beans'

        case ['frosted', 'ice']:
            adv_item.item_name = 'ice'
            adv_item.description = 'Shatter Ice From Frost Walking'
            adv_item.adv_item_type = prev_type

        case [*_, 'fire']:
            adv_item.item_name = 'flint_and_steel'
            adv_item.description = 'Put out a fire'
            adv_item.adv_item_type = prev_type

        case ['kelp', 'plant']:
            adv_item.item_name = 'kelp'
            adv_item.description = 'Harvest a Kelp Plant'

        case ['powder', 'snow']:
            adv_item.item_name = 'powder_snow_bucket'
            adv_item.adv_item_type = prev_type

        case ['redstone', 'wire']:
            adv_item.item_name = 'redstone'

        case ['tripwire']:
            adv_item.item_name = 'string'

        case [*_, _, 'cauldron']:
            adv_item.item_name = 'cauldron'

        case ['nether', 'portal']:
            adv_item.item_name = 'obsidian'

        case ['cave', 'vines', *_]:
            adv_item.item_name = 'glow_berries'

        case ['big', 'dripleaf', 'stem']:
            adv_item.item_name = 'big_dripleaf'

        case ['sweet', 'berry', 'bush']:
            adv_item.item_name = 'sweet_berries'

        case ['tall', 'seagrass']:
            adv_item.item_name = 'seagrass'

        case ['tall', 'grass']:
            pass  # assures tall grass registers as obtainable from items it drops since it drops seeds and not grass itself

        case _:
            adv_item.adv_item_type = prev_type

    if adv_item.description is None:
        adv_item.description = 'Collect or Break This Block'


def fix_chest_name(adv_item: AdvItem):
    adv_item.item_name = 'chest'
    adv_item.description = f'Find a {get_upper_name(adv_item.name)} Chest'


def fix_empty_name(adv_item: AdvItem, rand_template: RandomizerTemplate):
    pass


def fix_entity_name(adv_item: AdvItem, rand_template: RandomizerTemplate):
    if adv_item.name == 'sheep' or 'sheep' in rand_template.path:
        adv_item.item_name = 'sheep_spawn_egg'
        if adv_item.name != 'sheep':
            adv_item.title = f'{get_upper_name(adv_item.name)} Sheep'
            adv_item.description = f'Kill a {get_upper_name(adv_item.name)} Sheep'
        else:
            adv_item.title = 'The Sheep Loot Table'
            adv_item.description = 'Collect Items From This Loot Table'
            if adv_item.adv_item_type is eAdvItemType.root:
                adv_item.adv_item_type = eAdvItemType.root_table

    elif adv_item.name == 'ender_dragon':
        adv_item.item_name = 'dragon_head'
        adv_item.description = f'Kill the {get_upper_name(adv_item.name)}'

    elif adv_item.name == 'wither':
        adv_item.item_name = 'nether_star'
        adv_item.description = f'Kill the {get_upper_name(adv_item.name)}'

    elif adv_item.name == 'iron_golem':
        adv_item.item_name = 'iron_ingot'

    elif adv_item.name == 'snow_golem':
        adv_item.item_name = 'snowball'

    elif adv_item.name == 'giant':
        adv_item.item_name = 'zombie_spawn_egg'

    elif adv_item.name == 'illusioner':
        adv_item.item_name = 'pillager_spawn_egg'

    elif adv_item.name == 'player':
        adv_item.item_name = 'player_head'

    elif adv_item.name == 'skeleton':
        adv_item.item_name = 'skeleton_skull'

    elif adv_item.name == 'zombie':
        adv_item.item_name = 'zombie_head'

    elif adv_item.name == 'wither_skeleton':
        adv_item.item_name = 'wither_skeleton_skull'

    elif adv_item.name == 'creeper':
        adv_item.item_name = 'creeper_head'

    elif not adv_item.name == 'armor_stand':
        adv_item.item_name = f'{adv_item.name}_spawn_egg'

    if adv_item.name == 'armor_stand':
        adv_item.description = 'Punch an Armor Stand'

    elif adv_item.name == 'player':
        adv_item.description = 'Get Yourself Killed'

    elif adv_item.description is None:
        adv_item.description = f'Kill a {get_upper_name(adv_item.name)}'


def fix_fishing_name(adv_item: AdvItem):
    adv_item.item_name = 'fishing_rod'
    if adv_item.name == 'fishing':
        adv_item.description = 'Go Fishing'
    else:
        adv_item.title = f'The {get_upper_name(adv_item.name)} Loot Table'
        adv_item.description = 'Collect Items From This Loot Table'
        if adv_item.adv_item_type is eAdvItemType.root:
            adv_item.adv_item_type = eAdvItemType.root_table


def fix_generic_name(adv_item: AdvItem):
    adv_item.item_name = 'chest'
    adv_item.description = 'A Generic Loot table'


def fix_gift_name(adv_item: AdvItem):
    if adv_item.name.startswith('armorer'):
        adv_item.item_name = 'blast_furnace'

    elif adv_item.name.startswith('butcher'):
        adv_item.item_name = 'smoker'

    elif adv_item.name.startswith('cartographer'):
        adv_item.item_name = 'cartography_table'

    elif adv_item.name.startswith('cleric'):
        adv_item.item_name = 'brewing_stand'

    elif adv_item.name.startswith('farmer'):
        adv_item.item_name = 'composter'

    elif adv_item.name.startswith('fisherman'):
        adv_item.item_name = 'barrel'

    elif adv_item.name.startswith('fletcher'):
        adv_item.item_name = 'fletching_table'

    elif adv_item.name.startswith('leatherworker'):
        adv_item.item_name = 'cauldron'

    elif adv_item.name.startswith('librarian'):
        adv_item.item_name = 'lectern'

    elif adv_item.name.startswith('mason'):
        adv_item.item_name = 'stonecutter'

    elif adv_item.name.startswith('shepherd'):
        adv_item.item_name = 'loom'

    elif adv_item.name.startswith('toolsmith'):
        adv_item.item_name = 'smithing_table'

    elif adv_item.name.startswith('weaponsmith'):
        adv_item.item_name = 'grindstone'

    else:
        adv_item.item_name = 'string'

    adv_item.description = f'Recieve a {get_upper_name(adv_item.name)}'


def fix_name(adv_item: AdvItem, rand_template: RandomizerTemplate):
    adv_item2 = AdvItem(adv_item.name, adv_item.adv_item_type, adv_item.item_name, adv_item.title, adv_item.description)
    match rand_template.original.type_:
        case eLootTable.advancement_reward:
            fix_advancement_reward_name(adv_item)

        case eLootTable.barter:
            fix_barter_name(adv_item)

        case eLootTable.block:
            fix_block_name(adv_item)

        case eLootTable.chest:
            fix_chest_name(adv_item)

        case eLootTable.entity:
            fix_entity_name(adv_item, rand_template)

        case eLootTable.fishing:
            fix_fishing_name(adv_item)

        case eLootTable.generic:
            fix_generic_name(adv_item)

        case eLootTable.gift:
            fix_gift_name(adv_item)

        case _:
            warnings.warn(
                f'Unrecognized loot table type: {rand_template.original.type_}, script is probably outdated, download the newest version or yell at the developer for not updating the script!')

    if adv_item.description is None:
        warnings.warn(
            f'Something went wrong, description not set for: {adv_item.name}')

def create_and_fix_name(adv_name: str, item_type: eAdvItemType, rand_templates: dict[str, RandomizerTemplate]):
    adv_item = AdvItem(adv_name, item_type)
    fix_name(adv_item, rand_templates[adv_name])
    return adv_item