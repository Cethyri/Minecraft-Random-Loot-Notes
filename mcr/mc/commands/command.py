from abc import ABC
from typing import List

class Command(ABC):
	_command: List[str]
	
	def _append(self, command: str):
		self._command.append(command)
		return self

	@property
	def command(self):
		return ' '.join(self._command)

	def __str__(self):
		return self.command