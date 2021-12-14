from enum import Enum
from typing import Any, Literal, Optional, Union

# Put in Safeties (errors thrown on invalid arguments)


int_or_float = Union[int, float]


class eDimension(str, Enum):
    overworld = 'minecraft:overworld'
    the_nether = 'minecraft:the_nether'
    the_end = 'minecraft:the_end'


dimensionLiteral = Literal['minecraft:overworld',
                           'minecraft:the_nether',
                           'minecraft:the_end']
dimension = Union[eDimension, dimensionLiteral]


class eSelector(str, Enum):
    nearest = '@p'
    random = '@r'
    all_players = '@a'
    all_entities = '@e'
    current = '@s'


selectorLiteral = Literal['@p', '@r', '@a', '@e', '@s']
selector = Union[eSelector, selectorLiteral]


class Entity():
    def __init__(self, selector_: Union[str, selector], **kwargs: Any):
        self.selector_ = selector_
        self.arguments = kwargs

    def __str__(self):
        var_list = ', '.join(f'{key} = {value}' for key,
                             value in self.arguments.items())
        var_list = f'[{var_list}]' if self.arguments is not None else ""
        return f'{self.selector_}{var_list}'


class eEntityAnchor(str, Enum):
    feet = 'feet'
    eyes = 'eyes'


entityAnchorLiteral = Literal['eyes', 'feet']
entity_anchor = Union[eEntityAnchor, entityAnchorLiteral]

# override accessor [] to use range syntax [1:]


class IntRange():
    def __init__(self, eq: Optional[int_or_float] = None, low: Optional[int_or_float] = None, high: Optional[int_or_float] = 0) -> None:
        self.r = str(eq) or f'{low or ""}..{high or ""}'
        if self.r == '..':
            self.r = '0'

    @staticmethod
    def eq(eq: int_or_float):
        return IntRange(eq)

    @staticmethod
    def le(low: int_or_float):
        return IntRange(low=low)

    @staticmethod
    def ge(high: int_or_float):
        return IntRange(high=high)

    @staticmethod
    def bt(low: int_or_float, high: int_or_float):
        return IntRange(low=low, high=high)

    def __str__(self) -> str:
        return self.r


class NamespacedId(): # TODO maybe do (str)
    def __init__(self, id_: str, namespace: str = 'minecraft') -> None:
        self.id_ = id_
        self.namespace = namespace

    def __str__(self) -> str:
        return f'{self.namespace}:{self.id_}'


class Objective():
    def __init__(self, objectiveName: str) -> None:
        self.objectiveName = objectiveName

    def __str__(self) -> str:
        return self.objectiveName


class eSwizzle(str, Enum):
    x = 'x'
    y = 'y'
    z = 'z'
    xy = 'xy'
    xz = 'xz'
    yz = 'yz'
    xyz = 'xyz'


swizzleLiteral = Literal['x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz']
swizzle = Union[eSwizzle, swizzleLiteral]


class eRelativeSymbol(str, Enum):
    relative = '~'
    local = '^'


relativeSymbolLiteral = Literal['~', '^']
relative_symbol = Union[eRelativeSymbol, relativeSymbolLiteral]


class Vec3():
    def __init__(self, x: int_or_float = 0, y: int_or_float = 0, z: int_or_float = 0, rel: Optional[relative_symbol] = None):
        self.x = x or ''
        self.y = y or ''
        self.z = z or ''
        self.relx = rel or ''
        self.rely = rel or ''
        self.relz = rel or ''

    def rel(self, rel: relative_symbol = '~', which: swizzle = eSwizzle.xyz):
        self.relx = rel if 'x' in which else self.relx
        self.rely = rel if 'y' in which else self.rely
        self.relz = rel if 'z' in which else self.relz
        return self

    @property
    def loc(self):
        return self.rel(eRelativeSymbol.local)

    def __str__(self):
        x = f'{self.relx}{self.x}' or 0
        y = f'{self.rely}{self.y}' or 0
        z = f'{self.relz}{self.z}' or 0
        return f'{x} {y} {z}'


class Vec2(Vec3):
    def __init__(self, x: int_or_float = 0, y: int_or_float = 0, rel: Optional[relative_symbol] = None):
        super().__init__(x, y, rel=rel)

    def rel(self, rel: relative_symbol = '~', which: swizzle = eSwizzle.xy):
        return super().rel(rel, which)

    def __str__(self):
        x = f'{self.relx}{self.x}' or 0
        y = f'{self.rely}{self.y}' or 0
        return f'{x} {y}'


BlockPos = Vec3
Rotation = Vec2
