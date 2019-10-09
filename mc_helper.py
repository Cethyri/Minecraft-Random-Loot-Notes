from typing import List, Callable, Dict, NewType, TypeVar

T = TypeVar('T')

def _dynamic_getter(key: str, return_type: T):
	def getter(self) -> return_type:
		return self[key]

	return getter

def _dynamic_setter(key: str, value_type: T):
	def setter(self, value: value_type):
		self[key] = value
	
	return setter


class _MCObj(property):
	def __init__(self, key: str, prop_type: T, getter: Callable, setter: Callable):
		super().__init__(getter, setter)
		self.key = key
		self.prop_type = prop_type

class _MCList(_MCObj):
	pass

class _MCMulti(property):
	def __init__(self, key: str, create: Callable, getter: Callable, setter: Callable):
		super().__init__(getter, setter)
		self.key = key
		self.create = create

class _MCMultiList(_MCMulti):
	pass

class _MCMultiDict(_MCMulti):
	pass


def mc_obj(key: str, prop_type: T) -> property:
	return _MCObj(key, prop_type, _dynamic_getter(key, prop_type), _dynamic_setter(key, prop_type))

def mc_list(key: str, elem_type: T) -> property:
	return _MCList(key, elem_type, _dynamic_getter(key, List[elem_type]), _dynamic_setter(key, List[elem_type]))

def mc_multi(key: str, prop_type: T, create: Callable) -> property:
	return _MCMulti(key, create, _dynamic_getter(key, prop_type), _dynamic_setter(key, prop_type))

def mc_multi_list(key: str, elem_type: T, create_elem: Callable) -> property:
	return _MCMultiList(key, create_elem, _dynamic_getter(key, List[elem_type]), _dynamic_setter(key, List[elem_type]))

def mc_multi_dict(key: str, elem_type: T, create_elem: Callable) -> property:
	return _MCMultiDict(key, create_elem, _dynamic_getter(key, Dict[str, elem_type]), _dynamic_setter(key, Dict[str, elem_type]))


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

			if isinstance(value, _MCMultiDict):
				if value.key in json_body:
					self[value.key] = {}
					for key, element in json_body[value.key]:
						self[value.key][key] = (value.create(element))

			if isinstance(value, _MCMultiList):
				if value.key in json_body:
					self[value.key] = []
					for element in json_body[value.key]:
						self[value.key].append(value.create(element))

			elif isinstance(value, _MCMulti):
				if value.key in json_body:
					self[value.key] = value.create(json_body[value.key])
