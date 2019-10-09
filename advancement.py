from enum import Enum
from typing import List, Dict

from mc_helper import MCDict, mc_obj, mc_list, mc_multi_dict

from display import Display
from criteria import Criteria


class Rewards(MCDict):
	recipes:	List[str]	= mc_list('recipes', str)
	loot:		List[str]	= mc_list('loot', str)
	experience:	int			= mc_obj('experience', int)
	function:	str			= mc_obj('function', str)


class Advancement(MCDict):
	display:		Display				= mc_obj('display', Display)
	parent:			str					= mc_obj('parent', str)
	criteria:		Dict[str, Criteria]	= mc_multi_dict('criteria', Criteria, Criteria.create)
	requirements:	List[str]			= mc_list('requirements', str)
	rewards: 		Rewards				= mc_obj('rewards', Rewards)

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