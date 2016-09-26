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
import polishing.microsoft_api_5gram as polishing
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
r = '*rel' 	#The keyword representing the place where a correct preposition or is/are/has... will be put in by further modules

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
		Expects a [[property, answer] tuple to fill the appropriate template (Template 8)
		Return type - a list of strings
	'''
	head = 'SELECT DISTINCT ?uri WHERE '
	variable_name = '?uri'
	queries = []

	#Since the HTTP URIs need to be within a < >, we need to go through the triples and add this to all the triples
	for i in range(len(_tup)):
		if nlutils.has_literal(_tup[i][1]):
			_tup[i][1] = '"'+_tup[i][1]+'"@en'		#Assuming we are using literals only in english

		if nlutils.has_url(_tup[i][0]):
			_tup[i][0] = '<'+_tup[i][0]+'>'

		if nlutils.has_url(_tup[i][1]):
			_tup[i][1] = '<'+_tup[i][1]+'>'


	for i in range(len(_tup)):

		for j in range(len(_tup)):

			if not i == j:
				query = head + '{ ' + variable_name + " " + _tup[i][0] + " " + _tup[i][1] + ' . ' + variable_name + " " + _tup[j][0] + " " + _tup[j][1] + " }"
				queries.append(query)

	return queries

def get_pseudo_natural_language(_sparql):
	'''
		Code to convert SPARQL queries into some sort of an NL query. 
		IMPORTANT: This function assumes that the query is that of template 8.

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

	# #DEBUG
	# pprint(triples);raw_input('TRIPLES')	

	for t in triples:
		resources = t.split()
		resources_labelled = []
		
		for res in resources:
			
			#If the resource of the triple is a variable
			if res[0] == '?':
				resources_labelled.append(res)
				continue

			#Get label only if the resource is a URI
			if nlutils.has_url(res) or nlutils.has_shorthand(res):
				resources_labelled.append(dbp.get_label(res))
				continue

			#If the resource of the triple is not a URI, but a value like height or a label or something
			else:
				resources_labelled.append(res)

		splitted_triples.append(resources_labelled)

	#Now we can access each resource individually

	#Get Answer for the SPARQL query and it's type and then the type's label
	#http://dbpedia.org/resource/Bill_Gates -> http://dbpedia.org/resource/Person -> person
	
	answers = dbp.get_answer(_sparql)
	if len(answers) < 1:
		#No Answer found.
		print "NO ANSWER FOUND for ", _sparql
		#For now, simply ignore the question. Later, find better ways to do it.
		return None
	answer_type = dbp.get_type_of_resource(answers[0], _filter_dbpedia = True)[0]
	answer_type_label = dbp.get_label(answer_type)
	
	#Join all this together in a hardcoded template. TODO: Automate this, generalize across templates
	nlquery = ' '.join([ splitted_triples[0][1], r, splitted_triples[0][2], r, wh[0], answer_type_label, 'whose', splitted_triples[1][1], r, splitted_triples[1][2] ])

	# print nlquery
	return nlquery

def start_rube_goldberg_machine(_limit = None):
	global DOMAINS, dbp

	#The sparql queries come here
	sparqls = []
	for domain in DOMAINS:
		
		if verbose: print"DOMAIN: ", domain
		#Find entities of the domains
		entities = dbp.get_entities_of_class(domain)
		useful_entities = get_useful_entities(entities)

		#Slice the entities if the user wants to limit to something
		if _limit: useful_entities = useful_entities[:_limit]

		for entity in useful_entities:

			if verbose: print "ENTITY: ", entity
			#Get list of properties
			properties = dbp.get_properties_of_resource(entity, _with_connected_resource = True )
			useful_properties = get_useful_properties(properties)

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
	dbp =  db_interface.DBPedia(_verbose = True)

	#Run the code to get filled templates
	sparqls = start_rube_goldberg_machine(_limit = 2)

	#Put the SPARQLs Individually in a file. Then proceed
	outputfile = open("output/template-8-sparql.txt",'w+')
	outputfile.write('\n\n\n'.join(sparqls))
	outputfile.close()

	#Run the code to convert SPARQL to Pseudo-natural language
	psnlquestions = [ (x,get_pseudo_natural_language(x)) for x in sparqls]

	# #DEBUG
	# pprint(nlquestions)

	#Put the SPARQL and PsNL Queries in a file
	outputfile = open("output/template-8-sparql-pseudonl.txt","w+")
	outputfile.write('\n--------------------\n'.join([x[0]+'\n'+x[1] for x in psnlquestions]))
	outputfile.close()

	#Pass these Pseudo NL Questions into the polishing module and get their results
	# nlquestions = [] 
	# for tup in psnlquestions:
	# 	if tup[1] is None:
	# 		answers = [(0,None)]
	# 		nlquestions.append((tup[0],tup[1],answers))
	# 		continue

	# 	answers = polishing.create_question(tup[1])
	# 	answers = sorted(answers, key=lambda x:x[0])[-5:]
	# 	nlquestions.append((tup[0],tup[1],answers))
	# #These answers are in the format [(p,'q'),(p,'q')...]
	# #Print NLQ in a file
	# outputfile = open('output/template-8.txt','w+')
	# for q in nlquestions:
	# 	answers_str = ''
	# 	for answer in q[2]:
	# 		answer_str = ' '.join(answer[1]) + ', p:' + str(answer[0])[:min(5,len(str(answer[0])))]
	# 		answers_str = answer_str + '\n'
	# 	outputfile.write(q[0]+'\n'+q[1]+'\n'+answers_str+'\n-------------------\n')

	nlquestions = []
	for tup in psnlquestions:

		if tup[1] is None:
			answers = [None]
			nlquestions.append((tup[0],tup[1],answer))
			continue

		answers = polishing.create_question(nlutils.convert_to_no_symbols(tup[1]))[-5:]
		answers_str = []
		for answer in answers:
			answers_str.append(' '.join(answer))
		
		nlquestions.append((tup[0],tup[1],answers_str))

	outputfile = open('output/template-8.txt','w+')
	for q in nlquestions:
		outputfile.write(q[0]+'\n'+q[1]+'\n'+'\n'.join(q[2])+'\n------------------\n')