from mcr.json_dict import JsonDict
from mcr.mc.data_structures.criteria import Criteria
from mcr.mc.data_structures.display import Display


class Rewards(JsonDict):
    recipes:	list[str]
    loot:		list[str]
    experience:	int
    function:	str


class Advancement(JsonDict):
    display:		Display
    parent:			str
    criteria:		dict[str, Criteria]
    requirements:	list[list[str]]
    rewards: 		Rewards
