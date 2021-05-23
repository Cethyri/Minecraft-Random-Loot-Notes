import json
from typing import Any, List

from mcr.helpers.regex import remove_initial_dashes

flagFile = 'mcr/data/flags.json'

def flagHelp(json_flags: dict[str, Any]):
	for flag, flagInfo in json_flags.items():
		print(f'{flag}:')
		print(f'    {flagInfo["explanation"]}')
		if 'warning' in flagInfo:
			print(f'    [Warning] {flagInfo["warning"]}')
		print()

def handleFlags(args: List[str]):
	with open(flagFile) as json_file:
		json_flags = json.load(json_file)

	if len(args) > 1 and 'help' in args[1]:
		flagHelp(json_flags)
		return None

	print('Checking flags and setting up...')

	flags: dict[str, Any] = {}
	for flag in json_flags:
		flags[flag] = False

	for arg in args:
		arg = remove_initial_dashes(arg)
		if arg in flags:
			flags[arg] = True
		elif arg.isdigit():
			flags['seed'] = arg
		elif '=' in arg:
			setArg = arg.split('=')
			flags[setArg[0]] = setArg[1]
		else:
			print(f'{arg} is not a recognized flag, ignoring...')

	return flags
