from mcr.mc.base import JsonDict
from mcr.mc.properties import json_basic

from mcr.mc.data_structures.position import Distance
from mcr.mc.data_structures.location import Location

class Entity(JsonDict):
	distance:	Distance	= json_basic('distance', Distance)
	effects:	dict		= json_basic('effect', dict)
	location:	Location	= json_basic('location', Location)
	nbt:		str			= json_basic('nbt', str)
	typ:		str			= json_basic('type', str)