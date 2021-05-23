from abc import ABC
from enum import Enum
from typing import (Any, Generic, Literal, Optional, TypeVar, Union, overload)

from mcr.mc.data_structures.nbt import NBT

# Put in Safeties (errors thrown on invalid arguments)


class dimension(str, Enum):
    overworld = 'minecraft:overworld'
    the_nether = 'minecraft:the_nether'
    the_end = 'minecraft:the_end'


class eSelector(str, Enum):
    nearest = '@p'
    random = '@r'
    all_players = '@a'
    all_entities = '@e'
    current = '@s'


selectorLiteral = Literal['@p', '@r', '@a', '@e', '@s']

selector = Union[eSelector, selectorLiteral]
class Entity():
    def __init__(self, selector_: Union[str, selector], arguments: Union[str, dict[str, Any], None] = None):
        self.selector_ = selector_
        self.arguments = arguments

    def __str__(self):
        var_list = ', '.join(f'{key} = {value}' for key, value in self.arguments.items(
        )) if isinstance(self.arguments, dict) else self.arguments
        var_list = f'[{var_list}]' if self.arguments is not None else ""
        return f'{self.selector_}{var_list}'


class entity_anchor(str, Enum):
    feet = 'feet'
    eyes = 'eyes'


feet = entity_anchor.feet
eyes = entity_anchor.eyes

# override accessor [] to use range syntax [1:]


class IntRange():
    pass


class eNBTCurrentResult(Enum):
    root = 'root'
    tags = 'tags'


class Node(ABC):
    @property
    def canBeSubListed(self) -> bool:
        return False


class RootCompound(Node):
    rootNBT: NBT

    def __init__(self, root: NBT) -> None:
        self.rootNBT = root

    def __str__(self) -> str:
        return str(self.rootNBT)


class Named(Node):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return NBT.safeTagName(self.name)


class NamedCompound(Node):
    name: str
    tag: NBT

    def __init__(self, name: str, tag: NBT) -> None:
        self.name = name
        self.tag = tag

    def __str__(self) -> str:
        return NBT.safeTagName(self.name) + str(self.tag)


class ElementOf(Node):
    name: str
    index: int

    def __init__(self, name: str, index: int) -> None:
        self.name = name
        self.index = index

    def __str__(self) -> str:
        return f'{NBT.safeTagName(self.name)}[{self.index}]'

    @property
    def canBeSubListed(self) -> bool:
        return True


class AllElementsOf(Node):
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f'{NBT.safeTagName(self.name)}[]'

    @property
    def canBeSubListed(self) -> bool:
        return True

# maybe make subclass of elements of sublist


class CompoundElementsOf(Node):
    name: str
    tag: NBT

    def __init__(self, name: str, tag: NBT) -> None:
        self.name = name
        self.tag = tag

    def __str__(self) -> str:
        return f'{NBT.safeTagName(self.name)}[{self.tag}]'


class ElementsOfSubList(Node):
    parent: Node
    index: Union[int, None, NBT]

    def __init__(self, parent: Node, index: Union[int, None, NBT]):
        self.parent = parent
        self.index = index

    def __str__(self):
        return f'{self.parent}[{"" if self.index is None else self.index}]'

    @property
    def canBeSubListed(self) -> bool:
        return not isinstance(self.index, NBT)


class NBTPath():
    __path: list[Node]

    @property
    def __lastNode(self):
        if len(self.__path) == 0:
            # error? warn?
            pass
        return self.__path[~0]

    def __init__(self, root: Optional[NBT] = None) -> None:
        self.__path = list[Node]()
        if root is not None:
            self.__path.append(RootCompound(root))

    def __getattribute__(self, name: str) -> 'NBTPath':
        if name.startswith('_NBTPath__') or name.startswith('__'):
            return object.__getattribute__(self, name)

        self.__path.append(Named(name))
        return self

    @overload
    def __call__(self, tag: NBT) -> 'NBTPath':
        return self

    @overload
    def __call__(self, name: str) -> 'NBTPath':
        return self

    def __call__(self, *args: Union[NBT, str]) -> 'NBTPath':
        arg = args[0]

        if isinstance(arg, NBT):
            lastNode = self.__lastNode
            if isinstance(lastNode, Named):
                self.__path[~0] = NamedCompound(lastNode.name, arg)
            else:
                # error? warn?
                pass
        else:
            self.__path.append(Named(arg))

        return self

    def __getitem__(self, key: Union[str, int, slice, None, NBT] = None) -> 'NBTPath':
        if isinstance(key, str):
            self.__path.append(Named(key))
        else:
            if isinstance(key, slice):
                if key.start or key.step or key.stop:
                    # warn only empty slice allowed
                    pass
                key = None

            lastNode = self.__lastNode

            if lastNode.canBeSubListed:
                self.__path[~0] = ElementsOfSubList(lastNode, key)
            elif not isinstance(lastNode, Named):
                # error? warn?
                pass
            elif isinstance(key, int):
                self.__path[~0] = ElementOf(lastNode.name, key)
            elif key is None:
                self.__path[~0] = AllElementsOf(lastNode.name)
            else:
                self.__path[~0] = CompoundElementsOf(lastNode.name, key)

        return self

    def __str__(self) -> str:
        return '.'.join(str(n) for n in self.__path)


class NamespacedId():
    def __init__(self, id_: str, namespace: str = 'minecraft') -> None:
        self.id_ = id_
        self.namespace = namespace

    def __str__(self) -> str:
        return f'{self.id_}:{self.namespace}'


class Objective():
    def __init__(self, objectiveName: str) -> None:
        self.objectiveName = objectiveName

    def __str__(self) -> str:
        return self.objectiveName


class swizzle(str, Enum):
    x = 'x'
    y = 'y'
    z = 'z'
    xy = 'xy'
    xz = 'xz'
    yz = 'yz'
    xyz = 'xyz'


VecType = TypeVar('VecType', int, float)


class relative_symbol(str, Enum):
    relative = '~'
    local = '^'

# Add Literal Support
class Vec3(Generic[VecType]):
    def __init__(self, x: VecType = 0, y: VecType = 0, z: VecType = 0, rel: Union[relative_symbol, str] = ''):
        self.x = x or ''
        self.y = y or ''
        self.z = z or ''
        self.relx = rel
        self.rely = rel
        self.relz = rel

    @property
    def rel(self, rel: Union[swizzle, str] = swizzle.xyz):
        self.relx = relative_symbol.relative if 'x' in rel else self.relx
        self.rely = relative_symbol.relative if 'y' in rel else self.rely
        self.relz = relative_symbol.relative if 'z' in rel else self.relz
        return self

    @property
    def loc(self):
        self.relx = '^'
        self.rely = '^'
        self.relz = '^'
        return self

    def __str__(self):
        return f'{self.relx}{self.x} {self.rely}{self.y} {self.relz}{self.z}'


class Vec2(Vec3[VecType]):
    def __init__(self, x: VecType = 0, y: VecType = 0, rel: Union[relative_symbol, str] = ''):
        # super().__init__(x, y, rel=rel)
        raise NotImplementedError('Nope')
        pass

    def __str__(self):
        return f'{self.relx}{self.x} {self.rely}{self.y}'


BlockPos = Vec3
Rotation = Vec2
