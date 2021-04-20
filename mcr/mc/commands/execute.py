from enum import Enum
from typing import Union


class Pos():
	def __init__(self, x: str, y: str, z: str):
		self.x = x
		self.y = y
		self.z = z

	def __str__(self):
		return f'{self.x} {self.y} {self.z}'

class Rot():
	def __init__(self, x: str, y: str):
		self.x = x
		self.y = y

	def __str__(self):
		return f'{self.x} {self.y}'

class eAxes(str, Enum):
	x	= 'x'
	y	= 'y'
	z	= 'z'
	xy	= 'xy'
	xz	= 'xz'
	yz	= 'yz'
	xyz	= 'xyz'

class eAnchor(str, Enum):
	feet	= 'feet'
	eyes	= 'eyes'

class eSelector(str, Enum):
	nearest			= '@p'
	random			= '@r'
	all_players		= '@a'
	all_entities	= '@e'
	current			= '@s'
	your_agents		= '@c'
	all_agents		= '@v'

class Target():
	def __init__(self, selector: Union[str, eSelector], variables: Union[str, dict]):
		self.selector = selector
		self.variables = variables

	def __str__(self):
		var_list = ', '.join(f'{key} = {value}' for key, value in self.variables.items()) if isinstance(self.variables, dict) else self.variables
		return f'{self.selector}[{var_list}]'

class eStoreValue(str, Enum):
	result	= 'result'
	success	= 'success'

class eStoreTarget(str, Enum):
	block	= 'block'
	bossbar	= 'bossbar'
	entity	= 'entity'
	score	= 'score'
	storage	= 'storage'

class eNBTType(str, Enum):
	NBTByte		= 'byte'
	NBTShort	= 'short'
	NBTInt		= 'int'
	NBTLong		= 'long'
	NBTFloat	= 'float'
	NBTDouble	= 'double'

class eBossbarTarget(str, Enum):
	value	= 'value'
	max		= 'max'

class StoreTarget():
	def __init__(self, target: eStoreTarget, arguments: str):
		self.target = target
		self.arguments = arguments

	@staticmethod
	def block(pos: Pos, path: str, nbtType: eNBTType, scale: str):
		return StoreTarget(eStoreTarget.block, f'{pos} {path} {nbtType} {scale}')

	@staticmethod
	def bossbar(barId: str, target: eBossbarTarget):
		return StoreTarget(eStoreTarget.block, f'{barId} {target}')

	@staticmethod
	def entity(target: Target, path: str, nbtType: eNBTType, scale: str):
		return StoreTarget(eStoreTarget.block, f'{target} {path} {nbtType} {scale}')

	@staticmethod
	def score(name: str, objective: str):
		return StoreTarget(eStoreTarget.block, f'{name} {objective}')

	@staticmethod
	def storage(target: Target, path: str, nbtType: eNBTType, scale: str):
		return StoreTarget(eStoreTarget.block, f'{target} {path} {nbtType} {scale}')

	def __str__(self):
		return f'{self.target} {self.arguments}'

class Execute():
	def __init__(self, initialCommand = None):
		self._command = [initialCommand or 'execute']
	
	def align(self, axes: eAxes):
		self._command.append(f'align {axes}')
		return self

	def anchored(self, anchor: eAnchor):
		self._command.append(f'anchored {anchor}')
		return self

	def asTargets(self, targets: Target):
		self._command.append(f'as {targets}')
		return self

	def atTarget(self, target: Target):
		self._command.append(f'at {target}')
		return self

	def facing(self, pos: Pos):
		self._command.append(f'facing {pos}')
		return self

	def facingTarget(self, target: Target, anchor: eAnchor):
		self._command.append(f'facing entity {target} {anchor}')
		return self

	def inDimension(self, dimension: str):
		self._command.append(f'in {dimension}')
		return self

	def positioned(self, pos: Pos):
		self._command.append(f'positioned {pos}')
		return self

	def positionedAs(self, targets: Target):
		self._command.append(f'positioned as {targets}')
		return self

	def rotated(self, rot: Rot):
		self._command.append(f'rotated {rot}')
		return self

	def rotatedAs(self, targets: Target):
		self._command.append(f'rotated as {targets}')
		return self

	def store(self, value: eStoreValue, target: StoreTarget):
		self._command.append(f'store {value} {target}')
		return self

	def ifBlock(self, invert: bool, pos: Pos, block: str):
		self._command.append(f'{"unless" if invert else "unless"} block {pos} {block}')
		return self

	def ifBlocks(self, invert: bool, pos: Pos, block: str):
		self._command.append(f'{"unless" if invert else "unless"} block {pos} {block}')
		return self
		
	@property
	def command(self):
		return ' '.join(self._command)

	def __str__(self):
		return self.command