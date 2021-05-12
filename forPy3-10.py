from abc import ABC
from inspect import signature, _empty
from typing import Callable, List, Optional, Type, TypeVar, Union, _UnionGenericAlias
import warnings
from mcr.mc.commands.function import Function
from mcr.mc.commands.mcfunction import MCFunction
from mcr.mc.commands.execute import Execute, eNBTType, eStoreReturn
from mcr.mc.commands.argument_types import BlockPos, Entity, NamespacedId, entity_anchor, selector, swizzle

class Validate(ABC):
	@classmethod
	def validate(cls, value):
		return value
		pass
	pass

T = TypeVar('T')

def self_validate(func: Callable):
	validations: dict[str, Callable[[T], T]] = {}
	
	for name, param in signature(func).parameters.items():
		#Refactor this in 3.10 to stop using Union and instead use | syntax which works with isinstance and (hopefully) issubclass
		if type(param.annotation) is _UnionGenericAlias:
			for t in param.annotation.__args__:
				if issubclass(t, Validate):
					validations[name] = t.validate
					break
		elif issubclass(type(param.annotation), Validate):
			validations[name] = t.validate

		elif type(param.annotation) is _empty:
			validations[name] = lambda arg: arg
		
		if name not in validations:
			def checkTypes(arg):
				if ((type(param.annotation) is _UnionGenericAlias and not any(issubclass(type(arg), t) for t in param.annotation.__args__))
					or not issubclass(type(arg), type(param.annotation))):
					# warnings.warn('Argument does not match type expectations')
					raise Exception('Argument does not match type expectations')
				return arg
			
			if type(param.annotation) is _UnionGenericAlias:
				validations[name] = checkTypes
			else:
				validations[name] = checkTypes

	def validated(*args, **kwargs):
		new_args = []
		new_kwargs = {}

		for arg, validation in zip(args, validations.values()):
			new_args.append(validation(arg))

		for name, arg in kwargs.items():
			new_kwargs[name] = validations[name](arg)

		return func(*new_args, **new_kwargs)

	return validated


@self_validate
def test_method(self, un: Union[Validate, str, Union[int, bool]], a, b):
	pass

test_method(3, 4, b = 1, a= False)

def allow_strings(func: Callable):
	pass
