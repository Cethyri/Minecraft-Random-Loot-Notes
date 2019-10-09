from enum import Enum

from mc_helper import MCDict, mc_obj

class Icon(MCDict):
	item:	str = mc_obj('item', str)
	nbt:	str = mc_obj('nbt', str)

	@staticmethod
	def populate(item: str = ''):
		icon = Icon()
		icon.item = item

		return icon

class TextComponent(MCDict):
	text: str = mc_obj('text', str)

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
	icon:				Icon			= mc_obj('icon', Icon)
	title:				TextComponent	= mc_obj('title', TextComponent)
	frame:				eFrame			= mc_obj('frame', eFrame)
	background:			str				= mc_obj('background', str)
	description:		TextComponent	= mc_obj('description', TextComponent)
	show_toast:			bool			= mc_obj('show_toast', bool)
	announce_to_chat:	bool			= mc_obj('announce_to_chat', bool)
	hidden:				bool			= mc_obj('hidden', bool)

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