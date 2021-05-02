from mcr.mc.commands.argument_types import NamespacedId
from mcr.mc.commands.command import Command, T
from typing import Union

class Function(Command[T]):
	def __init__(self, name: Union[NamespacedId, str]):
		super().__init__(f'function {name}')
	
	def validate(self):
		return super().validate()