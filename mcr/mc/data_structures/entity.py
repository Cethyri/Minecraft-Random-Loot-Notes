from mcr.json_dict import JsonDict

from mcr.mc.data_structures.position import Distance
from mcr.mc.data_structures.location import Location


class Entity(JsonDict, overrides={'type_': 'type'}):
    distance:	Distance
    effects:	dict
    location:	Location
    nbt:		str
    type_:		str
