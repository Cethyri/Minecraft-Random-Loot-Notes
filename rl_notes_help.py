import json


with open('rl_notes/data/flags.json') as json_file:
	flags = json.load(json_file)

for flag in flags:
	print('--{}:'.format(flag))
	print('    {}'.format(flags[flag]["explanation"]))
	print()