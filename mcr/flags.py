import json
from typing import Any, Optional, Tuple

from mcr.helpers.regex import remove_initial_dashes
from mcr.json_dict import JsonDict

flagFile = 'mcr/data/flags.json'


class MCRFlags(JsonDict, overrides={'no_cheats': 'no-cheats', 'no_dead_ends': 'no-dead-ends', 'gift_boxes': 'gift-boxes', 'save_seed': 'save-seed', 'hide_seed': 'hide-seed', 'co_op': 'co-op'}):
    hardcore: bool
    no_cheats: bool
    no_dead_ends: bool
    hide_seed: bool
    co_op: bool


def flagHelp(json_flags: dict[str, Any]):
    for flag, flagInfo in json_flags.items():
        print(f'{flag}:')
        print(f'    {flagInfo["explanation"]}')
        if 'warning' in flagInfo:
            print(f'    [Warning] {flagInfo["warning"]}')
        print()


def handleFlags(args: list[str]) -> Optional[Tuple[MCRFlags, dict[str, dict[str, str]], Optional[str]]]:
    with open(flagFile) as json_file:
        json_flags = json.load(json_file)

    if len(args) > 1 and 'help' in args[1]:
        flagHelp(json_flags)
        return None

    seed: Optional[str] = None
    flags: dict[str, Any] = {}
    for flag in json_flags:
        flags[flag] = False

    for arg in args:
        arg = remove_initial_dashes(arg)
        if arg in flags:
            flags[arg] = True
        elif arg.isdigit() and flags['seed'] is False:
            flags['seed'] = arg
        elif '=' in arg:
            setArg = arg.split('=')
            flags[setArg[0]] = setArg[1]
        else:
            print(f'{arg} is not a recognized flag, ignoring...')

    if flags['seed'] is not False:
        seed = flags['seed']
        del flags['seed']
    result = MCRFlags(flags)

    return result, json_flags, seed
