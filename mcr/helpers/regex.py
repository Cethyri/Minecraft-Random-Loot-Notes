import re
from typing import Match


def fix_a_an(string: str):
    return re.sub(r' a ([aeiou])', r' an \1', string)


def upper(match: Match[str]):
    return match.group(1).replace('_', ' ').upper()


def get_upper_name(name: str):
    return re.sub(r'((^|_)[a-z])', upper, name)


def shorten_name(name: str):
    new_name = re.sub(r'[_]', '', name)
    return re.sub(r'([a-z]{10}).*$', r'\1', new_name)


def remove_initial_dashes(string: str):
    return re.sub(r'^-+', '', string)
