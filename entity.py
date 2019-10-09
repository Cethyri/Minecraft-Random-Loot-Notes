from mc_helper import MCDict, mc_obj

from position import Distance
from location import Location

class Entity(MCDict):
	distance:	Distance	= mc_obj('distance', Distance)
	effects:	dict		= mc_obj('effect', dict)
	location:	Location	= mc_obj('location', Location)
	nbt:		str			= mc_obj('nbt', str)
	typ:		str			= mc_obj('type', str)