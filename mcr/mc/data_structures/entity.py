from mcr.mc.properties import JsonDict

from mcr.mc.data_structures.position import Distance
from mcr.mc.data_structures.location import Location


class Entity(JsonDict):
    distance:	Distance
    effects:	dict
    location:	Location
    nbt:		str
    typ:		str
