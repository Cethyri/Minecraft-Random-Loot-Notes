from enum import Enum

from mcr.mc.base import JsonDict
from mcr.mc.properties import json_basic

class Icon(JsonDict):
	item:	str = json_basic('item', str)
	nbt:	str = json_basic('nbt', str)

	@staticmethod
	def populate(item: str = ''):
		icon = Icon()
		icon.item = item

		return icon

class TextComponent(JsonDict):
	text: str = json_basic('text', str)

	@staticmethod
	def populate(text: str = ''):
		tc = TextComponent()
		tc.text = text

		return tc

class eFrame(str, Enum):
	task		= 'task'
	goal		= 'goal'
	challenge	= 'challenge'

class Display(JsonDict):
	icon:				Icon			= json_basic('icon', Icon)
	title:				TextComponent	= json_basic('title', TextComponent)
	frame:				eFrame			= json_basic('frame', eFrame)
	background:			str				= json_basic('background', str)
	description:		TextComponent	= json_basic('description', TextComponent)
	show_toast:			bool			= json_basic('show_toast', bool)
	announce_to_chat:	bool			= json_basic('announce_to_chat', bool)
	hidden:				bool			= json_basic('hidden', bool)

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