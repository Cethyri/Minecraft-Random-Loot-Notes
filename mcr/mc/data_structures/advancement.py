from typing import List, Dict

from mcr.mc.base import JsonDict
from mcr.mc.properties import json_basic, json_list, json_dict

from mcr.mc.data_structures.display import Display
from mcr.mc.data_structures.criteria import Criteria


class Rewards(JsonDict):
	recipes:	List[str]	= json_list('recipes', str)
	loot:		List[str]	= json_list('loot', str)
	experience:	int			= json_basic('experience', int)
	function:	str			= json_basic('function', str)

class Advancement(JsonDict):
	display:		Display				= json_basic('display', Display)
	parent:			str					= json_basic('parent', str)
	criteria:		Dict[str, Criteria]	= json_dict('criteria', Criteria.create)
	requirements:	List[List[str]]		= json_list('requirements', list)
	rewards: 		Rewards				= json_basic('rewards', Rewards)

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