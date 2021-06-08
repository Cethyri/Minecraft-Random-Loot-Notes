from mcr.mc.data_structures.nbt import NBTPath, Tag_Short
from typing import Union


class myBaseClass:
    pass

class mydict(dict[str, myBaseClass], myBaseClass):
    pass


class myint(int, myBaseClass):

    def __init_subclass__(cls, min_: int, max_: int, postfix: str):
        cls.min_ = min_
        cls.max_ = max_
        cls.postFix = postfix


def test(a: Union[mydict, dict[str, myBaseClass]]):
    print(a)


test({'s': myint(101)})