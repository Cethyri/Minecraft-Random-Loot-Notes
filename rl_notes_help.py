import json


with open('rln/data/flags.json') as json_file:
	flags = json.load(json_file)

for flag in flags:
	print(f'--{flag}:')
	print(f'    {flags[flag]["explanation"]}')
	if 'warning' in flags[flag]:
		print(f'    [Warning] {flags[flag]["warning"]}')
	print()