from typing import Union

from mcr.mc.properties import JsonDict
from mcr.mc.data_structures.range import IntRange, init_int_or_range


class eEnchantment(JsonDict):
    aqua_affinity = 'minecraft:aqua_affinity'
    bane_of_arthropods = 'minecraft:bane_of_arthropods'
    binding_curse = 'minecraft:binding_curse'
    blast_protection = 'minecraft:blast_protection'
    channeling = 'minecraft:channeling'
    depth_strider = 'minecraft:depth_strider'
    efficiency = 'minecraft:efficiency'
    feather_falling = 'minecraft:feather_falling'
    fire_aspect = 'minecraft:fire_aspect'
    fire_protection = 'minecraft:fire_protection'
    flame = 'minecraft:flame'
    fortune = 'minecraft:fortune'
    frost_walker = 'minecraft:frost_walker'
    impaling = 'minecraft:impaling'
    infinity = 'minecraft:infinity'
    knockback = 'minecraft:knockback'
    looting = 'minecraft:looting'
    loyalty = 'minecraft:loyalty'
    luck_of_the_sea = 'minecraft:luck_of_the_sea'
    lure = 'minecraft:lure'
    mending = 'minecraft:mending'
    multishot = 'minecraft:multishot'
    piercing = 'minecraft:piercing'
    power = 'minecraft:power'
    projectile_protection = 'minecraft:projectile_protection'
    protection = 'minecraft:protection'
    punch = 'minecraft:punch'
    quick_charge = 'minecraft:quick_charge'
    respiration = 'minecraft:respiration'
    riptide = 'minecraft:riptide'
    sharpness = 'minecraft:sharpness'
    silk_touch = 'minecraft:silk_touch'
    smite = 'minecraft:smite'
    sweeping = 'minecraft:sweeping'
    thorns = 'minecraft:thorns'
    unbreaking = 'minecraft:unbreaking'
    vanishing_curse = 'minecraft:vanishing_curse'


class Enchantment(JsonDict, overrides={'levels': init_int_or_range}):
    enchantment:	eEnchantment
    levels:			Union[IntRange, int]
