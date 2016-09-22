import validators
import string
import re

#SOME MACROS
KNOWN_SHORTHANDS = ['dbo','dbp','rdf','rdfs','dbr']	
#TODO Import the above list from http://dbpedia.org/sparql?nsdecl

def has_url(_string):
	if validators.url(_string):
		return True
	return False

def has_shorthand(_string):
	splitted_string = _string.split(':')
	
	if len(splitted_string) == 1:
		return False

	if splitted_string[0] in KNOWN_SHORTHANDS:
		#Validate the right side of the ':'
		if '/' in splitted_string[1]:
			return False

		return True

	return False

def has_literal(_string):
	#Very rudementary logic. Make it better sometime later.
	if has_url(_string) or has_shorthand(_string):
		return False
	return True
	

def convert_shorthand_to_uri(_string):
	#TODO: Dis function
	return _string

def is_alpha_with_underscores(_string):
	for char in _string:
		if not char in string.letters+'_':
			return False
			
	return True