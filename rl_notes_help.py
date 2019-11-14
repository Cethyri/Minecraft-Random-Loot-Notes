import json


with open('rln/data/flags.json') as json_file:
	flags = json.load(json_file)

for flag in flags:
	print('--{}:'.format(flag))
	print('    {}'.format(flags[flag]["explanation"]))
	if "warning" in flags[flag]:
		print('    [Warning] {}'.format(flags[flag]["warning"]))
	print()