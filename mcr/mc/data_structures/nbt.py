from abc import ABC
import re
from typing import Callable, Generic, Optional, TypeVar, Union, overload


Tag_Compatible = Union[dict[str, 'Tag_Compatible'],
                       list['Tag_Compatible'], int, float, str, 'Tag']


class Tag():
    @staticmethod
    def safeTagName(name: str):
        if not name or '"' in name:
            raise Exception(f'"{name}" is not a valid tag name.')

        return name if re.fullmatch(r"[a-zA-Z_]+[a-zA-Z_0-9]*", name) else f'"{name}"'

    @staticmethod
    def handleValue(value: Tag_Compatible) -> 'Tag':
        result = value
        if isinstance(value, Tag):
            result = value
        elif isinstance(value, dict):
            result = Tag_Compound(value)
        elif isinstance(value, list):
            result = Tag_List(value)
        elif isinstance(value, int):
            result = Tag_Int(value)
        elif isinstance(value, float):
            result = Tag_Float(value)
        else:
            result = Tag_String(value)

        return result


TAG = TypeVar('TAG', bound=Tag)

class Tag_Compound(dict[str, Tag], Tag):
    def __init__(self, initialValue: dict[str, Tag_Compatible]):
        super().__init__()
        for key, value in initialValue.items():
            self[Tag.safeTagName(key)] = Tag.handleValue(value)

    def __str__(self) -> str:
        values = ', '.join(f'{key}: {value}' for key, value in self.items())
        return f'{{ {values} }}' if values else '{}'


class Tag_Int(int, Tag):
    min_: int = -2147483648
    max_: int = 2147483647
    postFix: str = ''

    def __init_subclass__(cls, min_: int, max_: int, postfix: str):
        cls.min_ = min_
        cls.max_ = max_
        cls.postFix = postfix

    def __new__(cls, value: Union[int, 'Tag_Int']):
        if isinstance(value, Tag_Int):
            return value

        if cls.min_ <= value <= cls.max_:
            return super().__new__(cls, value)
        else:
            raise Exception(
                f'Value does not fit within defined bounds. Values for a {cls} must be between {cls.min_} and {cls.max_}')

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return f'{int(self)}{self.postFix}'


class Tag_Float(float, Tag):
    postFix: str = 'f'

    def __init_subclass__(cls, postfix: str):
        cls.postFix = postfix

    def __new__(cls, value: Union[float, 'Tag_Float']):
        if isinstance(value, Tag_Float):
            return value

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f'{float(self)}{self.postFix}'


class Tag_Byte(Tag_Int, min_=-128, max_=127, postfix='b'):
    pass


class Tag_Short(Tag_Int, min_=-32768, max_=32767, postfix='s'):
    pass


class Tag_Long(Tag_Int, min_=-9223372036854775808, max_=9223372036854775807, postfix='l'):
    pass


class Tag_Double(Tag_Float, postfix='d'):
    pass


L = TypeVar('L', bound=Tag_Compatible)


class Tag_Generic_List(Generic[TAG, L], list[TAG], Tag):
    type_notifier: str = ''
    index_initializer: Callable[[Union[TAG, L]], TAG]

    def __init_subclass__(cls, index_initializer: Callable[[Union[TAG, L]], TAG], type_notifier: str = ''):
        super().__init_subclass__()
        cls.type_notifier = type_notifier
        cls.index_initializer = index_initializer

    def __init__(self, value: Union[list[TAG], list[L]]):
        super().__init__(type(self).index_initializer(v) for v in value)

    def __str__(self) -> str:
        return f'[{self.type_notifier} {", ".join(str(t) for t in self)} ]'


class Tag_List(Tag_Generic_List[Tag, Tag_Compatible], index_initializer=Tag.handleValue):
    pass


class Tag_Byte_Array(Tag_Generic_List[Tag_Byte, int], index_initializer=Tag_Byte, type_notifier='B;'):
    pass


class Tag_Int_Array(Tag_Generic_List[Tag_Int, int], index_initializer=Tag_Int, type_notifier='I;'):
    pass


class Tag_Long_Array(Tag_Generic_List[Tag_Long, int], index_initializer=Tag_Long, type_notifier='L;'):
    pass


class Tag_String(Tag):
    value: str

    def __init__(self, value: str) -> None:
        self.value = value.replace('"', '\\"')

    def __str__(self) -> str:
        return f'"{self.value}"'


NBT = Tag_Compound


class Node(ABC):
    @property
    def canBeSublisted(self) -> bool:
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
    def canBeSublisted(self) -> bool:
        return True


class AllElementsOf(Node):
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f'{NBT.safeTagName(self.name)}[]'

    @property
    def canBeSublisted(self) -> bool:
        return True


class CompoundElementsOf(Node):
    name: str
    tag: NBT

    def __init__(self, name: str, tag: NBT) -> None:
        self.name = name
        self.tag = tag

    def __str__(self) -> str:
        return f'{NBT.safeTagName(self.name)}[{self.tag}]'


class ElementsOfSublist(Node):
    parent: Node
    index: Union[int, None, NBT]

    def __init__(self, parent: Node, index: Union[int, None, NBT]):
        self.parent = parent
        self.index = index

    def __str__(self):
        return f'{self.parent}[{"" if self.index is None else self.index}]'

    @property
    def canBeSublisted(self) -> bool:
        return not isinstance(self.index, NBT)


class NBTPath():
    __path: list[Node]

    @property
    def __lastNode(self):
        if len(self.__path) == 0:
            # error? warn?
            pass
        return self.__path[~0]

    def __init__(self, root: Optional[Union[dict[str, Tag_Compatible], NBT]] = None) -> None:
        self.__path = list[Node]()
        if root is not None:
            if isinstance(root, NBT):
                self.__path.append(RootCompound(root))
            else:
                self.__path.append(RootCompound(NBT(root)))

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

            if lastNode.canBeSublisted:
                self.__path[~0] = ElementsOfSublist(lastNode, key)
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
