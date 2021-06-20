from abc import ABC
from typing import Generic, List, TypeVar


class Command(ABC):
    _command: list[str]

    def __init__(self, initialcommand: str):
        self._command = [initialcommand]

    @property
    def command(self):
        return ' '.join(self._command)

    def __str__(self):
        return self.command


T = TypeVar('T')


class ChainCommand(Command, ABC, Generic[T]):
    _owner: T

    def __init__(self, initialcommand: str, owner: T):
        super().__init__(initialcommand)
        self._owner = owner

    def _chainSelf(self, command: str):
        self._command.append(command)
        return self

    def _chainOwner(self, command: str):
        self._command.append(command)
        return self._owner

    @property
    def end(self):
        return self._owner
