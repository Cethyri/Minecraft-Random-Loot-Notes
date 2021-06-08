from enum import Enum
from mcr.mc.data_structures.nbt import NBTPath
from typing import Union

from mcr.mc.commands.argument_types import (BlockPos, Entity, IntRange,
                                            NamespacedId, Objective,
                                            Rotation, Vec3, dimension,
                                            entity_anchor, selector, swizzle)
from mcr.mc.commands.command import ChainCommand, Command, T

# import warnings

# idea for full dot syntax use properties that return a custom class with getattr overidden to hide the command under another variable but still pass back the command eg Execute().store.results


class eStoreReturn(str, Enum):
    result = 'result'
    success = 'success'


class eStoreContainer(str, Enum):
    block = 'block'
    bossbar = 'bossbar'
    entity = 'entity'
    score = 'score'
    storage = 'storage'


class eNBTType(str, Enum):
    NBTByte = 'byte'
    NBTShort = 'short'
    NBTInt = 'int'
    NBTLong = 'long'
    NBTFloat = 'float'
    NBTDouble = 'double'


class eBossbarTarget(str, Enum):
    value = 'value'
    max = 'max'


class eConditionalType(str, Enum):
    block = 'block'
    blocks = 'blocks'
    data = 'data'
    entity = 'entity'
    predicate = 'predicate'
    score = 'score'


class eScanMode(str, Enum):
    all = 'all'
    masked = 'masked'


class eDataCheck(str, Enum):
    block = 'block'
    entity = 'entity'
    storage = 'storage'


class eComparison(str, Enum):
    lt = '<'
    le = '<='
    eq = '='
    ge = '>='
    gt = '>'


class Execute(ChainCommand[T]):

    @classmethod
    def conditions(cls):
        return Execute('')

    def __init__(self, initialCommand: str = 'execute', owner: T = None):
        super().__init__(initialCommand, owner)

    def align(self, axes: swizzle):
        return self._chainSelf(f'align {axes}')

    def anchored(self, anchor: entity_anchor):
        return self._chainSelf(f'anchored {anchor}')

    def as_(self, targets: Union[Entity, selector]):
        return self._chainSelf(f'as {targets}')

    def at(self, targets: Union[Entity, selector]):
        return self._chainSelf(f'at {targets}')

    def facing(self, pos: Vec3):
        return self._chainSelf(f'facing {pos}')

    def facing_entity(self, target: Union[Entity, selector], anchor: entity_anchor):
        return self._chainSelf(f'facing entity {target} {anchor}')

    def in_(self, dim: dimension):
        return self._chainSelf(f'in {dim}')

    def positioned(self, pos: Vec3):
        return self._chainSelf(f'positioned {pos}')

    def positioned_as(self, targets: Union[Entity, selector]):
        return self._chainSelf(f'positioned as {targets}')

    def rotated(self, rot: Rotation):
        return self._chainSelf(f'rotated {rot}')

    def rotated_as(self, targets: Union[Entity, selector]):
        return self._chainSelf(f'rotated as {targets}')

    def store(self, value: eStoreReturn, target: eStoreContainer, arguments: str):
        return self._chainSelf(f'store {value} {target} {arguments}')

    def store_result_block(self, targetPos: BlockPos, path: NBTPath, nbtType: eNBTType, scale: float):
        return self.store(eStoreReturn.result, eStoreContainer.block, f'{targetPos} {path} {nbtType} {scale}')

    def store_success_block(self, targetPos: BlockPos, path: NBTPath, nbtType: eNBTType, scale: float):
        return self.store(eStoreReturn.success, eStoreContainer.block, f'{targetPos} {path} {nbtType} {scale}')

    def store_result_bossbar(self, barId: NamespacedId, target: eBossbarTarget):
        return self.store(eStoreReturn.result, eStoreContainer.bossbar, f'{barId} {target}')

    def store_success_bossbar(self, barId: NamespacedId, target: eBossbarTarget):
        return self.store(eStoreReturn.success, eStoreContainer.bossbar, f'{barId} {target}')

    def store_result_entity(self, target: Union[Entity, selector], path: NBTPath, nbtType: eNBTType, scale: float):
        return self.store(eStoreReturn.result, eStoreContainer.entity, f'{target} {path} {nbtType} {scale}')

    def store_success_entity(self, target: Union[Entity, selector], path: NBTPath, nbtType: eNBTType, scale: float):
        return self.store(eStoreReturn.success, eStoreContainer.entity, f'{target} {path} {nbtType} {scale}')

    def store_result_score(self, name: Union[Entity, selector], objective: Objective):
        return self.store(eStoreReturn.result, eStoreContainer.score, f'{name} {objective}')

    def store_success_score(self, name: Union[Entity, selector], objective: Objective):
        return self.store(eStoreReturn.success, eStoreContainer.score, f'{name} {objective}')

    def store_result_storage(self, target: NamespacedId, path: NBTPath, nbtType: eNBTType, scale: float):
        return self.store(eStoreReturn.result, eStoreContainer.storage, f'{target} {path} {nbtType} {scale}')

    def store_success_storage(self, target: NamespacedId, path: NBTPath, nbtType: eNBTType, scale: float):
        return self.store(eStoreReturn.success, eStoreContainer.storage, f'{target} {path} {nbtType} {scale}')

    def if_unless(self, isIf: bool, testType: eConditionalType, arguments: str):
        return self._chainSelf(f'{"if" if isIf else "unless"} {testType} {arguments}')

    def if_block(self, pos: BlockPos, block: NamespacedId):
        # TODO: fix block should allow nbt? data of some sort
        return self.if_unless(True, eConditionalType.block, f'{pos} {block}')

    def unless_block(self, pos: BlockPos, block: NamespacedId):
        return self.if_unless(False, eConditionalType.block, f'{pos} {block}')

    def if_blocks(self, start: BlockPos, end: BlockPos, destination: BlockPos, scanMode: eScanMode):
        return self.if_unless(True, eConditionalType.blocks, f'{start} {end} {destination} {scanMode}')

    def unless_blocks(self, start: BlockPos, end: BlockPos, destination: BlockPos, scanMode: eScanMode):
        return self.if_unless(False, eConditionalType.blocks, f'{start} {end} {destination} {scanMode}')

    def if_data_block(self, pos: BlockPos, path: NBTPath):
        return self.if_unless(True, eConditionalType.data, f'{eDataCheck.block} {pos} {path}')

    def unless_data_block(self, pos: BlockPos, path: NBTPath):
        return self.if_unless(False, eConditionalType.data, f'{eDataCheck.block} {pos} {path}')

    def if_data_entity(self, target: Union[Entity, selector], path: NBTPath):
        return self.if_unless(True, eConditionalType.data, f'{eDataCheck.entity} {target} {path}')

    def unless_data_entity(self, target: Union[Entity, selector], path: NBTPath):
        return self.if_unless(False, eConditionalType.data, f'{eDataCheck.entity} {target} {path}')

    def if_data_storage(self, source: NamespacedId, path: NBTPath):
        return self.if_unless(True, eConditionalType.data, f'{eDataCheck.storage} {source} {path}')

    def unless_data_storage(self, source: NamespacedId, path: NBTPath):
        return self.if_unless(False, eConditionalType.data, f'{eDataCheck.storage} {source} {path}')

    def if_entity(self, target: Union[Entity, selector]):
        return self.if_unless(True, eConditionalType.entity, str(target))

    def unless_entity(self, target: Union[Entity, selector]):
        return self.if_unless(False, eConditionalType.entity, str(target))

    def if_predicate(self, predicate: NamespacedId):
        return self.if_unless(True, eConditionalType.predicate, str(predicate))

    def unless_predicate(self, predicate: NamespacedId):
        return self.if_unless(False, eConditionalType.predicate, str(predicate))

    def if_score(self, target: Union[Entity, selector], targetObjective: Objective, comparison: eComparison, source: Union[Entity, selector], sourceObjective: Objective):
        return self.if_unless(True, eConditionalType.score, f'{target} {targetObjective} {comparison} {source} {sourceObjective}')

    def unless_score(self, target: Union[Entity, selector], targetObjective: Objective, comparison: eComparison, source: Union[Entity, selector], sourceObjective: Objective):
        return self.if_unless(False, eConditionalType.score, f'{target} {targetObjective} {comparison} {source} {sourceObjective}')

    def if_score_matches(self, target: Union[Entity, selector], targetObjective: Objective, range_: Union[IntRange, str, int]):
        return self.if_unless(True, eConditionalType.score, f'{target} {targetObjective} matches {range_}')

    def unless_score_matches(self, target: Union[Entity, selector], targetObjective: Objective, range_: Union[IntRange, str, int]):
        return self.if_unless(False, eConditionalType.score, f'{target} {targetObjective} matches {range_}')

    def run(self, command: Union[Command, str]) -> T:
        return self._chainOwner(f'run {command}')
