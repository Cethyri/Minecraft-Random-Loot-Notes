import re
from typing import Match


def fix_a_an(string: str):
    return re.sub(r' a ([aeiou])', r' an \1', string)


def upper(match: Match[str]):
    return match.group(1).replace('_', ' ').upper()


def get_upper_selector(selector: str):
    return re.sub(r'((^|_)[a-z])', upper, selector)


def shorten_selector(selector: str):
    new_selector = re.sub(r'[_]', '', selector)
    return re.sub(r'([a-z]{10}).*$', r'\1', new_selector)


def remove_initial_dashes(string: str):
    return re.sub(r'^-+', '', string)
