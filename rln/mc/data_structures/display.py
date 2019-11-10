from enum import Enum

from rln.mc.base import MCDict
from rln.mc.properties import mc_basic

class Icon(MCDict):
	item:	str = mc_basic('item', str)
	nbt:	str = mc_basic('nbt', str)

	@staticmethod
	def populate(item: str = ''):
		icon = Icon()
		icon.item = item

		return icon

class TextComponent(MCDict):
	text: str = mc_basic('text', str)

	@staticmethod
	def populate(text: str = ''):
		tc = TextComponent()
		tc.text = text

		return tc

class eFrame(str, Enum):
	task		= 'task'
	goal		= 'goal'
	challenge	= 'challenge'

class Display(MCDict):
	icon:				Icon			= mc_basic('icon', Icon)
	title:				TextComponent	= mc_basic('title', TextComponent)
	frame:				eFrame			= mc_basic('frame', eFrame)
	background:			str				= mc_basic('background', str)
	description:		TextComponent	= mc_basic('description', TextComponent)
	show_toast:			bool			= mc_basic('show_toast', bool)
	announce_to_chat:	bool			= mc_basic('announce_to_chat', bool)
	hidden:				bool			= mc_basic('hidden', bool)

	@staticmethod
	def populate(icon: str, title: str, description: str, frame: str = None, background: str = None, show: bool = None, announce: bool = None, hidden: bool = None):
		display = Display()
		display.icon = Icon.populate(icon)
		display.title = TextComponent.populate(title)
		display.description = TextComponent.populate(description)
		if frame is not None:
			display.frame = eFrame(frame)
		if background is not None:
			display.background = background
		if show is not None:
			display.show_toast = show
		if announce is not None:
			display.announce_to_chat = announce
		if hidden is not None:
			display.hidden = hidden
		
		return display