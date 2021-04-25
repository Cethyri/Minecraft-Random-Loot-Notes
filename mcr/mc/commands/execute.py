from enum import Enum
from mcr.mc.commands.command import Command
from typing import List, Union

from mcr.mc.commands.argument_types import BlockPos, Entity, dimension, entity_anchor, Rotation, swizzle, Vec3

class eStoreReturn(str, Enum):
	result	= 'result'
	success	= 'success'

class eStoreContainer(str, Enum):
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

class eIfTestType(str, Enum):
	block	= 'block'
	bossbar	= 'bossbar'
	entity	= 'entity'
	score	= 'score'
	storage	= 'storage'

class Execute(Command):
	def __init__(self, initialCommand = None):
		self._command = [initialCommand or 'execute']
	
	def align(self, axes: swizzle):
		return self._append(f'align {axes}')

	def anchored(self, anchor: entity_anchor):
		return self._append(f'anchored {anchor}')

	def as_(self, targets: Entity):
		return self._append(f'as {targets}')

	def at(self, targets: Entity):
		return self._append(f'at {targets}')

	def facing(self, pos: Vec3):
		return self._append(f'facing {pos}')

	def facing_entity(self, target: Entity, anchor: entity_anchor):
		return self._append(f'facing entity {target} {anchor}')

	def in_(self, dimension: dimension):
		return self._append(f'in {dimension}')

	def positioned(self, pos: Vec3):
		return self._append(f'positioned {pos}')

	def positioned_as(self, targets: Entity):
		return self._append(f'positioned as {targets}')

	def rotated(self, rot: Rotation):
		return self._append(f'rotated {rot}')

	def rotated_as(self, targets: Entity):
		return self._append(f'rotated as {targets}')


	def if_unless(self, isIf: bool, ):
		pass

	def store(self, value: eStoreReturn, target: eStoreContainer, arguments: str):
		return self._append(f'store {value} {target} {arguments}')

# incomplete, path should be nbt
	def store_result_block(self, targetPos: BlockPos, path: str, type: eNBTType, scale: float):
		return self.store(eStoreReturn.result, eStoreContainer.block, f'{targetPos} {path} {type} {scale}')
	
	def store_success_block(self, targetPos: BlockPos, path: str, type: eNBTType, scale: float):
		return self.store(eStoreReturn.success, eStoreContainer.block, f'{targetPos} {path} {type} {scale}')

	def store_result_bossbar(self, barId: str, target: eBossbarTarget):
		return self.store(eStoreReturn.result, eStoreContainer.bossbar, f'{barId} {target}')
		
	def store_success_bossbar(self, barId: str, target: eBossbarTarget):
		return self.store(eStoreReturn.success, eStoreContainer.bossbar, f'{barId} {target}')

	def store_result_entity(self, target: Entity, path: str, nbtType: eNBTType, scale: str):
		return self.store(eStoreReturn.result, eStoreContainer.entity, f'{target} {path} {nbtType} {scale}')

	def store_success_entity(self, target: Entity, path: str, nbtType: eNBTType, scale: str):
		return self.store(eStoreReturn.success, eStoreContainer.entity, f'{target} {path} {nbtType} {scale}')

	def store_result_score(self, name: str, objective: str):
		return self.store(eStoreReturn.result, eStoreContainer.score, f'{name} {objective}')

	def store_success_score(self, name: str, objective: str):
		return self.store(eStoreReturn.success, eStoreContainer.score, f'{name} {objective}')

	def store_result_storage(self, target: Entity, path: str, nbtType: eNBTType, scale: str):
		return self.store(eStoreReturn.result, eStoreContainer.storage, f'{target} {path} {nbtType} {scale}')

	def store_success_storage(self, target: Entity, path: str, nbtType: eNBTType, scale: str):
		return self.store(eStoreReturn.success, eStoreContainer.storage, f'{target} {path} {nbtType} {scale}')

	def if_block(self, invert: bool, pos: BlockPos, block: str):
		return self._append(f'{"unless" if invert else "unless"} block {pos} {block}')

	def if_blocks(self, invert: bool, pos: BlockPos, block: str):
		return self._append(f'{"unless" if invert else "unless"} block {pos} {block}')

class ExecuteRunnable(Execute):
    def run():
        return