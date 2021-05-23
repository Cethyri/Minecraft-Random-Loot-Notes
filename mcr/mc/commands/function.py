from mcr.mc.commands.argument_types import NamespacedId
from mcr.mc.commands.command import Command


class Function(Command):
    def __init__(self, name: NamespacedId):
        super().__init__(f'function {name}')
