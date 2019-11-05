from enum import Enum

from mc_helper import MCDict, mc_property

class Icon(MCDict):
	item:	str = mc_property('item', str)
	nbt:	str = mc_property('nbt', str)

	@staticmethod
	def populate(item: str = ''):
		icon = Icon()
		icon.item = item

		return icon

class TextComponent(MCDict):
	text: str = mc_property('text', str)

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
	icon:				Icon			= mc_property('icon', Icon)
	title:				TextComponent	= mc_property('title', TextComponent)
	frame:				eFrame			= mc_property('frame', eFrame)
	background:			str				= mc_property('background', str)
	description:		TextComponent	= mc_property('description', TextComponent)
	show_toast:			bool			= mc_property('show_toast', bool)
	announce_to_chat:	bool			= mc_property('announce_to_chat', bool)
	hidden:				bool			= mc_property('hidden', bool)

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