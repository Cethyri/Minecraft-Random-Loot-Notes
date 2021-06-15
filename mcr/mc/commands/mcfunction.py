from mcr.mc.commands.command import Command
from typing import Any, TypeVar

from mcr.mc.commands.argument_types import NamespacedId
from mcr.mc.commands.execute import Execute
from mcr.mc.commands.function import Function

C = TypeVar('C', bound=Command)


class MCFunction(list[Any]):

    def _chainSelf(self, command: Any):
        self.append(command)
        return self

    def _chainCommand(self, command: C) -> C:
        self.append(command)
        return command

    def custom(self, command: Any):
        return self._chainSelf(command)

    def execute(self, initialCommand: str = 'execute'):
        return self._chainCommand(Execute(initialCommand, self))

    def function(self, name: NamespacedId):
        return self._chainSelf(Function(name))

    def __str__(self):
        return '\r\n'.join(str(command) for command in self)
