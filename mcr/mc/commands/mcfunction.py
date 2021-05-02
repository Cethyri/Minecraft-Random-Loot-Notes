from mcr.mc.commands.argument_types import NamespacedId
from mcr.mc.commands.function import Function
from mcr.mc.commands.execute import Execute
from typing import List, TypeVar, Union
from mcr.mc.commands.command import Command

C = TypeVar('C')

# check what vars() does 

class MCFunction(List[Union[Command, str]]):

	def _appendChainSelf(self, command):
		self.append(command)
		return self

	def _appendChainCommand(self, command):
		self.append(command)
		return command

	def custom(self, command):
		return self._appendChainSelf(command)

	def execute(self, initialCommand: str = 'execute'):
		return self._appendChainCommand(Execute(initialCommand, self))

	def function(self, name: Union[NamespacedId, str]):
		return self._appendChainSelf(Function(name))

	@property
	def __str__(self):
		return '\r\n'.join(self)