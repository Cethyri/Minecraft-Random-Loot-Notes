import io
import json
import os
import random
import zipfile
from dataclasses import dataclass
from tkinter.filedialog import asksaveasfile
from typing import Any, Callable, IO, Optional, Union

import mcr.mc.commands.argument_types as mcArgs
from mcr.helpers.regex import get_upper_name, shorten_name
from mcr.loot_table_map import AdvItem, LootTableMap, eAdvItemType
from mcr.mc.commands.execute import Execute
from mcr.mc.commands.function import Function
from mcr.mc.commands.mcfunction import MCFunction
from mcr.mc.data_structures.advancement import Advancement, Rewards
from mcr.mc.data_structures.criteria import (
    Criteria,
    EntityKilledPlayer,
    FishingRodHooked,
    PlayerKilledEntity,
    eTrigger,
)
from mcr.mc.data_structures.function import Function as ltFunction, eFunction
from mcr.mc.data_structures.display import Display
from mcr.mc.data_structures.entity import Entity
from mcr.mc.data_structures.loot_table import LootTable, eLootTable
from mcr.mc.data_structures.nbt import NBT, NBTPath, Tag_Byte, Tag_Short
from mcr.mc.data_structures.recipe import (
    CraftingShaped,
    Ingredient,
    Recipe,
    Result,
    eRecipe,
)
from mcr.mcr_data import MCRData
from mcr.populate_advancement_chain import populate_advancement_chain
from mcr.validation import validate_conditions

TEMP_DIR = "mc_temp_dir"
TOTAL_STEPS = 11


def initialize_pack_info(mcr_data: MCRData):
    mcr_data.datapack_filename = mcr_data.datapack_name

    if not mcr_data.flags.hide_seed:
        mcr_data.datapack_filename += f"(seed={mcr_data.seed})"

    random.seed(mcr_data.seed)
    mcr_data.datapack_desc = f"Minecraft Randomizer, Seed: {mcr_data.seed}"

    mcr_data.notesGrantSelector = "@s"
    if mcr_data.flags.co_op:
        mcr_data.notesGrantSelector = "@a"

    with open("mcr/mc/data/requires_cheats.json") as json_file:
        mcr_data.requires_cheats = json.load(json_file)

    with open("mcr/mc/data/double_tall_blocks.json") as json_file:
        mcr_data.double_tall_blocks = json.load(json_file)


def load_table_info(
    mcr_data: MCRData, file_path: str, table_name: str
) -> Optional[LootTable]:
    if (table_name == "player" and mcr_data.flags.hardcore) or (
        table_name in mcr_data.requires_cheats and mcr_data.flags.no_cheats
    ):
        return None

    with open(file_path) as json_file:
        json_text = json_file.read().replace("\n", "")

    loot_table = LootTable(json.loads(json_text))

    if (
        "pools" not in loot_table or len(loot_table.pools) == 0
    ) and mcr_data.flags.no_dead_ends:
        return None

    return loot_table


def load_all_table_info(mcr_data: MCRData):
    loot_table_path = os.path.join(
        TEMP_DIR, mcr_data.jarname, "data", "minecraft", "loot_tables"
    )

    loot_table: Optional[LootTable]

    for dirpath, _, filenames in os.walk(loot_table_path):
        for filename in filenames:
            table_name = filename.replace(".json", "")
            relative_path = dirpath.replace(loot_table_path + os.path.sep, "").split(
                os.path.sep
            )
            file_path = os.path.join(dirpath, filename)

            loot_table = load_table_info(mcr_data, file_path, table_name)

            if loot_table is None:
                continue

            mcr_data.loot_table_maps[table_name] = LootTableMap(
                table_name, relative_path, loot_table
            )       


def randomize(mcr_data: MCRData):
    """
    Instantiates a loot table map for every loot table and pairs each with a target loot table.
    The original is a reference for the source, target is a reference for the drops, both are a reference for the conditions.
    """
    target_maps: list[LootTableMap] = list(mcr_data.loot_table_maps.values())
    random.shuffle(target_maps)

    for loot_table_map, target_map in zip(
        mcr_data.loot_table_maps.values(), target_maps
    ):

        loot_table_map.target_name = target_map.name

        loot_table_map.target = LootTable(
            json.loads(json.dumps(target_map.original))
        )  # Deep Copy

        
def add_nbt_setter(loot_table_map: LootTableMap):
    set_nbt = ltFunction.populate(eFunction.set_nbt, {'tag': json.dumps({'mcr_val': loot_table_map.name})})
    if ('functions' not in loot_table_map.target or loot_table_map.target.functions is None):
        loot_table_map.target.functions = [set_nbt]
    else:
        loot_table_map.target.functions.extend([set_nbt])


def populate_chains(mcr_data: MCRData):
    current_map: LootTableMap
    for name, loot_table_map in mcr_data.loot_table_maps.items():

        populate_advancement_chain(name, mcr_data.loot_table_maps)

        for adv_item in loot_table_map.adv_chain:
            current_map = mcr_data.loot_table_maps[adv_item.name]
            if not adv_item.name == name:
                current_map.is_sub = not current_map.is_loop


sheep_color_to_number: dict[str, int] = {
    "white": 0,
    "orange": 1,
    "magenta": 2,
    "light_blue": 3,
    "yellow": 4,
    "lime": 5,
    "pink": 6,
    "gray": 7,
    "light_gray": 8,
    "cyan": 9,
    "purple": 10,
    "blue": 11,
    "brown": 12,
    "green": 13,
    "red": 14,
    "black": 15,
}


def get_pathed_name(name: str, path: str, base: str, link_index: int):
    name = f"{link_index}-{name}" if link_index >= 0 else name
    return os.path.join(path, base, name).replace(os.path.sep, "/")


@dataclass
class RecipeInfo:
    pathed_name: str
    parent_item_name: mcArgs.NamespacedId
    parent_item_is_correct: bool
    child_item_name: mcArgs.NamespacedId
    child_item_is_correct: bool
    group_name: str


def generate_recipe(rInfo: RecipeInfo):
    recipe = CraftingShaped()
    recipe.type_ = eRecipe.crafting_shaped
    recipe.group = f"rl_notes_{rInfo.group_name}"
    recipe.pattern = [
        f'{" " if rInfo.parent_item_is_correct and rInfo.child_item_is_correct else "B"}I',
        "PK",
    ]

    knowledge_book = Ingredient()
    knowledge_book.item = "minecraft:knowledge_book"
    parent = Ingredient()
    parent.item = str(rInfo.parent_item_name)
    child = Ingredient()
    child.item = str(rInfo.child_item_name)
    barrier = Ingredient()
    barrier.item = "minecraft:barrier"

    recipe.key = {"I": child, "P": parent, "K": knowledge_book, "B": barrier}
    if rInfo.parent_item_is_correct and rInfo.child_item_is_correct:
        del recipe.key["B"]

    recipe.result = Result()
    recipe.result.count = 1
    recipe.result.item = str(rInfo.child_item_name)

    return recipe


def generate_children_functions(
    mcr_data: MCRData,
    pathed_name: str,
    start_link: AdvItem,
    path: str,
    base: str,
    child_index: int,
    execute_conditions_list: list[Callable[..., Any]],
):
    (mcr_data.functions[pathed_name]
    .custom('scoreboard players set @s mcr_incomplete 0')
    .custom('scoreboard players set @s mcr_complete 0'))

    references: list[str] = []
    search_queue = [start_link]
    reference_namespaced_ids = {}

    cur_link: AdvItem
    current_map: LootTableMap

    is_reference = False

    while len(search_queue) > 0:
        cur_link = search_queue.pop()
        current_map = mcr_data.loot_table_maps[cur_link.name]

        if is_reference:
            (mcr_data.functions[pathed_name]
            .custom('scoreboard players set @s mcr_ref_complete 0'))

        references.append(current_map.name)

        branches: list[AdvItem] = []
        if cur_link.name in current_map.adv_branches:
            branches.extend(current_map.adv_branches[cur_link.name])
        if (
            len(current_map.adv_chain) > 1
            and current_map.adv_chain[1].adv_item_type is not eAdvItemType.from_items
        ):
            branches.append(current_map.adv_chain[1])

        for adv_child in branches:
            child_pathed_name = get_pathed_name(
                adv_child.name, path, base, 1 if is_reference else child_index
            )

            namespaced_id = mcr_data.datapack_id(child_pathed_name)
            if (
                adv_child.adv_item_type is not eAdvItemType.reference
                and adv_child.name == adv_child.item_name
            ):
                for execute_conditions in execute_conditions_list:
                    mcr_data.functions[pathed_name].execute(
                        f"execute{execute_conditions(adv_child)}"
                    ).run(f"advancement grant @s only {namespaced_id}")
                (
                    mcr_data.functions[pathed_name]
                    .custom(
                        f"recipe give @s[advancements = {{ {namespaced_id} = true }}] {namespaced_id}"
                    )
                    .custom(
                        f"scoreboard players add @s[advancements = {{ {namespaced_id} = true }}] mcr_complete 1"
                    )
                    .custom(
                        f"scoreboard players add @s[advancements = {{ {namespaced_id} = false }}] mcr_incomplete 1"
                    )
                )

                if is_reference:
                    mcr_data.functions[pathed_name].custom(
                        f"scoreboard players add @s[advancements = {{ {namespaced_id} = true }}] mcr_ref_complete 1"
                    )

            elif (
                adv_child.adv_item_type is eAdvItemType.reference
                and adv_child.name not in references
            ):
                search_queue.append(adv_child)
                reference_namespaced_ids[adv_child.name] = namespaced_id

        if is_reference:
            root_namespaced_id = mcr_data.datapack_id(
                get_pathed_name(cur_link.name, path, base, 0)
            )
            (
                mcr_data.functions[pathed_name]
                .custom(
                    f"advancement grant @s[scores = {{ mcr_ref_complete = 1.. }}] only {reference_namespaced_ids[cur_link.name]}"
                )
                .custom(
                    f"advancement grant @s[scores = {{ mcr_ref_complete = 1.. }}] only {root_namespaced_id}"
                )
            )
        else:
            is_reference = True


def generate_conditions(
    mcr_data: MCRData,
    pathed_name: str,
    adv_link: AdvItem,
    path: str,
    base: str,
    link_index: int,
    objective_num: int,
) -> int:

    if pathed_name in mcr_data.functions:
        mcr_data.printDetail("Warning: duplicate function!")

    loot_table_map = mcr_data.loot_table_maps[adv_link.name]

    helper_name = f"helper/{pathed_name}"
    namespaced_helper = mcr_data.datapack_id(helper_name)
    namespaced_id = mcr_data.datapack_id(pathed_name)
    named_function = Function(namespaced_id)

    adv_namespaced_id = mcArgs.NamespacedId(adv_link.name)

    mcr_data.functions[pathed_name] = MCFunction()

    objective_name = f"{shorten_name(adv_link.name)}_r{objective_num}"
    objective = mcArgs.Objective(objective_name)
    if len(objective_name) > 16:
        mcr_data.printDetail(objective_name)
    objective_num += 1
    objective_criteria = "dummy"
    use_helper = False
    reset_objective = False
    execute_conditions_list: list[Callable[[AdvItem], Execute[None]]]
    grant_target_selector = "[scores = { mcr_incomplete = 0 }]"
    child_index = link_index + 1

    def get_item_entity(adv_child: AdvItem, distance: Union[int, float]):
        return mcArgs.Entity(
            "@e",
            distance=f"..{distance}",
            type="minecraft:item",
            limit=1,
            nbt=NBT(
                {
                    "Age": Tag_Short(0),
                    "Item": {"id": f"minecraft:{adv_child.item_name}"},
                }
            ),
        )

    if adv_link.name == "sheep" or "fishing" in loot_table_map.path:
        return objective_num

    elif adv_link.name == "armor_stand":
        # TODO check if get_item_entity needs 'armor_stand' explicitly
        mcr_data.functions["tick"].execute().as_("@a").if_score_matches(
            "@s", objective, "..0"
        ).at("@s").at(get_item_entity(adv_link, 8)).run(named_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(
                get_item_entity(adv_child, 2)
            )
        ]

        grant_target_selector = ""

    elif adv_link.name in mcr_data.double_tall_blocks:
        for i in range(10):
            score = i + 1
            distance = score / 2
            pos = mcArgs.Vec3(z=distance, rel="^")
            (
                mcr_data.functions["tick"]
                .execute()
                .as_("@a")
                .if_score_matches("@s", objective, "0")
                .at("@s")
                .anchored("eyes")
                .if_block(pos, adv_namespaced_id)
                .run(f"scoreboard players set @s {objective} {score}")
                .execute()
                .as_("@a")
                .if_score_matches("@s", objective, score)
                .at("@s")
                .anchored("eyes")
                .unless_block(pos, adv_namespaced_id)
                .positioned(pos)
                .run(named_function)
            )

        execute_conditions_list = [
            lambda adv_child: Execute.conditions()
            .unless_block(mcArgs.Vec3().loc, adv_namespaced_id)
            .if_entity(get_item_entity(adv_child, 2))
        ]

        reset_objective = True
        grant_target_selector = ""

    elif loot_table_map.original.type_ is eLootTable.block:
        objective_criteria = f"minecraft.mined:minecraft.{adv_link.name}"

        mcr_data.functions["tick"].execute().as_("@a").if_score_matches(
            "@s", objective, "1.."
        ).at("@s").run(named_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(
                get_item_entity(adv_child, 8)
            )
        ]

        reset_objective = True
        grant_target_selector = ""

    elif loot_table_map.original.type_ is eLootTable.chest:
        loot_table_pathed_name = get_pathed_name(adv_link.name, path, "", -1)

        for i in range(10):
            score = i + 1
            distance = score / 2
            pos = mcArgs.Vec3(z=distance, rel="^")
            block = mcArgs.NamespacedId(
                f'chest{{ LootTable: "minecraft:{loot_table_pathed_name}" }}'
            )
            (
                mcr_data.functions["tick"]
                .execute()
                .as_("@a")
                .if_score_matches("@s", objective, 0)
                .at("@s")
                .anchored("eyes")
                .if_block(pos, block)
                .run(f"scoreboard players set @s {objective} {score}")
                .execute()
                .as_("@a")
                .if_score_matches("@s", objective, score)
                .at("@s")
                .anchored("eyes")
                .unless_block(pos, block)
                .positioned(pos)
                .run(named_function)
            )

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_block(
                mcArgs.Vec3().rel(),
                mcArgs.NamespacedId(
                    f'chest{{ Items: [{{ id: "minecraft:{adv_child.item_name}" }}] }}'
                ),
            )
        ]

        reset_objective = True

    elif (
        loot_table_map.original.type_ is eLootTable.gift
        and "hero_of_the_village" in loot_table_map.path
    ):
        villager_type = adv_link.name.replace("_gift", "")

        as_selector = mcArgs.Entity(
            "@a", nbt=NBT({"ActiveEffects": [{"Id": Tag_Byte(32)}]})
        )
        at_selector = mcArgs.Entity(
            "@e",
            distance="..8",
            type="minecraft:villager",
            nbt=NBT({"VillagerData": {"profession": f"minecraft:{villager_type}"}}),
        )

        mcr_data.functions["tick"].execute().as_(as_selector).if_score_matches(
            "@s", objective, "0.."
        ).at("@s").at(at_selector).run(named_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(
                get_item_entity(adv_child, 2)
            )
        ]

    elif adv_link.name == "cat_morning_gift":
        sleeptimerCheck = NBTPath({"SleepTimer": Tag_Short(101)})

        mcr_data.functions["tick"].execute().as_("@a").if_data_entity(
            "@s", sleeptimerCheck
        ).at("@s").at(mcArgs.Entity("@e", distance="..16", type="minecraft:cat")).run(
            named_function
        )

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(
                get_item_entity(adv_child, 4)
            ),
            lambda adv_child: Execute.conditions().as_(
                mcArgs.Entity(
                    "@s",
                    nbt=NBT(
                        {"Inventory": [{"id": f"minecraft:{adv_child.item_name}"}]}
                    ),
                )
            ),
        ]

    elif loot_table_map.original.type_ is eLootTable.entity:
        use_helper = True

        if adv_link.name == "player":
            conditions = EntityKilledPlayer()
            killed_trigger_type = eTrigger.entity_killed_player
        else:
            conditions = PlayerKilledEntity()
            conditions.entity = Entity()
            if "sheep" in mcr_data.loot_table_maps[adv_link.name].path:
                conditions.entity.type_ = "minecraft:sheep"
                conditions.entity["Color"] = sheep_color_to_number[adv_link.name]
            else:
                conditions.entity.type_ = str(mcArgs.NamespacedId(adv_link.name))
            killed_trigger_type = eTrigger.player_killed_entity

        mcr_data.advancements[helper_name] = Advancement()
        mcr_data.advancements[helper_name].criteria = {
            "kill": Criteria.populate(killed_trigger_type, conditions)
        }

        mcr_data.advancements[helper_name].rewards = Rewards()
        mcr_data.advancements[helper_name].rewards.function = str(namespaced_helper)
        mcr_data.functions[helper_name].custom(
            f"scoreboard players set @a {objective} 1"
        )

        mcr_data.functions["tick"].execute().as_("@a").if_score_matches(
            "@s", objective, "1.."
        ).at("@s").run(named_function)

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(
                get_item_entity(adv_child, 64)
            )
        ]

        reset_objective = True
        grant_target_selector = ""

    elif adv_link.name == "fishing":
        use_helper = True

        conditions = FishingRodHooked()

        mcr_data.advancements[helper_name] = Advancement()
        mcr_data.advancements[helper_name].criteria = {
            "fish": Criteria.populate(eTrigger.fishing_rod_hooked, conditions)
        }

        mcr_data.advancements[helper_name].rewards = Rewards()
        mcr_data.advancements[helper_name].rewards.function = str(namespaced_helper)
        mcr_data.functions[helper_name].custom(
            f"scoreboard players set @a {objective} 1"
        )

        mcr_data.functions["tick"].execute().as_("@a").if_score_matches(
            "@s", objective, "1.."
        ).at("@s").run(named_function)

        parent_name = get_upper_name(adv_link.name)
        mcr_data.advancements[
            pathed_name
        ].display.description = f"{parent_name} Loot Table Reference"

        execute_conditions_list = [
            lambda adv_child: Execute.conditions().if_entity(
                get_item_entity(adv_child, 64)
            )
        ]

        reset_objective = True
        grant_target_selector = ""

    elif loot_table_map.original.type_ is eLootTable.barter:
        execute_conditions_list = []

    else:
        raise Exception(f"No Problem!\r\n{adv_link}\r\nDidn't Work!")

    generate_children_functions(
        mcr_data,
        pathed_name,
        adv_link,
        path,
        base,
        child_index,
        execute_conditions_list,
    )

    mcr_data.functions["reset"].append(
        f"scoreboard objectives add {objective} {objective_criteria}"
    )
    mcr_data.functions["setup"].append(f"scoreboard players set @s {objective} 0")
    mcr_data.functions["add"].append(f"scoreboard objectives add {objective} {objective_criteria}")
    mcr_data.functions["remove"].append(f"scoreboard objectives remove {objective}")

    if reset_objective:
        mcr_data.functions[pathed_name].append(
            f"scoreboard players set @s {objective} 0"
        )
    if use_helper:
        mcr_data.functions[pathed_name].append(
            f"advancement revoke @s[scores = {{ mcr_incomplete = 1.. }}] only {namespaced_helper}"
        )

    (
        mcr_data.functions[pathed_name]
        .custom(f"advancement grant @s{grant_target_selector} only {namespaced_id}")
        .custom(
            f"scoreboard players reset @s[scores = {{ mcr_incomplete = 0 }}] {objective}"
        )
    )

    show_debug = mcArgs.Objective("show_debug")

    (
        mcr_data.functions[pathed_name]
        .execute()
        .if_score_matches("@s", show_debug, 1)
        .run(f"tell @s @s triggered {namespaced_id} : obj {objective}")
        .execute()
        .if_score_matches("@s", show_debug, 1)
        .run(
            'tellraw @s [{ "text": "complete:"}, { "score": { "name": "@s", "objective": "mcr_complete" } }, { "text": ", mcr_incomplete:" },{ "score": { "name": "@s", "objective": "incomplete" } }]'
        )
    )

    return objective_num


def generate_single_advancement(
    mcr_data: MCRData,
    current_advs_and_recipes: list[Advancement | Recipe],
    adv_link: AdvItem,
    pathed_name: str,
    parent_namespaced_id: mcArgs.NamespacedId | None = None,
    parent_item_name: mcArgs.NamespacedId | None = None,
    parent_item_is_correct: bool = False,
    hidden: bool = True,
    gen_base_criteria: bool = True,
    show: bool = True,
    announce: bool = True,
):
    name = adv_link.name
    cap_name = get_upper_name(name)
    item_id = mcArgs.NamespacedId(adv_link.item_name)

    if parent_item_name is not None:
        recipe = generate_recipe(
            RecipeInfo(
                pathed_name,
                parent_item_name,
                parent_item_is_correct,
                item_id,
                adv_link.name == adv_link.item_name,
                adv_link.name,
            )
        )

        mcr_data.recipes[pathed_name] = recipe
        current_advs_and_recipes.append(recipe)

    advancement = Advancement()
    if (
        adv_link.adv_item_type is eAdvItemType.root
        or adv_link.adv_item_type is eAdvItemType.root_table
    ):
        advancement.rewards = Rewards()
        advancement.rewards.recipes = [str(mcr_data.datapack_id(pathed_name))]

    advancement.display = Display.populate(
        icon=str(item_id),
        title=adv_link.title if adv_link.title is not None else cap_name,
        description="No Description",
        frame=adv_link.frame,
        show=show,
        announce=announce,
        hidden=hidden,
    )

    if parent_namespaced_id is not None:
        advancement.parent = str(parent_namespaced_id)
    else:
        advancement.display.background = "minecraft:textures/block/dirt.png"

    if gen_base_criteria:
        advancement.criteria = {"get": Criteria.populate(eTrigger.impossible)}

    mcr_data.advancements[pathed_name] = advancement
    current_advs_and_recipes.append(advancement)


def get_parent_tab(loot_table_map: LootTableMap):
    match loot_table_map.original.type_:
        case eLootTable.advancement_reward:
            return "advancement_reward"
        case eLootTable.block:
            return "blocks"
        case eLootTable.chest:
            if "village" in loot_table_map.path:
                return "village_chests"
            return "chests"
        case eLootTable.entity:
            if "sheep" in loot_table_map.path or loot_table_map.name == "sheep":
                return "sheep"
            return "entities"
        case eLootTable.fishing:
            return "fishing"
        case eLootTable.generic:
            return "generic_tables"
        case eLootTable.gift:
            return "gifts"
        case eLootTable.empty:
            return "no_parent"
        case _:
            return "no_parent"


def generate_advancements(mcr_data: MCRData, loot_table_map: LootTableMap):
    current_advs_and_recipes: list[Union[Advancement, Recipe]] = []

    parent = get_parent_tab(loot_table_map)
    pathed_parent = mcr_data.datapack_id(parent)
    parent_name = parent
    parent_item_id = mcArgs.NamespacedId(mcr_data.mcr_item)
    parent_item_is_correct = False

    base = loot_table_map.name
    path = loot_table_map.file_path

    first_path = get_pathed_name(loot_table_map.name, path, base, 0)
    pathed_name = first_path

    from_items_length = 0
    child_pathed_parent = None

    column = 0

    current_obj_num = 0

    for link_index in range(0, len(loot_table_map.adv_chain)):
        loot_table_map.adv_length += 1

        adv_link = loot_table_map.adv_chain[link_index]

        if (
            adv_link.adv_item_type is eAdvItemType.from_items
            and child_pathed_parent is not None
        ):
            loot_table_map.adv_length += from_items_length
            from_items_length = 0
            pathed_parent = child_pathed_parent

        pathed_name = get_pathed_name(adv_link.name, path, base, link_index)
        generate_single_advancement(
            mcr_data,
            current_advs_and_recipes,
            adv_link,
            pathed_name,
            pathed_parent,
            parent_item_id,
            parent_item_is_correct,
        )

        parent_name = adv_link.name
        parent_item_id = mcArgs.NamespacedId(adv_link.item_name)
        parent_item_is_correct = adv_link.item_name == adv_link.name
        pathed_parent = mcr_data.datapack_id(pathed_name)

        if parent_name in loot_table_map.adv_branches:
            child_pathed_parent = pathed_parent
            branch = loot_table_map.adv_branches[parent_name]
            split = False
            branch_length = len(branch)
            if link_index == len(loot_table_map.adv_chain) - 1:
                split = branch_length > 6
                column = 0
                if not split:
                    loot_table_map.adv_length += branch_length

            for adv_child in branch:
                child_pathed_name = get_pathed_name(
                    adv_child.name, path, base, link_index + 1
                )
                generate_single_advancement(
                    mcr_data,
                    current_advs_and_recipes,
                    adv_child,
                    child_pathed_name,
                    child_pathed_parent,
                    parent_item_id,
                    parent_item_is_correct,
                )
                child_pathed_parent = mcr_data.datapack_id(child_pathed_name)
                from_items_length += 1
                if split:
                    column += 1
                    loot_table_map.adv_length += 0.5
                    if column >= branch_length / 2:
                        child_pathed_parent = pathed_parent
                        column = 0

        current_obj_num = generate_conditions(
            mcr_data, pathed_name, adv_link, path, base, link_index, current_obj_num
        )

    tab_name = parent
    if parent != "fishing":
        if loot_table_map.adv_length == 1:
            tab_name = "no_drops"
        elif loot_table_map.adv_length < 8:
            tab_name = f"{parent}_short"
        elif loot_table_map.adv_length < 16 and parent == "entities":
            tab_name = f"{parent}_medium_short"
        elif loot_table_map.adv_length >= 24 and parent == "entities":
            tab_name = f"{parent}_long"

        mcr_data.advancements[first_path].parent = str(mcr_data.datapack_id(tab_name))

    if tab_name not in mcr_data.tabs:
        mcr_data.tabs.append(tab_name)

    if tab_name not in mcr_data.tabbed_advs_and_recipes:
        mcr_data.tabbed_advs_and_recipes[tab_name] = []
    mcr_data.tabbed_advs_and_recipes[tab_name].extend(current_advs_and_recipes)


def GetZipBytes(mcr_data: MCRData) -> io.BytesIO:

    zipbytes = io.BytesIO()
    zip_ = zipfile.ZipFile(zipbytes, "w", zipfile.ZIP_DEFLATED, False)

    for file_name, loot_table_map in mcr_data.loot_table_maps.items():
        zip_.writestr(
            os.path.join(
                "data",
                "minecraft",
                "loot_tables",
                loot_table_map.file_path,
                f"{file_name}.json",
            ),
            json.dumps(loot_table_map.target),
        )

    for full_path, advancement in mcr_data.advancements.items():
        zip_.writestr(
            os.path.join(
                "data", mcr_data.datapack_name, "advancements", f"{full_path}.json"
            ),
            json.dumps(advancement),
        )

    for full_path, function_list in mcr_data.functions.items():
        zip_.writestr(
            os.path.join(
                "data", mcr_data.datapack_name, "functions", f"{full_path}.mcfunction"
            ),
            str(function_list),
        )

    for full_path, recipe in mcr_data.recipes.items():
        zip_.writestr(
            os.path.join(
                "data", mcr_data.datapack_name, "recipes", f"{full_path}.json"
            ),
            json.dumps(recipe),
        )

    zip_.writestr(
        "data/minecraft/tags/functions/load.json",
        f'{{"values": ["{mcr_data.datapack_name}:load"]}}',
    )
    zip_.writestr(
        "data/minecraft/tags/functions/tick.json",
        f'{{"values": ["{mcr_data.datapack_name}:tick"]}}',
    )

    zip_.writestr(
        "pack.mcmeta",
        json.dumps(
            {"pack": {"pack_format": 7, "description": mcr_data.datapack_desc}},
            indent=4,
        ),
    )

    zip_.write("Icon.png", "pack.png")

    zip_.close()

    return zipbytes


def initialize_functions(mcr_data: MCRData):
    (
        mcr_data.functions["load"]
        .custom("scoreboard objectives add mcr_loaded dummy")
        .execute()
        .unless_score_matches(mcArgs.Entity("debug"), mcArgs.Objective("mcr_loaded"), 1)
        .run(Function(mcr_data.datapack_id("add")))
        .custom("scoreboard players set debug mcr_loaded 1")
        .custom('scoreboard objectives add show_debug trigger ["",{"text":"Debug"}]')
        .custom(
            'tellraw @a ["",{"text":"Loot table randomizer with notes, by Cethyrion, adapted from SethBling\'s Loot table randomizer","color":"green"}]'
        )
    )
    (
        mcr_data.functions["add"]
        .custom("scoreboard objectives add mcr_setup dummy")
        .custom("scoreboard objectives add mcr_complete dummy")
        .custom("scoreboard objectives add mcr_incomplete dummy")
        .custom("scoreboard objectives add mcr_ref_complete dummy")
    )
    (
        mcr_data.functions["tick"]
        .execute()
        .as_("@a")
        .unless_score_matches("@s", mcArgs.Objective("mcr_setup"), 1)
        .run(Function(mcr_data.datapack_id("setup")))
    )
    (
        mcr_data.functions["setup"]
        .custom("scoreboard players set @s mcr_setup 1")
        .custom(
            'tellraw @s ["",{"selector":"say mcr_setup @s\'s MCRandomizer","color":"green"}]'
        )
    )
    (mcr_data.functions["debug"].function(mcr_data.datapack_id("reset")))
    (
        mcr_data.functions["reset"]
        .custom("scoreboard players set debug mcr_loaded 0")
        .function(mcr_data.datapack_id("remove"))
        .function(mcr_data.datapack_id("load"))
    )
    (
        mcr_data.functions["remove"]
        .custom("scoreboard objectives remove mcr_setup")
        .custom("scoreboard objectives remove mcr_complete")
        .custom("scoreboard objectives remove mcr_incomplete")
        .custom("scoreboard objectives remove mcr_ref_complete")
    )
    (
        mcr_data.functions["uninstall"]
        .function(mcr_data.datapack_id("remove"))
        .custom("scoreboard objectives remove mcr_loaded")
        .custom("scoreboard objectives remove show_debug")
    )


def finalizeAdvTabs(mcr_data: MCRData):

    page = 0
    for tab in mcr_data.tabs:
        page += 1

        parent = f"mcr_tab_{page}"

        current_advs_and_recipes: list[
            Union[Advancement, Recipe]
        ] = mcr_data.tabbed_advs_and_recipes[tab]

        for stuff in current_advs_and_recipes:
            if isinstance(stuff, Advancement):
                stuff.display.description = f"On Randomizer Tab {page}"
                if (stuff.parent == str(mcr_data.datapack_id(tab))):
                    stuff.parent = str(mcr_data.datapack_id(parent))
            elif isinstance(stuff, CraftingShaped):
                stuff.result.count = page

        tab_name = parent

        title = f"Randomizer Tab {page}"
        adv_tab = AdvItem(
            parent, eAdvItemType.tab, mcr_data.mcr_item, title, "A Randomizer Tab"
        )

        generate_single_advancement(
            mcr_data,
            current_advs_and_recipes,
            adv_tab,
            tab_name,
            None,
            hidden=False,
            gen_base_criteria=False,
            show=False,
            announce=False,
        )
        mcr_data.advancements[tab_name].criteria = {
            "take_notes": Criteria.populate(eTrigger.impossible)
        }
        mcr_data.functions["debug"].append(
            f"advancement grant @a from {mcr_data.datapack_id(tab_name)}"
        )


def mc_randomizer(
    mcr_data: MCRData, finishedCallback: Optional[Callable[..., Any]] = None
):

    mcr_data.printStep("Initializing Pack...", 0)
    initialize_pack_info(mcr_data)

    if mcr_data.seed_generated:
        print(
            'If you want to use a specific randomizer seed, include a seed in the list of arguments. ex: "python mc_randomize.py 12345" or "python mc_randomize.py seed=12345".'
        )

        if not any(mcr_data.flags):
            print(
                'Customization is available through flags. If you would like to see a list of flags use: "python mc_randomizer.py -help"'
            )

    print(f"flags: {mcr_data.flags}")

    mcr_data.printStep("Loading Tables...")
    load_all_table_info(mcr_data)

    mcr_data.printStep("Randomizing drops...")
    randomize(mcr_data)

    mcr_data.printStep("Validating loot tables...")
    for loot_table_map in mcr_data.loot_table_maps.values():
        validate_conditions(loot_table_map)

    mcr_data.printStep("Adding NBT Setters...")
    for loot_table_map in mcr_data.loot_table_maps.values():
        add_nbt_setter(loot_table_map)

    mcr_data.printStep("Populating Advancement chains...")
    populate_chains(mcr_data)

    mcr_data.printStep("Initialize MCFunctions...")
    initialize_functions(mcr_data)

    mcr_data.printStep("Generating Advancements...")
    for loot_table_map in mcr_data.loot_table_maps.values():
        if not loot_table_map.is_sub:
            generate_advancements(mcr_data, loot_table_map)

    mcr_data.printStep("Finalizing Advancement Tabs...")
    finalizeAdvTabs(mcr_data)

    mcr_data.printStep("Writing Files...")
    zipbytes = GetZipBytes(mcr_data)
    files = [("Compressed (zipped) Folders", "*.zip")]

    file: Optional[IO[Any]] = asksaveasfile(
        mode="wb",
        filetypes=files,
        defaultextension=".zip",
        initialfile=mcr_data.datapack_filename,
    )
    if file:
        file.write(zipbytes.getvalue())
        file.close()

    mcr_data.printStep(f'Created datapack "{mcr_data.datapack_filename}".')
    mcr_data.printDetail("The program can now be closed.")

    if finishedCallback is not None:
        finishedCallback()
