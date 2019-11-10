from enum import Enum
from typing import List, Dict

from rl_notes.mc.base import MCDict
from rl_notes.mc.properties import mc_basic, mc_list, mc_dict

from rl_notes.mc.data_structures.display import Display
from rl_notes.mc.data_structures.criteria import Criteria


class Rewards(MCDict):
	recipes:	List[str]	= mc_list('recipes', str)
	loot:		List[str]	= mc_list('loot', str)
	experience:	int			= mc_basic('experience', int)
	function:	str			= mc_basic('function', str)

class Advancement(MCDict):
	display:		Display				= mc_basic('display', Display)
	parent:			str					= mc_basic('parent', str)
	criteria:		Dict[str, Criteria]	= mc_dict('criteria', Criteria.create)
	requirements:	List[List[str]]		= mc_list('requirements', list)
	rewards: 		Rewards				= mc_basic('rewards', Rewards)

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