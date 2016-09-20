import string
import re

def has_url(_string):
	#TODO: Change the logic here
	return True

def convert_shorthand_to_uri(_string):
	#TODO: Dis function
	return _string

def is_alpha_with_underscores(_string):
	for char in _string:
		if not char in string.letters+'_':
			return False
			
	return True