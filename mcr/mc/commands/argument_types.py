from enum import Enum
from typing import Union

# Put in Safeties (errors thrown on invalid arguments)

class relative_symbol(str, Enum):
	tilde = '~'
	caret = '^'

class BlockPos():
	def __init__(self, x: Union[int, str], y: Union[int, str], z: Union[int, str], rel: relative_symbol = ''):
		self.x = x
		self.y = y
		self.z = z
		self.rel = rel

	def __str__(self):
		return f'{self.rel}{self.x} {self.rel}{self.y} {self.rel}{self.z}'

class dimension(str, Enum):
	overworld		= 'minecraft:overworld'
	the_nether		= 'minecraft:the_nether'
	the_end			= 'minecraft:the_end'

class selector(str, Enum):
	nearest			= '@p'
	random			= '@r'
	all_players		= '@a'
	all_entities	= '@e'
	current			= '@s'
	p				= '@p'
	r				= '@r'
	a				= '@a'
	e				= '@e'
	s				= '@s'

class Entity():
	def __init__(self, selector: Union[str, selector], variables: Union[str, dict] = None):
		self.selector = selector
		self.variables = variables

	def __str__(self):
		var_list = ', '.join(f'{key} = {value}' for key, value in self.variables.items()) if isinstance(self.variables, dict) else self.variables
		var_list = f'[{var_list}]' if self.variables is not None else ""
		return f'{self.selector}{var_list}'

class entity_anchor(str, Enum):
	feet	= 'feet'
	eyes	= 'eyes'

class Rotation():
	def __init__(self, x: Union[float, str], y: Union[float, str], rel: relative_symbol = ''):
		self.x = x
		self.y = y
		self.rel = rel

	def __str__(self):
		return f'{self.rel}{self.x} {self.rel}{self.y}'

class swizzle(str, Enum):
	x	= 'x'
	y	= 'y'
	z	= 'z'
	xy	= 'xy'
	xz	= 'xz'
	yz	= 'yz'
	xyz	= 'xyz'

class Vec3():
	def __init__(self, x: Union[float, str], y: Union[float, str], z: Union[float, str], rel: relative_symbol = ''):
		self.x = x
		self.y = y
		self.z = z
		self.rel = rel

	def __str__(self):
		return f'{self.rel}{self.x} {self.rel}{self.y} {self.rel}{self.z}'