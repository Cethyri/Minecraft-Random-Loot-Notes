from enum import Enum
from typing import List, Dict

from mc_helper import MCDict, mc_property, mc_list_property, mc_dict_property

from display import Display
from criteria import Criteria


class Rewards(MCDict):
	recipes:	List[str]	= mc_list_property('recipes', str)
	loot:		List[str]	= mc_list_property('loot', str)
	experience:	int			= mc_property('experience', int)
	function:	str			= mc_property('function', str)

class Advancement(MCDict):
	display:		Display				= mc_property('display', Display)
	parent:			str					= mc_property('parent', str)
	criteria:		Dict[str, Criteria]	= mc_dict_property('criteria', Criteria)
	requirements:	List[str]			= mc_list_property('requirements', str)
	rewards: 		Rewards				= mc_property('rewards', Rewards)

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