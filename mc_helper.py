from typing import List, Callable


def _dynamic_getter(key: str, return_type: type):
	def getter(self) -> return_type:
		return self[key]

	return getter

def _dynamic_setter(key: str, value_type: type):
	def setter(self, value: value_type):
		self[key] = value
	
	return setter


class _MCObj(property):
	def __init__(self, key: str, prop_type: type, getter: Callable, setter: Callable):
		super().__init__(getter, setter)
		self.key = key
		self.prop_type = prop_type

class _MCList(_MCObj):
	__init__ = _MCObj.__init__

class _MCMulti(property):
	def __init__(self, key: str, create: Callable, getter: Callable, setter: Callable):
		super().__init__(getter, setter)
		self.key = key
		self.create = create

class _MCMultiList(_MCMulti):
	__init__ = _MCMulti.__init__


def mc_obj(key: str, prop_type: type) -> property:
	return _MCObj(key, prop_type, _dynamic_getter(key, prop_type), _dynamic_setter(key, prop_type))

def mc_list(key: str, elem_type: type) -> property:
	return _MCList(key, elem_type, _dynamic_getter(key, List[elem_type]), _dynamic_setter(key, List[elem_type]))

def mc_multi(key: str, prop_type: type, create: Callable) -> property:
	return _MCMulti(key, create, _dynamic_getter(key, prop_type), _dynamic_setter(key, prop_type))

def mc_multi_list(key: str, elem_type: type, create_elem: Callable) -> property:
	return _MCMultiList(key, create_elem, _dynamic_getter(key, List[elem_type]), _dynamic_setter(key, List[elem_type]))


class MCDict(dict):
	def __init__(self, json_body: dict = None):
		if json_body is None:
			return

		for key, value in json_body.items():
			self[key] = value
			
		for value in self.__class__.__dict__.values():
			if isinstance(value, _MCList):
				if value.key in json_body:
					self[value.key] = []
					for element in json_body[value.key]:
						self[value.key].append(value.prop_type(element))

			elif isinstance(value, _MCObj):
				if value.key in json_body:
					self[value.key] = value.prop_type(json_body[value.key])

			if isinstance(value, _MCMultiList):
				if value.key in json_body:
					self[value.key] = []
					for element in json_body[value.key]:
						self[value.key].append(value.create(element))

			elif isinstance(value, _MCMulti):
				if value.key in json_body:
					self[value.key] = value.create(json_body[value.key])
