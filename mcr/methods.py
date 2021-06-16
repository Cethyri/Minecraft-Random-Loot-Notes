
import io
import json
import os
import random
import zipfile
from dataclasses import dataclass
from tkinter.filedialog import asksaveasfile
from typing import Any, Callable, Optional, Union

import mcr.mc.commands.argument_types as mcArgs
from mcr.helpers.regex import get_upper_selector, shorten_selector
from mcr.loot_table_map import (AdvItem, LootTableMap, eAdvItemType,
                                populate_advancement_chain,
                                validate_conditions)
from mcr.mc.commands.execute import Execute
from mcr.mc.commands.function import Function
from mcr.mc.commands.mcfunction import MCFunction
from mcr.mc.data_structures.advancement import Advancement, Rewards
from mcr.mc.data_structures.criteria import (Criteria, EntityKilledPlayer,
                                             FishingRodHooked,
                                             PlayerKilledEntity, eTrigger)
from mcr.mc.data_structures.display import Display
from mcr.mc.data_structures.entity import Entity
from mcr.mc.data_structures.loot_table import LootTable, eLootTable
from mcr.mc.data_structures.nbt import NBT, NBTPath, Tag_Byte, Tag_Short
from mcr.mc.data_structures.recipe import (CraftingShaped, Ingredient, Recipe,
                                           Result, eRecipe)
from mcr.mcr_data import MCRData

TEMP_DIR = 'mc_temp_dir'
TOTAL_STEPS = 9


def _initializePackInformation(mcrData: MCRData):
    if not mcrData.flags.hide_seed:
        mcrData.datapack_name += f'(seed={mcrData.seed})'

    random.seed(mcrData.seed)
    mcrData.datapack_desc = f'Minecraft Randomizer, Seed: "{mcrData.seed}"'

    mcrData.notesGrantSelector = '@s'
    if mcrData.flags.co_op:
        mcrData.notesGrantSelector = '@a'

    with open('mcr/mc/data/requires_cheats.json') as json_file:
        mcrData.requires_cheats = json.load(json_file)

    with open('mcr/mc/data/double_tall_blocks.json') as json_file:
        mcrData.double_tall_blocks = json.load(json_file)


def _load_table_info(mcrData: MCRData):
    loot_table_path = os.path.join(
        TEMP_DIR, 'data', 'minecraft', 'loot_tables')

    for dirpath, _, filenames in os.walk(loot_table_path):
        for filename in filenames:
            selector = filename.replace('.json', '')
            path = dirpath.replace(loot_table_path + '\\', '').split('\\')

            if selector == 'player' and mcrData.flags.hardcore:
                continue

            if selector in mcrData.requires_cheats and mcrData.flags.no_cheats:
                continue

            with open(os.path.join(dirpath, filename)) as json_file:
                json_text = json_file.read().replace('\n', '')
                mcrData.original_to_selector[json_text] = selector
                loot_table = LootTable(json.loads(json_text))

            if ('pools' not in loot_table or len(loot_table.pools) == 0) and mcrData.flags.no_dead_ends:
                continue

            mcrData.loot_table_maps[selector] = LootTableMap(
                selector, path, loot_table)
            mcrData.remaining_selectors.append(selector)


def _randomize(mcrData: MCRData):
    for selector in mcrData.loot_table_maps:

        i = random.randrange(0, len(mcrData.remaining_selectors))

        remapped_table = mcrData.loot_table_maps[mcrData.remaining_selectors[i]].original
        mcrData.loot_table_maps[selector].remap_selector = mcrData.remaining_selectors[i]

        mcrData.loot_table_maps[selector].remapped = LootTable(
            json.loads(json.dumps(remapped_table)))  # Deep Copy

        del mcrData.remaining_selectors[i]


def _populate(mcrData: MCRData):
    current_map: LootTableMap
    for selector in mcrData.loot_table_maps:
        populate_advancement_chain(selector, mcrData.loot_table_maps)
        for adv_item in mcrData.loot_table_maps[selector].adv_chain:
            current_map = mcrData.loot_table_maps[adv_item.selector]
            if not adv_item.selector == selector:
                current_map.is_sub = not current_map.is_loop


def namespaced_func(funcName: str, datapack_name: str):
    return mcArgs.NamespacedId(funcName, datapack_name)


def datapack_func(funcName: str, datapack_name: str):
    return Function(namespaced_func(funcName, datapack_name))


def get_minecraft_selector(selector: str):
    return f'minecraft:{selector}'


def get_namespaced_selector(datapack_name: str, pathed_selector: str, additional: Optional[str] = None):
    return f'{datapack_name}:{pathed_selector}{additional if additional is not None else ""}'


sheep_color_to_number: dict[str, int] = {
    'white': 0,
    'orange': 1,
    'magenta': 2,
    'light_blue': 3,
    'yellow': 4,
    'lime': 5,
    'pink': 6,
    'gray': 7,
    'light_gray': 8,
    'cyan': 9,
    'purple': 10,
    'blue': 11,
    'brown': 12,
    'green': 13,
    'red': 14,
    'black': 15
}


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


def generate_recipe(rInfo: RecipeInfo):
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

    return recipe


def generate_children_functions(mcrData: MCRData, pathed_selector: str, start_link: AdvItem, path: str, base: str, child_index: int, execute_conditions_list: list[Callable[..., Any]]):
    mcrData.functions[pathed_selector].append(
        'scoreboard players set @s mcr_incomplete 0')
    mcrData.functions[pathed_selector].append(
        'scoreboard players set @s mcr_complete 0')

    references: list[str] = []
    search_queue = [start_link]
    reference_namespaced_selectors = {}

    cur_link: AdvItem
    current_map: LootTableMap

    is_reference = False

    while len(search_queue) > 0:
        cur_link = search_queue.pop()
        current_map = mcrData.loot_table_maps[cur_link.selector]

        if is_reference:
            mcrData.functions[pathed_selector].append(
                'scoreboard players set @s mcr_ref_complete 0')

        references.append(current_map.selector)

        branches: list[AdvItem] = []
        if cur_link.selector in current_map.adv_branches:
            branches.extend(current_map.adv_branches[cur_link.selector])
        if len(current_map.adv_chain) > 1 and current_map.adv_chain[1].adv_item_type is not eAdvItemType.from_items:
            branches.append(current_map.adv_chain[1])

        for adv_child in branches:
            child_pathed_selector = get_pathed_selector(
                adv_child.selector, path, base, 1 if is_reference else child_index)

            namespaced_selector = get_namespaced_selector(
                mcrData.datapack_name, child_pathed_selector)
            if adv_child.adv_item_type is not eAdvItemType.reference and adv_child.selector == adv_child.item_selector:
                for execute_conditions in execute_conditions_list:
                    mcrData.functions[pathed_selector].execute(f'execute {execute_conditions(adv_child)}').run(
                        f'advancement grant @s only {namespaced_selector}')
                (mcrData.functions[pathed_selector]
                    .custom(f'recipe give @s[advancements = {{ {namespaced_selector} = true }}] {namespaced_selector}')
                    .custom(f'scoreboard players add @s[advancements = {{ {namespaced_selector} = true }}] mcr_complete 1')
                    .custom(f'scoreboard players add @s[advancements = {{ {namespaced_selector} = false }}] mcr_incomplete 1')
                 )

                if is_reference:
                    mcrData.functions[pathed_selector].custom(
                        f'scoreboard players add @s[advancements = {{ {namespaced_selector} = true }}] mcr_ref_complete 1')

            elif adv_child.adv_item_type is eAdvItemType.reference and adv_child.selector not in references:
                search_queue.append(adv_child)
                reference_namespaced_selectors[adv_child.selector] = namespaced_selector

        if is_reference:
            root_namespaced_selector = get_namespaced_selector(
                mcrData.datapack_name, get_pathed_selector(cur_link.selector, path, base, 0))
            (mcrData.functions[pathed_selector]
                .custom(f'advancement grant @s[scores = {{ mcr_ref_complete = 1.. }}] only {reference_namespaced_selectors[cur_link.selector]}')
                .custom(f'advancement grant @s[scores = {{ mcr_ref_complete = 1.. }}] only {root_namespaced_selector}')
             )
        else:
            is_reference = True


def generate_conditions(mcrData: MCRData, pathed_selector: str, adv_link: AdvItem, path: str, base: str, link_index: int, objective_num: int) -> int:

    if pathed_selector in mcrData.functions:
        mcrData.printDetail('Warning: duplicate function!')

    loot_table_map = mcrData.loot_table_maps[adv_link.selector]

    helper_selector = f'helper/{pathed_selector}'
    namespaced_helper = get_namespaced_selector(
        mcrData.datapack_name, helper_selector)
    namespaced_selector = get_namespaced_selector(
        mcrData.datapack_name, pathed_selector)
    selector_function = Function(mcArgs.NamespacedId(namespaced_selector))

    adv_selector_id = mcArgs.NamespacedId(adv_link.selector)

    mcrData.functions[pathed_selector] = MCFunction()

    objective_name = f'{shorten_selector(adv_link.selector)}_r{objective_num}'
    objective = mcArgs.Objective(objective_name)
    if len(objective_name) > 16:
        mcrData.printDetail(objective_name)
    objective_num += 1
    objective_criteria = 'dummy'
    use_helper = False
    reset_objective = False
    execute_conditions_list: list[Callable[[AdvItem], Execute[None]]]
    grant_target_selector = '[scores = { mcr_incomplete = 0 }]'
    child_index = link_index + 1

    def get_item_entity(adv_child: AdvItem, distance: Union[int, float]):
        return mcArgs.Entity('@e', distance=f'..{distance}', type='minecraft:item', limit=1, nbt=NBT({'Age': Tag_Short(0), 'Item': {'id': f'minecraft:{adv_child.item_selector}'}}))

    if adv_link.selector == 'sheep' or 'fishing' in loot_table_map.path:
        return objective_num

    elif adv_link.selector == 'armor_stand':
        # TODO check if get_item_entity needs 'armor_stand' explicitly
        mcrData.functions['tick'].execute().as_('@a').if_score_matches('@s', objective,
                                                                       '..0').at('@s').at(get_item_entity(adv_link, 8)).run(selector_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(get_item_entity(adv_child, 2))
        ]

        grant_target_selector = ''

    elif adv_link.selector in mcrData.double_tall_blocks:
        for i in range(10):
            score = i + 1
            distance = score / 2
            pos = mcArgs.Vec3(z=distance, rel='^')
            (mcrData.functions['tick']
                .execute().as_('@a').if_score_matches('@s', objective, '0').at('@s').anchored('eyes').if_block(pos, adv_selector_id).run(f'scoreboard players set @s {objective} {score}')
                .execute().as_('@a').if_score_matches('@s', objective, score).at('@s').anchored('eyes').unless_block(pos, adv_selector_id).positioned(pos).run(selector_function)
             )

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().unless_block(
                mcArgs.Vec3().loc, adv_selector_id).if_entity(get_item_entity(adv_child, 2))
        ]

        reset_objective = True
        grant_target_selector = ''

    elif loot_table_map.original.type_ is eLootTable.block:
        objective_criteria = f'minecraft.mined:minecraft.{adv_link.selector}'

        mcrData.functions['tick'].execute().as_('@a').if_score_matches('@s',
                                                                       objective, '1..').at('@s').run(selector_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(get_item_entity(adv_child, 8))
        ]

        reset_objective = True
        grant_target_selector = ''

    elif loot_table_map.original.type_ is eLootTable.chest:
        loot_table_pathed_selector = get_pathed_selector(
            adv_link.selector, path, '', -1)

        for i in range(10):
            score = i + 1
            distance = score / 2
            pos = mcArgs.Vec3(z=distance, rel='^')
            block = mcArgs.NamespacedId(
                f'chest{{ LootTable: "minecraft:{loot_table_pathed_selector}" }}')
            (mcrData.functions['tick']
                .execute().as_('@a').if_score_matches('@s', objective, 0).at('@s').anchored('eyes').if_block(pos, block).run(f'scoreboard players set @s {objective} {score}')
                .execute().as_('@a').if_score_matches('@s', objective, score).at('@s').anchored('eyes').unless_block(pos, block).positioned(pos).run(selector_function)
             )

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_block(mcArgs.Vec3().rel(), mcArgs.NamespacedId(
                f'chest{{ Items: [{{ id: "minecraft:{adv_child.item_selector}" }}] }}'))
        ]

        reset_objective = True

    elif loot_table_map.original.type_ is eLootTable.gift and 'hero_of_the_village' in loot_table_map.path:
        villager_type = adv_link.selector.replace('_gift', '')

        as_selector = mcArgs.Entity(
            '@a', nbt=NBT({'ActiveEffects': [{'Id': Tag_Byte(32)}]}))
        at_selector = mcArgs.Entity('@e', distance='..8', type='minecraft:villager', nbt=NBT(
            {'VillagerData': {'profession': f'minecraft:{villager_type}'}}))

        mcrData.functions['tick'].execute().as_(as_selector).if_score_matches(
            '@s', objective, '0..').at('@s').at(at_selector).run(selector_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(get_item_entity(adv_child, 2))
        ]

    elif adv_link.selector == 'cat_morning_gift':
        sleeptimerCheck = NBTPath({'SleepTimer': Tag_Short(101)})

        mcrData.functions['tick'].execute().as_('@a').if_data_entity('@s', sleeptimerCheck).at('@s').at(
            mcArgs.Entity('@e', distance='..16', type='minecraft:cat')).run(selector_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(get_item_entity(adv_child, 4)),
            lambda adv_child: Execute.conditions().as_(mcArgs.Entity(
                '@s', nbt=NBT({'Inventory': [{'id': f'minecraft:{adv_child.item_selector}'}]})))
        ]

    elif loot_table_map.original.type_ is eLootTable.entity:
        use_helper = True

        if adv_link.selector == 'player':
            conditions = EntityKilledPlayer()
            killed_trigger_type = eTrigger.entity_killed_player
        else:
            conditions = PlayerKilledEntity()
            conditions.entity = Entity()
            if 'sheep' in mcrData.loot_table_maps[adv_link.selector].path:
                conditions.entity.type_ = 'minecraft:sheep'
                conditions.entity['Color'] = sheep_color_to_number[adv_link.selector]
            else:
                conditions.entity.type_ = get_minecraft_selector(
                    adv_link.selector)
            killed_trigger_type = eTrigger.player_killed_entity

        mcrData.advancements[helper_selector] = Advancement()
        mcrData.advancements[helper_selector].criteria = {
            'kill': Criteria.populate(killed_trigger_type, conditions)
        }

        mcrData.advancements[helper_selector].rewards = Rewards()
        mcrData.advancements[helper_selector].rewards.function = namespaced_helper
        mcrData.functions[helper_selector].custom(
            f'scoreboard players set @a {objective} 1')

        mcrData.functions['tick'].execute().as_('@a').if_score_matches('@s',
                                                                       objective, '1..').at('@s').run(selector_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(get_item_entity(adv_child, 64))
        ]

        reset_objective = True
        grant_target_selector = ''

    elif adv_link.selector == 'fishing':
        use_helper = True

        conditions = FishingRodHooked()

        mcrData.advancements[helper_selector] = Advancement()
        mcrData.advancements[helper_selector].criteria = {
            'fish': Criteria.populate(eTrigger.fishing_rod_hooked, conditions)
        }

        mcrData.advancements[helper_selector].rewards = Rewards()
        mcrData.advancements[helper_selector].rewards.function = namespaced_helper
        mcrData.functions[helper_selector].custom(
            f'scoreboard players set @a {objective} 1')

        mcrData.functions['tick'].execute().as_('@a').if_score_matches('@s',
                                                                       objective, '1..').at('@s').run(selector_function)

        parent_name = get_upper_selector(adv_link.selector)
        # TODO figure what went wrong here?
        mcrData.advancements[pathed_selector].display.description = f'{parent_name} Loot Table Reference'

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(get_item_entity(adv_child, 64))
        ]

        reset_objective = True
        grant_target_selector = ''

    else:
        raise Exception(f'No Problem!\r\n{adv_link}\r\nDidn\'t Work!')

    generate_children_functions(
        mcrData, pathed_selector, adv_link, path, base, child_index, execute_conditions_list)

    mcrData.functions['reset'].append(
        f'scoreboard objectives add {objective} {objective_criteria}')
    mcrData.functions['setup'].append(
        f'scoreboard players set @s {objective} 0')
    mcrData.functions['remove'].append(
        f'scoreboard objectives remove {objective}')

    if reset_objective:
        mcrData.functions[pathed_selector].append(
            f'scoreboard players set @s {objective} 0')
    if use_helper:
        mcrData.functions[pathed_selector].append(
            f'advancement revoke @s[scores = {{ mcr_incomplete = 1.. }}] only {namespaced_helper}')

    (mcrData.functions[pathed_selector]
        .custom(f'advancement grant @s{grant_target_selector} only {namespaced_selector}')
        .custom(f'scoreboard players reset @s[scores = {{ mcr_incomplete = 0 }}] {objective}')
     )

    show_debug = mcArgs.Objective('show debug')

    (mcrData.functions[pathed_selector]
        .execute().if_score_matches('@s', show_debug, 1).run(f'tell @s @s triggered {namespaced_selector} : obj {objective}')
        .execute().if_score_matches('@s', show_debug, 1).run('tellraw @s [{ "text": "complete:"}, { "score": { "name": "@s", "objective": "mcr_complete" } }, { "text": ", mcr_incomplete:" },{ "score": { "name": "@s", "objective": "incomplete" } }]')
     )

    return objective_num


def generate_single_advancement(mcrData: MCRData, current_advs_and_recipes: list[Union[Advancement, Recipe]], adv_link: AdvItem, pathed_selector: str, namespaced_parent_selector: Optional[str] = None, parent_item_selector: Optional[str] = None, parent_item_is_correct: bool = False, hidden: bool = True, gen_base_criteria: bool = True, show: bool = True, announce: bool = True):
    selector = adv_link.selector
    cap_name = get_upper_selector(selector)
    item_selector = get_minecraft_selector(adv_link.item_selector)

    if parent_item_selector is not None:
        recipe = generate_recipe(RecipeInfo(pathed_selector, parent_item_selector, parent_item_is_correct,
                                            item_selector, adv_link.selector == adv_link.item_selector, adv_link.selector))

        mcrData.recipes[pathed_selector] = recipe
        current_advs_and_recipes.append(recipe)

    advancement = Advancement()
    if adv_link.adv_item_type is eAdvItemType.root or adv_link.adv_item_type is eAdvItemType.root_table:
        advancement.rewards = Rewards()
        advancement.rewards.recipes = [
            get_namespaced_selector(mcrData.datapack_name, pathed_selector)]

    advancement.display = Display.populate(
        icon=item_selector,
        title=adv_link.title if adv_link.title is not None else cap_name,
        description='No Description',
        frame=adv_link.frame,
        show=show,
        announce=announce,
        hidden=hidden
    )

    if namespaced_parent_selector is not None:
        advancement.parent = namespaced_parent_selector
    else:
        advancement.display.background = 'minecraft:textures/block/dirt.png'

    if gen_base_criteria:
        advancement.criteria = {'get': Criteria.populate(eTrigger.impossible)}

    mcrData.advancements[pathed_selector] = advancement
    current_advs_and_recipes.append(advancement)


def get_parent_tab(loot_table_map: LootTableMap):
    if loot_table_map.original.type_ is eLootTable.advancement_reward:
        return 'advancement_reward'
    elif loot_table_map.original.type_ is eLootTable.block:
        return 'blocks'
    elif loot_table_map.original.type_ is eLootTable.chest:
        if 'village' in loot_table_map.path:
            return 'village_chests'
        else:
            return 'chests'
    elif loot_table_map.original.type_ is eLootTable.entity:
        if 'sheep' in loot_table_map.path or loot_table_map.selector == 'sheep':
            return 'sheep'
        else:
            return 'entities'
    elif loot_table_map.original.type_ is eLootTable.fishing:
        return 'fishing'
    elif loot_table_map.original.type_ is eLootTable.generic:
        return 'generic_tables'
    elif loot_table_map.original.type_ is eLootTable.gift:
        return 'gifts'
    elif loot_table_map.original.type_ is eLootTable.empty:
        return 'no_parent'
    else:
        return 'no_parent'


def _generate_advancements(mcrData: MCRData, loot_table_map: LootTableMap):
    current_advs_and_recipes: list[Union[Advancement, Recipe]] = []

    parent = get_parent_tab(loot_table_map)
    pathed_parent = get_namespaced_selector(mcrData.datapack_name, parent)
    parent_selector = parent
    parent_item_selector = get_minecraft_selector(mcrData.mcr_item)
    parent_item_is_correct = False

    base = loot_table_map.selector
    path = loot_table_map.file_path

    first_path = get_pathed_selector(
        loot_table_map.selector, path, base, 0)
    pathed_selector = first_path

    from_items_length = 0
    child_pathed_parent = None

    column = 0

    current_obj_num = 0

    for link_index in range(0, len(loot_table_map.adv_chain)):
        loot_table_map.adv_length += 1

        adv_link = loot_table_map.adv_chain[link_index]

        if adv_link.adv_item_type is eAdvItemType.from_items and child_pathed_parent is not None:
            loot_table_map.adv_length += from_items_length
            from_items_length = 0
            pathed_parent = child_pathed_parent

        pathed_selector = get_pathed_selector(
            adv_link.selector, path, base, link_index)
        generate_single_advancement(mcrData, current_advs_and_recipes, adv_link,
                                    pathed_selector, pathed_parent, parent_item_selector, parent_item_is_correct)

        parent_selector = adv_link.selector
        parent_item_selector = f'minecraft:{adv_link.item_selector}'
        parent_item_is_correct = adv_link.item_selector == adv_link.selector
        pathed_parent = get_namespaced_selector(
            mcrData.datapack_name, pathed_selector)

        if parent_selector in loot_table_map.adv_branches:
            child_pathed_parent = pathed_parent
            branch = loot_table_map.adv_branches[parent_selector]
            split = False
            branch_length = len(branch)
            if link_index == len(loot_table_map.adv_chain) - 1:
                split = branch_length > 6
                column = 0
                if not split:
                    loot_table_map.adv_length += branch_length

            for adv_child in branch:
                child_pathed_selector = get_pathed_selector(
                    adv_child.selector, path, base, link_index + 1)
                generate_single_advancement(mcrData, current_advs_and_recipes, adv_child, child_pathed_selector,
                                            child_pathed_parent, parent_item_selector, parent_item_is_correct)
                child_pathed_parent = get_namespaced_selector(
                    mcrData.datapack_name, child_pathed_selector)
                from_items_length += 1
                if split:
                    column += 1
                    loot_table_map.adv_length += 0.5
                    if column >= branch_length / 2:
                        child_pathed_parent = pathed_parent
                        column = 0

        current_obj_num = generate_conditions(
            mcrData, pathed_selector, adv_link, path, base, link_index, current_obj_num)

    tab_name = parent
    if parent != 'fishing':
        if loot_table_map.adv_length == 1:
            tab_name = 'no_drops'
        elif loot_table_map.adv_length < 8:
            tab_name = f'{parent}_short'
        elif loot_table_map.adv_length < 16 and parent == 'entities':
            tab_name = f'{parent}_medium_short'
        elif loot_table_map.adv_length >= 24 and parent == 'entities':
            tab_name = f'{parent}_long'

        mcrData.advancements[first_path].parent = get_namespaced_selector(
            mcrData.datapack_name, tab_name)

    if tab_name not in mcrData.tabs:
        mcrData.tabs.append(tab_name)

    if tab_name not in mcrData.tabbed_advs_and_recipes:
        mcrData.tabbed_advs_and_recipes[tab_name] = []
    mcrData.tabbed_advs_and_recipes[tab_name].extend(current_advs_and_recipes)


def GetZipBytes(mcrData: MCRData) -> io.BytesIO:

    zipbytes = io.BytesIO()
    zip_ = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

    for file_name, loot_table_map in mcrData.loot_table_maps.items():
        zip_.writestr(os.path.join('data', 'minecraft', 'loot_tables',
                                   loot_table_map.file_path, f'{file_name}.json'), loot_table_map.contents)

    for full_path, advancement in mcrData.advancements.items():
        zip_.writestr(os.path.join(
            'data', mcrData.datapack_name, 'advancements', f'{full_path}.json'), json.dumps(advancement))

    for full_path, function_list in mcrData.functions.items():
        zip_.writestr(os.path.join(
            'data', mcrData.datapack_name, 'functions', f'{full_path}.mcfunction'), '\n'.join(function_list))

    for full_path, recipe in mcrData.recipes.items():
        zip_.writestr(os.path.join(
            'data', mcrData.datapack_name, 'recipes', f'{full_path}.json'), json.dumps(recipe))

    zip_.writestr('pack.mcmeta', json.dumps(
        {'pack': {'pack_format': 1, 'description': mcrData.datapack_desc}}, indent=4))

    zip_.writestr('data/minecraft/tags/functions/load.json',
                  json.dumps({'values': [f'{mcrData.datapack_name}:load']}))
    zip_.writestr('data/minecraft/tags/functions/tick.json',
                  json.dumps({'values': [f'{mcrData.datapack_name}:tick']}))

    zip_.close()

    return zipbytes


def _initialize_functions(mcrData: MCRData):
    (mcrData.functions['load']
        .execute().unless_score_matches(mcArgs.Entity('debug'), mcArgs.Objective('mcr_loaded'), 1).run(datapack_func('add', mcrData.datapack_name))
        .custom('scoreboard objectives add mcr_loaded dummy')
        .custom('scoreboard players set debug mcr_loaded 1')
        .custom('scoreboard objectives add show_debug trigger ["",{"text":"Debug"}]')
        .custom('tellraw @a ["",{"text":"Loot table randomizer with notes, by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]')
     )
    (mcrData.functions['add']
        .custom('scoreboard objectives add mcr_setup dummy')
        .custom('scoreboard objectives add mcr_complete dummy')
        .custom('scoreboard objectives add mcr_incomplete dummy')
        .custom('scoreboard objectives add mcr_ref_complete dummy')
     )
    (mcrData.functions['tick']
        .execute().as_('@a').unless_score_matches('@a', mcArgs.Objective('mcr_setup'), 1).run(datapack_func('setup', mcrData.datapack_name))
     )
    (mcrData.functions['setup']
        .custom('scoreboard players set @s mcr_setup 1')
        .custom('tellraw @s ["",{"selector":"say mcr_setup @s\'s MCRandomizer","color":"green"}]')
     )
    (mcrData.functions['debug']
        .function(namespaced_func('reset', mcrData.datapack_name))
     )
    (mcrData.functions['reset']
        .custom('scoreboard players set debug mcr_loaded 0')
        .function(namespaced_func('remove', mcrData.datapack_name))
        .function(namespaced_func('load', mcrData.datapack_name))
     )
    (mcrData.functions['remove']
        .custom('scoreboard objectives remove mcr_setup')
        .custom('scoreboard objectives remove mcr_complete')
        .custom('scoreboard objectives remove mcr_incomplete')
        .custom('scoreboard objectives remove mcr_ref_complete')
     )
    (mcrData.functions['uninstall']
        .function(namespaced_func('remove', mcrData.datapack_name))
        .custom('scoreboard objectives remove mcr_loaded')
        .custom('scoreboard objectives remove show_debug')
     )


def _finalizeAdvTabs(mcrData: MCRData):

    page = 0
    for tab in mcrData.tabs:
        page += 1

        parent = f'mcr_tab_{page}'

        current_advs_and_recipes: list[Union[Advancement,
                                             Recipe]] = mcrData.tabbed_advs_and_recipes[tab]

        for stuff in current_advs_and_recipes:
            if isinstance(stuff, Advancement):
                # TODO another instance of what the heck happened is this datatype a union like Int range?
                stuff.display.description = f'On Randomizer Tab {page}'
                stuff.parent = parent
            elif isinstance(stuff, CraftingShaped):
                stuff.result.count = page

        tab_selector = get_pathed_selector(parent, '', '', -1)

        title = f'Randomizer Tab {page}'
        adv_tab = AdvItem(
            parent, eAdvItemType.tab, mcrData.mcr_item, title, 'A Randomizer Tab')

        generate_single_advancement(mcrData, current_advs_and_recipes, adv_tab, tab_selector, None, hidden=False,
                                    gen_base_criteria=False, show=False, announce=False)
        mcrData.advancements[tab_selector].criteria = {
            'take_notes': Criteria.populate(eTrigger.impossible)}
        mcrData.functions['debug'].append(
            f'advancement grant @a from {mcrData.datapack_name}:{tab_selector}')


def mc_randomizer(mcrData: MCRData, finishedCallback: Optional[Callable[..., Any]] = None, ):

    mcrData.printStep('Initializing Pack...')
    _initializePackInformation(mcrData)

    if mcrData.seed_generated:
        print('If you want to use a specific randomizer seed, include a seed in the list of arguments. ex: "python mc_randomize.py 12345" or "python mc_randomize.py seed=12345".')

        if not any(mcrData.flags):
            print('Customization is available through flags. If you would like to see a list of flags use: "python mc_randomizer.py -help"')

    print(f'flags: {mcrData.flags}')

    mcrData.printStep('Loading Tables...')
    _load_table_info(mcrData)

    mcrData.printStep('Randomizing drops...')
    _randomize(mcrData)

    mcrData.printStep('Validating loot tables...')
    for selector in mcrData.loot_table_maps:
        validate_conditions(mcrData.loot_table_maps[selector])

    mcrData.printStep('Populating Advancement chains...')
    _populate(mcrData)

    mcrData.printStep('Initialize MCFunctions...')
    _initialize_functions(mcrData)

    mcrData.printStep('Generating Advancements...')
    for loot_table_map in mcrData.loot_table_maps.values():
        if not loot_table_map.is_sub:
            _generate_advancements(mcrData, loot_table_map)

    mcrData.printStep('Finalizing Advancement Tabs...')
    _finalizeAdvTabs(mcrData)

    mcrData.printStep('Writing Files...')
    zipbytes = GetZipBytes(mcrData)
    files = [('Compressed (zipped) Folders', '*.zip')]

    file: io.BufferedWriter
    with asksaveasfile(mode='wb', filetypes=files, defaultextension='.zip', initialfile='a name') as file:
        file.write(zipbytes.getvalue())

    mcrData.printStep(f'Created datapack "{mcrData.datapack_filename}".')
    mcrData.printDetail('The program can now be closed.')

    if finishedCallback is not None:
        finishedCallback()
