
'''
	Author: pc.priyansh@gmail.com (Priyansh Trivedi)

	A simple parser to find all the queries shot to DBpedia which happen to have a count query. 
	Thereafter, find the queries which are not more than 4 triple long
'''


import os
import sys
import inspect
import urlparse
import traceback
from pprint import pprint

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import utils.natural_language_utilities as nlu

relations_whitelist = []

folder_path = '../resources/dbplogs/'
files = os.listdir(folder_path)

def parse_line(_query):
	q = urlparse.urlparse(_query).query
	query = urlparse.parse_qs(q)['query'][0].replace('\n','').replace('\r',' ')
	return query

def has_count(_query):
	q = _query.lower()
	if ' count(' in q.split('where')[0]:
		return True
	return False

def has_few_triples(_query):
	triple = _query.lower().split('where')[-1].replace('{','').replace('}','').strip()
	if len(triple.split('.')) <= 4:
		return True
	return False

def extract_relations(_query):
	#Code to extract all the predicates out of the query
	query_triples = _query.replace('where','WHERE').replace('Where','WHERE').split('WHERE')[1:]
	query_triples = ' '.join([x for x in query_triples]).strip().lstrip('{').rstrip('}').strip()

	if 'optional' in _query.lower() or 'union' in query.lower():
		return []

	# print query_triples
	# raw_input("This is query triple")
	
	tokens = query_triples.split()

	triple_list = [[]]
	number_of_triple = 0
	for token in tokens:
		
		if token.upper() in ['FILTER','ORDER','LIMIT']:
			triple_list[number_of_triple] += ['BAD TOKEN','IGNORING THIS','CREATING MORE THAN THREE THINGS SO AS TO SKIP THIS TRIPLE','POOP']
			continue

		if token == '.':
			#Everything preceding this was in a different triple, everythng after this is in a new triple
			number_of_triple += 1
			triple_list.append([])

		elif token[0] == '.':
			#Everything preceding this token was in a different triple, this and everything after this is in a new triple
			number_of_triple += 1
			triple_list.append([token[1:]])

		elif token[-1] == '.':
			#This triple will be put in the old list, but everything AFTER this goes onto the next triple
			triple_list[number_of_triple].append(token)
			number_of_triple += 1
			triple_list.append([])

		else:
			triple_list[number_of_triple].append(token)

	#Now that we haz the triples. Delete all those which have more than three members, or less than two.
	relations = [ x[1] for x in triple_list if len(x) == 3]

	#Now to clean the relations.
	cleaned_relations = []
	for relation in relations:

		if '<' == relation[0] and '>' == relation[-1]:
			#It might be a URI
			if not nlu.has_url(relation[1:-1]):
				continue

			#It is a URI.
			if nlu.is_clean_url(relation[1:-1]):
				cleaned_relations.append(relation[1:-1])
				continue

		#See if it is a dbpedia shorthand
		rel = nlu.is_dbpedia_shorthand(relation, _convert = True)
		if rel:
			cleaned_relations.append(rel)

	# print relations
	# print cleaned_relations
	# raw_input()
	return cleaned_relations


for filename in files:

	print "About to open ", filename
	file = open(folder_path+filename)

	#Read the file line by line
	for line in file:

		#Parse the line to extract the SPARQL
		try:
			query = parse_line(line)
		except:
			#If it's not parsable, skip this one
			#DEBUG
			# print "Cannot parse: ", line.replace('\n','')
			continue

		#Check if it is a count query
		if has_count(query):
			if has_few_triples(query):
				relations_whitelist += extract_relations(query)

pprint(list(set(relations_whitelist)))