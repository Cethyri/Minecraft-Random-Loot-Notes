from mcr.mc.base import MCDict
from mcr.mc.properties import mc_basic

from mcr.mc.data_structures.position import Distance
from mcr.mc.data_structures.location import Location

class Entity(MCDict):
	distance:	Distance	= mc_basic('distance', Distance)
	effects:	dict		= mc_basic('effect', dict)
	location:	Location	= mc_basic('location', Location)
	nbt:		str			= mc_basic('nbt', str)
	typ:		str			= mc_basic('type', str)