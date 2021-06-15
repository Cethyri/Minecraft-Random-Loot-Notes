from typing import List, Dict

from mcr.json_dict import JsonDict

from mcr.mc.data_structures.display import Display
from mcr.mc.data_structures.criteria import Criteria


class Rewards(JsonDict):
    recipes:	List[str]
    loot:		List[str]
    experience:	int
    function:	str


class Advancement(JsonDict):
    display:		Display
    parent:			str
    criteria:		Dict[str, Criteria]
    requirements:	List[List[str]]
    rewards: 		Rewards

    @staticmethod
    def populate(criteria: Dict[str, Criteria], display: Display = None, parent: str = None, requirements: List[str] = None, rewards: Rewards = None):
        adv = Advancement()
        adv.criteria = criteria
        if display is not None:
            adv.display = display
        if parent is not None:
            adv.parent = parent
        if requirements is not None:
            adv.requirements = requirements
        if rewards is not None:
            adv.rewards = rewards

        return adv
