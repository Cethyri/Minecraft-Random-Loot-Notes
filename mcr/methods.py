
from dataclasses import dataclass
import json
from mcr.mc.data_structures.advancement import Advancement
from mcr.mc.data_structures.recipe import CraftingShaped, Ingredient, Recipe, Result, eRecipe
from mcr.mc.commands.function import Function
import os
import random
from typing import Optional, Tuple, Union

from mcr.loot_table_map import LootTableMap, populate_advancement_chain
from mcr.mc.data_structures.loot_table import LootTable
import mcr.mc.commands.argument_types as mcArgs


def load_table_info(flags: dict[str, bool], requires_cheats: list[str]) -> Tuple[dict[str, LootTableMap], list[str], dict[str, str]]:
    loot_table_maps: dict[str, LootTableMap] = {}
    remaining_selectors: list[str] = []
    original_to_selector: dict[str, str] = {}

    for dirpath, _, filenames in os.walk('loot_tables'):
        for filename in filenames:
            selector = filename.replace('.json', '')
            path = dirpath.replace('loot_tables\\', '').split('\\')

            if selector == 'player' and flags['hardcore']:
                continue

            if selector in requires_cheats and flags['no-cheats']:
                continue

            with open(os.path.join(dirpath, filename)) as json_file:
                json_text = json_file.read().replace('\n', '')
                original_to_selector[json_text] = selector
                loot_table = LootTable(json.loads(json_text))

            if ('pools' not in loot_table or len(loot_table.pools) == 0) and flags['no-dead-ends']:
                continue

            loot_table_maps[selector] = LootTableMap(
                selector, path, loot_table)
            remaining_selectors.append(selector)

    return (loot_table_maps, remaining_selectors, original_to_selector)


def randomize(loot_table_maps: dict[str, LootTableMap], remaining_selectors: list[str]):
    for selector in loot_table_maps:
        i = random.randrange(0, len(remaining_selectors))
        remapped_table = loot_table_maps[remaining_selectors[i]].original
        loot_table_maps[selector].remap_selector = remaining_selectors[i]
        loot_table_maps[selector].remapped = LootTable(
            json.loads(json.dumps(remapped_table)))  # Deep Copy
        del remaining_selectors[i]


def populate(loot_table_maps: dict[str, LootTableMap]):
    for selector in loot_table_maps:
        populate_advancement_chain(selector, loot_table_maps)
        for adv_item in loot_table_maps[selector].adv_chain:
            if adv_item.selector != selector:
                loot_table_maps[adv_item.selector].is_sub = not loot_table_maps[adv_item.selector].is_loop


def namespaced_func(funcName: str, datapack_name: str):
    return mcArgs.NamespacedId(funcName, datapack_name)


def datapack_func(funcName: str, datapack_name: str):
    return Function(namespaced_func(funcName, datapack_name))


def get_minecraft_selector(selector: str):
    return f'minecraft:{selector}'


def get_namespaced_selector(datapack_name: str, pathed_selector: str, additional: Optional[str] = None):
    return f'{datapack_name}:{pathed_selector}{additional if additional is not None else ""}'


def sheep_color_to_number(color: str):
    if color == 'white':
        return 0
    if color == 'orange':
        return 1
    if color == 'magenta':
        return 2
    if color == 'light_blue':
        return 3
    if color == 'yellow':
        return 4
    if color == 'lime':
        return 5
    if color == 'pink':
        return 6
    if color == 'gray':
        return 7
    if color == 'light_gray':
        return 8
    if color == 'cyan':
        return 9
    if color == 'purple':
        return 10
    if color == 'blue':
        return 11
    if color == 'brown':
        return 12
    if color == 'green':
        return 13
    if color == 'red':
        return 14
    if color == 'black':
        return 15

    print(f'SHEEP COLOR BROKEN! {color}')


def get_pathed_selector(selector: str, path: str, base: str, link_index: int):
    name = f'{link_index}-{selector}' if link_index >= 0 else selector
    return os.path.join(path, base, name).replace('\\', '/')


@dataclass
class RecipeInfo:
    pathed_selector: str
    parent_item_selector: str
    parent_item_is_correct: bool
    child_item_selector: str
    child_item_is_correct: bool
    group_selector: str


def generate_recipe(rInfo: RecipeInfo, recipes: dict[str, CraftingShaped], current_advs_and_recipes: list[Union[Advancement, Recipe]]):
    recipe = CraftingShaped()
    recipe.type_ = eRecipe.crafting_shaped
    recipe.group = f'rl_notes_{rInfo.group_selector}'
    recipe.pattern = [
        f'{" " if rInfo.parent_item_is_correct and rInfo.child_item_is_correct else "B"}I',
        'PK'
    ]

    knowledge_book = Ingredient()
    knowledge_book.item = 'minecraft:knowledge_book'
    parent = Ingredient()
    parent.item = rInfo.parent_item_selector
    child = Ingredient()
    child.item = rInfo.child_item_selector
    barrier = Ingredient()
    barrier.item = 'minecraft:barrier'

    recipe.key = {
        'I': child,
        'P': parent,
        'K': knowledge_book,
        'B': barrier
    }
    if rInfo.parent_item_is_correct and rInfo.child_item_is_correct:
        del recipe.key['B']

    recipe.result = Result()
    recipe.result.count = 1
    recipe.result.item = rInfo.child_item_selector

    recipes[rInfo.pathed_selector] = recipe
    current_advs_and_recipes.append(recipe)