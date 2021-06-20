from abc import ABC, abstractstaticmethod
from typing import Any, Callable, Optional, Tuple, Union, get_args, get_origin, get_type_hints

callOrCast = Callable[[Any], Any]


def baseOrOrigin(type_: type):
    return get_origin(type_) or type_


class SpecialInit(ABC):
    @abstractstaticmethod
    def create(value: Any) -> Any:
        pass

class UnionInit(ABC):
    @abstractstaticmethod
    def create(value: Any) -> Any:
        pass


class JsonDict(dict[str, Any]):
    overrides: dict[str, Union[str, callOrCast, Tuple[str, callOrCast]]] = {}

    def __init_subclass__(cls, overrides: Optional[dict[str, Union[str, callOrCast, Tuple[str, callOrCast]]]] = None):
        cls.overrides = overrides or {}
        for baseCls in cls.__bases__:
            if issubclass(baseCls, JsonDict) and baseCls.overrides is not None:
                cls.overrides = cls.overrides | baseCls.overrides

        typehints = get_type_hints(cls)

        for name, type_ in typehints.items():
            if name in vars(cls):
                continue

            key: str = name
            init: callOrCast = baseOrOrigin(type_)
            args: Tuple[type, ...] = get_args(type_)
            json_property: Callable[[str, callOrCast], property] = json_basic

            if name in cls.overrides:
                override = cls.overrides[name]
                if isinstance(override, tuple):
                    key = override[0]
                    init = override[1]
                elif isinstance(override, str):
                    key = override
                else:
                    init = override
            else:
                if init is list and len(args) >= 1:
                    json_property = json_list
                    init = baseOrOrigin(get_args(type_)[0])
                elif init is dict and len(args) >= 2:
                    json_property = json_dict
                    init = baseOrOrigin(get_args(type_)[1])
                elif init is Union and len(args) >= 1:
                    json_property = json_basic

                    for arg in args:
                        if issubclass(arg, UnionInit):
                            init = arg.create
                            break

                if isinstance(init, type) and issubclass(init, SpecialInit):
                    init = init.create

                if not callable(init):
                    def noChange(x: Any):
                        return x
                    init = noChange

            setattr(cls, name, json_property(key, init))

    def __init__(self, jsonDict: Optional[dict[str, Any]] = None):
        if jsonDict is None:
            return

        classes = list(self.__class__.__bases__)
        classes.append(self.__class__)

        for cls in classes:
            for value in vars(cls).values():
                if isinstance(value, _JsonProperty):
                    key = value.key
                    if key in jsonDict:
                        self[key] = value.init(jsonDict[key])

        for key, value in jsonDict.items():
            if key not in self:
                self[key] = value

        super().__init__()


class _JsonProperty(property):
    def __init__(self, key: str, init: Callable[[Any], Any]):
        def getter(self: dict[str, Any]):
            return self[key]

        def setter(self: dict[str, Any], value: Any):
            self[key] = value

        def deleter(self: dict[str, Any]):
            del self[key]

        super().__init__(getter, setter, deleter)
        self.key = key
        self.init = init


json_basic: Callable[[str, Callable[[Any], Any]], property] = _JsonProperty


def json_list(key: str, init: Callable[[Any], Any]) -> property:
    def list_init(list_val: list[Any]):
        return [init(v) for v in list_val]

    return _JsonProperty(key, list_init)


def json_dict(key: str, init: Callable[[Any], Any]) -> property:
    def dict_init(dict_val: dict[Any, Any]):
        return {k: init(v) for k, v in dict_val.items()}

    return _JsonProperty(key, dict_init)
