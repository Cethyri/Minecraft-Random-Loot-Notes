import os
import random
import io
import zipfile
import json
import sys

if len(sys.argv) >= 2:
	try:
		seed = int(sys.argv[1])
	except Exception:
		print(f'The seed "{sys.argv[1]}" is not an integer.')
		exit()
	random.seed(seed)
	datapack_name = f'random_loot_{seed}'
	datapack_desc = f'Loot Table Randomizer, Seed: {seed}'
else:
	print('If you want to use a specific randomizer seed integer, use: "python randomize.py <seed>"')
	datapack_name = 'random_loot'
	datapack_desc = 'Loot Table Randomizer'
	
datapack_filename = datapack_name + '.zip'

print('Generating datapack...')
	
file_list = []
remaining = []

for dirpath, dirnames, filenames in os.walk('loot_tables'):
	for filename in filenames:
		file_list.append(os.path.join(dirpath, filename))
		remaining.append(os.path.join(dirpath, filename))
		
file_dict = {}

for file in file_list:
	i = random.randint(0, len(remaining)-1)
	file_dict[file] = remaining[i]
	del remaining[i]
	
zipbytes = io.BytesIO()
zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

for from_file in file_dict:
	with open(from_file) as file:
		contents = file.read()
		
	zip.writestr(os.path.join('data/minecraft/', file_dict[from_file]), contents)
	
zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))
zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':[f'{datapack_name}:reset']}))
zip.writestr(f'data/{datapack_name}/functions/reset.mcfunction', 'tellraw @a ["",{"text":"Loot table randomizer by SethBling","color":"green"}]')
	
zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())
	
print(f'Created datapack "{datapack_filename}"')