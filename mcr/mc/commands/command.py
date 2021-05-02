from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

import warnings

T = TypeVar('T')

class Command(ABC, Generic[T]):
	_command: List[str]
	_owner: T
	_warnings: List[str]

	def __init__(self, initialcommand: str, owner: T = None):
		self._command = [initialcommand]
		self._owner = owner

	@abstractmethod
	def validate(self):
		if not self.command:
			self._warnings.append('Command is blank.')

		for warning in self._warnings:
			warnings.warn(warning)

		return not self._warnings
		
	def _appendChainSelf(self, command):
		self._command.append(command)
		return self

	def _appendChainOwner(self, command):
		self._command.append(command)
		return self._owner

	@property
	def command(self):
		return ' '.join(self._command)

	def __str__(self):
		return self.command

	@property
	def end(self):
		return self._owner