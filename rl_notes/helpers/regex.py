import re

def fix_a_an(string: str):
	return re.sub(r' a ([aeiou])', r' an \1', string)

def upper(match):
	return match.group(1).replace('_', ' ').upper()

def get_upper_selector(selector):
	return re.sub(r'((^|_)[a-z])', upper, selector)

def shorten_selector(selector):
	new_selector = re.sub(r'[_]', '', selector)
	return re.sub(r'([a-z]{10}).*$', r'\1', new_selector)