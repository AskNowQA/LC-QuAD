'''
	If the world ends because of this script, the culprit is - 
		Priyansh (pc.priyansh@gmail.com)

	This script is used to generate SPARQL Queries out of SPARQL templates, by traversing DBPedia. 
	Template Number - 8 (from https://docs.google.com/document/d/1N4KRy_xMD7B5cAnQWMiytRrPkZ-HwIEiZj4PbI-xROM/edit)
	
	Human Intervention - 
		list of domains and sub-domains from OWL file for DBPedia
		whitelist of acceptable properties
	Pseudocode - 
		find entities of one of the domains
		for all those entities, find their appropriate properties (from the whitelist)
		for the entity_resource - whiteproperty - resource pair, fill in the SPARQL Template

	SPARQL Template 
	SELECT DISTINCT ?uri WHERE {
		?uri pred1 res1
		?uri pred2 res2	
	}
'''

import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
from pprint import pprint
import time
#FLAGS
verbose = False
final_verify = False 		#Explanation: This flag is used for checking to see if every generated query generates an output or not
rate_limit = False


#MACROS
DOMAINS = ['http://dbpedia.org/ontology/Person']

#Developers: whitelist of properties stored in file
properties_whitelist = open('relation_whitelist.txt').read().split('\n')

def fill_template(_tup):
	'''	
		Expects a [(property, answer)] tuple to fill the appropriate template (Template 8)
		Return type - a list of strings
	'''
	head = 'SELECT DISTINCT ?uri WHERE '
	variable_name = '?uri'
	queries = []
	print "Printing Tuples"
	for i in range(len(_tup)):

		for j in range(len(_tup)):

			if not i == j:
				query = head + '{ ' + variable_name + " " + _tup[i][0] + " " + _tup[i][1] + ' . ' + variable_name + " " + _tup[j][0] + " " + _tup[j][1] + " }"
				queries.append(query)

	return queries

def verify_results(_list_of_queries):
	'''
		Throw every query to DBPedia and ensure that you get atleast one result back. If not, return false. Else true.
		Return type : Boolean
	'''
	pass

def start_rube_goldberg_machine():
	global DOMAINS, properties_whitelist, dbp

	#The sparql queries come here
	sparqls = []
	for domain in DOMAINS:
		
		if verbose: print domain
		#Find entities of the domains
		#TODO paginate this
		entities = dbp.get_entities_of_class(domain)
		useful_entities = [ x for x in entities if nlutils.is_alpha_with_underscores(x[28:]) ]

		for entity in useful_entities[:5]:

			if verbose: print entity
			#Get list of properties
			properties = dbp.get_properties_of_resource(entity, _with_connected_resource = True )
			useful_properties = [ x for x in properties if x[0][28:] in properties_whitelist ]

			if not len(useful_properties) >= 2:
				#Not enough property in this entity to fill the template
				if verbose: print "Not enough triples. Skipping!"
				continue
			else:
				#Filling the template now
				neue_sparqls = fill_template(useful_properties)
				time.sleep(1)
				sparqls += neue_sparqls

	return sparqls
			
if __name__ == '__main__':

	print "Will start trying to generate templates"

	#Setting some flags
	verbose = True

	#Create a DBPedia Object
	dbp = db_interface.DBPedia()

	#Let ze work begin
	sparqls = start_rube_goldberg_machine()

	#Poop out the output
	outputfile = open("output.txt",'w+')
	outputfile.write('\n\n\n'.join(sparqls))
	outputfile.close()

	print len(sparqls)

	#Lol doesn't work anyway
	if final_verify:
		verify_results(sparqls)


