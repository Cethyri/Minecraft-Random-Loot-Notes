from mc_helper import MCDict, mc_property

from position import Distance
from location import Location

class Entity(MCDict):
	distance:	Distance	= mc_property('distance', Distance)
	effects:	dict		= mc_property('effect', dict)
	location:	Location	= mc_property('location', Location)
	nbt:		str			= mc_property('nbt', str)
	typ:		str			= mc_property('type', str)