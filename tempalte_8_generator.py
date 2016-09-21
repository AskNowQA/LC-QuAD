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

#Pseudo Natural Language Grammer
#TODO: make it more comprehensive
wh = ['what','when','where','who','which','whose']
r = ['of','is']



#Developers: whitelist of properties stored in file
properties_whitelist = open('relation_whitelist.txt').read().split('\n')

###############GENERIC FUNCTIONS###############
def verify_results(_list_of_queries):
	'''
		Throw every query to DBPedia and ensure that you get atleast one result back. If not, return false. Else true.
		Return type : Boolean
	'''
	pass

def get_useful_properties(_properties):
	'''
		Modular function to write logic of selecting good properties. Can extend it to whatever use, later on.
	'''
	global properties_whitelist

	properties = [ x for x in _properties if x[0][28:] in properties_whitelist ]
	return properties

def get_useful_entities(_entities):
	'''
		Modular function to write logic of selecting good entitiess. Can extend it to whatever use, later on.
	'''
	entities = [ x for x in _entities if nlutils.is_alpha_with_underscores(x[28:]) ]
	return entities


###############SPECIFIC FUNCTIONS###############
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
				query = head + '{ ' + variable_name + " <" + _tup[i][0] + "> <" + _tup[i][1] + '> . ' + variable_name + " <" + _tup[j][0] + "> <" + _tup[j][1] + "> }"
				queries.append(query)

	return queries

def get_pseudo_natural_language(_sparql):
	'''
		Code to convert SPARQL queries into some sort of an NL query. 
		This function assumes that the query is that of template 8.

		Typical SPARQL Query - 
		SELECT DISTINCT ?uri WHERE { 
			?uri http://dbpedia.org/ontology/birthPlace http://dbpedia.org/resource/Uganda . 
			?uri http://dbpedia.org/property/genre http://dbpedia.org/resource/Afro 
		}

		Typical NL Response -

		[Wh] person [R] birthplace [R] Uganda <and> genre [R] afro
	'''
	global dbp,wh,r

	#Parsing the Query
	query = _sparql.strip().replace('<','').replace('>','').split('{')
	head = query[0]
	body = query[1][:-1]

	triples = body.strip().split(' . ') #See what we did there ;)

	splitted_triples = []
	for t in triples:
		resources = t.split()
		resources_labelled = []
		for res in resources:
			splitted_triples.append(dbp.get_label(x for t.split()))

	#Now we can access each resource individually

	#Get Answer for the SPARQL query and it's type
	answers = dbp.get_answer(_sparql)
	answer_type = dbp.get_type_of_resource(answers[0], _filter_dbpedia = True)[0]
	
	nlquery = ' '.join([ splitted_triples[0][1], r[0], splitted_triples[0][2], r[0], wh[0], answer_type, 'whose', splitted_triples[1][1], r[0], splitted_triples[1][2] ])

	print nlquery


def start_rube_goldberg_machine():
	global DOMAINS, dbp

	#The sparql queries come here
	sparqls = []
	for domain in DOMAINS:
		
		if verbose: print domain
		#Find entities of the domains
		entities = dbp.get_entities_of_class(domain)
		useful_entities = get_useful_entities(entities)

		for entity in useful_entities:

			if verbose: print entity
			#Get list of properties
			properties = dbp.get_properties_of_resource(entity, _with_connected_resource = True )
			useful_properties = get_useful_properties(property)

			if not len(useful_properties) >= 2:
				#Not enough property in this entity to fill the template
				if verbose: print "Not enough triples. Skipping!"
				continue
			else:
				#Filling the template now
				neue_sparqls = fill_template(useful_properties)
				sparqls += neue_sparqls

	return sparqls
			
if __name__ == '__main__':

	print "Will start trying to generate templates"

	# #Setting some flags
	verbose = True

	# #Create a DBPedia Object

	# #Run the code to get filled templates
	# sparqls = start_rube_goldberg_machine()

	# #Run the code to convert SPARQL to Pseudo-natural language
	# nlquestions = [ get_pseudo_natural_language(x) for x in sparqls]

	# #Poop out the output
	# outputfile = open("template-8-sparql.txt",'w+')
	# outputfile.write('\n\n\n'.join(sparqls))
	# outputfile.close()

	# outputfile = open("template-8-nlqs.txt",'w+')
	# outputfile.write('\n\n\n'.join(nlquestions))
	# outputfile.close()

	# print "Number of generated queries: ",len(sparqls)

	# #Lol doesn't work anyway
	# if final_verify:
	# 	verify_results(sparqls)

	dbp = db_interface.DBPedia()
	q = 'SELECT DISTINCT ?uri WHERE { ?uri <http://dbpedia.org/ontology/birthPlace> <http://dbpedia.org/resource/Mengo,_Uganda> . ?uri <http://dbpedia.org/ontology/birthPlace> <http://dbpedia.org/resource/Uganda> }'
	get_pseudo_natural_language(q)


