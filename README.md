# RLNotes<img width="64px" align="left" src="Icon.png"><img width="64px" align="right" src="Icon.png">
RLNotes was inspired by and built upon Sethbling's Loot Table Randomizer, check out his video to see what started this project: [Minecraft 1.14 Loot Table Randomizer](https://youtu.be/3JEXAZOrykQ).

RLNotes is a Python project that aims to improve the minecraft randomizer experience. It provides features to improve usability and functionality of the randomizer datapack.

All of RLNotes' features are contained within a vanilla datapack, so no need to install mods. Using it is simple, you can just download one of the premade datapacks, but if you would prefer a more custom pack, download the project and try out it's different flags for customization.

The script can be run from command line with `py rl_notes_generate.py` or `py rl_notes_generate.py [seed] [flags]`, if you ever need a refresher on the available flags, a quick reference is available by running `py rl_notes_help.py`.


## Current Features
- **Base:**
  - Random Loot Tables:
    - Every Mob Drop, Chest Loot, Block Drop, and Gameplay Feature that uses loot tables is randomized
  - Condition Validation:
    - To ensure every drop is obtainable, conditions in each table are checked to make sure they work with their new source, and replaced with a valid condition if not.
  - Advancement Tree Visualizer:
    - Advancements, in conjuction with functions, help to track each loot table you interact with and create an advancement tree that you can reference so you can see what you've found.
  - Searchable Recipe "Notes":
    - Special un-craftable recipes are given to take advantage of the crafting book's search system, allowing you to search for any drop you've seen before.
- **Flags:**
  - Flags allow you to customize the datapack output from rl_notes_generate.py.
  - Available flags:
    - `--hardcore`
      - Excludes the player loot table from randomization. (will change the result of a seed)
    - `--update`
      - Attempts to create the datapack using pre-randomized loot-tables that you provide in the "randomized" folder. (will change the result of a seed)
    - `--no-cheats`
      - Excludes loot tables in \"requires_cheats.json\" from randomization. (will change the result of a seed)
    - `--no-dead-ends`
      - Excludes loot tables that drop nothing from randomization. (will change the result of a seed)
    - `--save-seed`
      - Includes the randomly generated seed in the datapack name and description.
    - `--hide-seed`
      - Excludes your provided seed from the datapack name and description.
      
## Planned Features:
- **More Flags:**
  - More flags are in the works like `--co-op` to share discoveries with other players, `--hints` for helpful hints when you're looking for new drops, and more
- **Better Validation**
- **Improved Detection**
- **Random Recipe Integration**
- **And More!**

## RLNotes is still in development<img width="96px" align="left" src="Icon.png"><img width="96px" align="right" src="Icon.png">
So feel free to give feedback, submit bug reports, write complaints, or send me general ego-boosting praise. Thanks!