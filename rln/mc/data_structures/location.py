from enum import Enum

from rln.mc.base import MCDict
from rln.mc.properties import mc_basic

from rln.mc.data_structures.position import Position

class eBiome(str, Enum):
	ocean								= 'minecraft:ocean'
	deep_ocean							= 'minecraft:deep_ocean'
	frozen_ocean						= 'minecraft:frozen_ocean'
	deep_frozen_ocean					= 'minecraft:deep_frozen_ocean'
	cold_ocean							= 'minecraft:cold_ocean'
	deep_cold_ocean						= 'minecraft:deep_cold_ocean'
	lukewarm_ocean						= 'minecraft:lukewarm_ocean'
	deep_lukewarm_ocean					= 'minecraft:deep_lukewarm_ocean'
	warm_ocean							= 'minecraft:warm_ocean'
	deep_warm_ocean						= 'minecraft:deep_warm_ocean'
	river								= 'minecraft:river'
	frozen_river						= 'minecraft:frozen_river'
	beach								= 'minecraft:beach'
	stone_shore							= 'minecraft:stone_shore'
	snowy_beach							= 'minecraft:snowy_beach'
	forest								= 'minecraft:forest'
	wooded_hills						= 'minecraft:wooded_hills'
	flower_forest						= 'minecraft:flower_forest'
	birch_forest						= 'minecraft:birch_forest'
	birch_forest_hills					= 'minecraft:birch_forest_hills'
	tall_birch_forest					= 'minecraft:tall_birch_forest'
	tall_birch_hills					= 'minecraft:tall_birch_hills'
	dark_forest							= 'minecraft:dark_forest'
	dark_forest_hills					= 'minecraft:dark_forest_hills'
	jungle								= 'minecraft:jungle'
	jungle_hills						= 'minecraft:jungle_hills'
	modified_jungle						= 'minecraft:modified_jungle'
	jungle_edge							= 'minecraft:jungle_edge'
	modified_jungle_edge				= 'minecraft:modified_jungle_edge'
	bamboo_jungle						= 'minecraft:bamboo_jungle'
	bamboo_jungle_hills					= 'minecraft:bamboo_jungle_hills'
	taiga								= 'minecraft:taiga'
	taiga_hills							= 'minecraft:taiga_hills'
	taiga_mountains						= 'minecraft:taiga_mountains'
	snowy_taiga							= 'minecraft:snowy_taiga'
	snowy_taiga_hills					= 'minecraft:snowy_taiga_hills'
	snowy_taiga_mountains				= 'minecraft:snowy_taiga_mountains'
	giant_tree_taiga					= 'minecraft:giant_tree_taiga'
	giant_tree_taiga_hills				= 'minecraft:giant_tree_taiga_hills'
	giant_spruce_taiga					= 'minecraft:giant_spruce_taiga'
	giant_spruce_taiga_hills			= 'minecraft:giant_spruce_taiga_hills'
	mushroom_fields						= 'minecraft:mushroom_fields'
	mushroom_field_shore				= 'minecraft:mushroom_field_shore'
	swamp								= 'minecraft:swamp'
	swamp_hills							= 'minecraft:swamp_hills'
	savanna								= 'minecraft:savanna'
	savanna_plateau						= 'minecraft:savanna_plateau'
	shattered_savanna					= 'minecraft:shattered_savanna'
	shattered_savanna_plateau			= 'minecraft:shattered_savanna_plateau'
	plains								= 'minecraft:plains'
	sunflower_plains					= 'minecraft:sunflower_plains'
	desert								= 'minecraft:desert'
	desert_hills						= 'minecraft:desert_hills'
	desert_lakes						= 'minecraft:desert_lakes'
	snowy_tundra						= 'minecraft:snowy_tundra'
	snowy_mountains						= 'minecraft:snowy_mountains'
	ice_spikes							= 'minecraft:ice_spikes'
	mountains							= 'minecraft:mountains'
	wooded_mountains					= 'minecraft:wooded_mountains'
	gravelly_mountains					= 'minecraft:gravelly_mountains'
	modified_gravelly_mountains			= 'minecraft:modified_gravelly_mountains'
	mountain_edge						= 'minecraft:mountain_edge'
	badlands							= 'minecraft:badlands'
	badlands_plateau					= 'minecraft:badlands_plateau'
	modified_badlands_plateau			= 'minecraft:modified_badlands_plateau'
	wooded_badlands_plateau				= 'minecraft:wooded_badlands_plateau'
	modified_wooded_badlands_plateau	= 'minecraft:modified_wooded_badlands_plateau'
	eroded_badlands						= 'minecraft:eroded_badlands'
	nether								= 'minecraft:nether'
	the_end								= 'minecraft:the_end'
	small_end_islands					= 'minecraft:small_end_islands'
	end_midlands						= 'minecraft:end_midlands'
	end_highlands						= 'minecraft:end_highlands'
	end_barrens							= 'minecraft:end_barrens'
	the_void							= 'minecraft:the_void'

class eDimension(str, Enum):
	overworld	= 'minecraft:overworld'
	the_end		= 'minecraft:the_end'
	the_nether	= 'minecraft:the_nether'

class eFeature(str, Enum):
	buried_treasure	= 'minecraft:buried_treasure'
	desert_pyramid	= 'minecraft:desert_pyramid'
	endcity			= 'minecraft:endcity'
	fortress		= 'minecraft:fortress'
	igloo			= 'minecraft:igloo'
	jungle_pyramid	= 'minecraft:jungle_pyramid'
	mansion			= 'minecraft:mansion'
	mineshaft		= 'minecraft:mineshaft'
	monument		= 'minecraft:monument'
	ocean_ruin		= 'minecraft:ocean_ruin'
	shipwreck		= 'minecraft:shipwreck'
	stronghold		= 'minecraft:stronghold'
	swamp_hut		= 'minecraft:swamp_hut'
	village			= 'minecraft:village'

class Location(MCDict):
	biome:		eBiome		= mc_basic('biome', eBiome)
	dimension:	eDimension	= mc_basic('dimension', eDimension)
	feature:	eFeature	= mc_basic('feature', eFeature)
	position:	Position	= mc_basic('position', Position)