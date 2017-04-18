import validators
import string
import re
import os.path
from urlparse import urlparse

#SOME MACROS
KNOWN_SHORTHANDS = ['dbo','dbp','rdf','rdfs','dbr']	

#Few regex to convert camelCase to _ i.e DonaldTrump to donald trump
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

#@TODO Import the above list from http://dbpedia.org/sparql?nsdecl

def has_url(_string):
	if validators.url(_string):
		return True
	return False

def is_clean_url(_string):
	'''
		!!!! ATTENTION !!!!!
		Radical changes about. 

	'''
	if validators.url(_string):
		
		if _string[-3:-1] == '__' and _string[-1] in string.digits:
			return False
		if _string[-1] == ',':
			return False
		if 'dbpedia' not in _string:
			return False

		#Lets kick out all the literals too?
		return True
	else:
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

def convert_to_no_symbols(_string):
	new_string = ''
	for char in _string:
		if char not in string.letters+string.digits+' *':
			continue
		new_string += char
	return new_string

def convert_shorthand_to_uri(_string):
	#TODO: Dis function
	return _string

def is_alpha_with_underscores(_string):
	for char in _string:
		if not char in string.letters+'_':
			return False
			
	return True

def convert(_string):
	s1 = first_cap_re.sub(r'\1_\2', _string)
	return all_cap_re.sub(r'\1_\2', s1)

def get_label_via_parsing(_uri, lower = False):
	parsed = urlparse(_uri)
	path = os.path.split(parsed.path)
	unformated_label = path[-1]
	label = convert(unformated_label)
	label = " ".join(label.split("_"))
	if lower:
		return label.lower()
	return label

if __name__ == "__main__":
	uris = ["http://dbpedia.org/ontology/Airport", "http://dbpedia.org/property/garrison", "<http://dbpedia.org/property/MohnishDubey"]
	for uri in uris:
		print get_label_via_parsing(uri)