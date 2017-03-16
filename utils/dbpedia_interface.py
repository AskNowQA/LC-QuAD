'''
	In case of a goofup, kill - Priyansh (pc.priyansh@gmail.com)
	This file is used to quench all the LOD desires of the main scripts. So, mostly a class with several DBPedia functions. 

	FAQ:
	Q: Why is every sparql request under a "with" block?
	A: With ensures that the object is thrown away when the request is done. 
		Since we choose a different endpoint at every call, it's a good idea to throw it away after use. I'm just being finicky probably, but it wouldn't hurt

	Q: What's with the warnings?
	A: Because I can, bitch.
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from operator import itemgetter
from pprint import pprint
import traceback
import warnings
import random

#Our scripts
import natural_language_utilities as nlutils

#GLOBAL MACROS
# DBPEDIA_ENDPOINTS = ['http://live.dbpedia.org/sparql/']
# 'http://dbpedia.org/sparql/','http://live.dbpedia.org/sparql/'
DBPEDIA_ENDPOINTS = ['http://131.220.153.66:8900/sparql']
MAX_WAIT_TIME = 1.0

#SPARQL Templates
GET_PROPERTIES_OF_RESOURCE = '''SELECT DISTINCT ?property WHERE { %(target_resource)s ?property ?useless_resource }'''

GET_PROPERTIES_ON_RESOURCE = '''SELECT DISTINCT ?property WHERE { ?useless_resource  ?property %(target_resource)s }'''

GET_PROPERTIES_OF_RESOURCE_WITH_OBJECTS = '''SELECT DISTINCT ?property ?resource WHERE { %(target_resource)s ?property ?resource	}'''

GET_ENTITIES_OF_CLASS = '''SELECT DISTINCT ?entity WHERE {	?entity <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %(target_class)s } '''

GET_LABEL_OF_RESOURCE = '''SELECT DISTINCT ?label WHERE { %(target_resource)s <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER (lang(?label) = 'en')	} '''

GET_TYPE_OF_RESOURCE = '''SELECT DISTINCT ?type WHERE { %(target_resource)s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type } '''

GET_CLASS_PATH = '''SELECT DISTINCT ?type WHERE { %(target_class)s rdfs:subClassOf* ?type }'''



class DBPedia:
	def __init__(self,_method='round-robin',_verbose=False):
		
		#Explanation: selection_method is used to select from the DBPEDIA_ENDPOINTS, hoping that we're not blocked too soon
		if _method in ['round-robin','random','select-one']:
			self.selection_method = _method 
		else:
			warnings.warn("Selection method not understood, proceeding with 'select-one'")
			self.selection_method = 'select-one'

		self.verbose = _verbose
		self.sparql_endpoint = DBPEDIA_ENDPOINTS[0]

	def select_sparql_endpoint(self):
		'''
			This function is to be called whenever we're making a call to DBPedia. Based on the selection mechanism selected at __init__,
			this function tells which endpoint to use at every point.
		'''
		if self.selection_method == 'round-robin':
			index = DBPEDIA_ENDPOINTS.index(self.sparql_endpoint)
			return DBPEDIA_ENDPOINTS[index+1] if index >= len(DBPEDIA_ENDPOINTS) else DBPEDIA_ENDPOINTS[0]

		if self.selection_method == 'select-one':
			return self.sparql_endpoint

		if selection_method == 'random':
			return random.choice(DBPEDIA_ENDPOINTS)

	def get_properties_on_resource(self, _resource_uri):
		'''
			Fetch properties that point to this resource. 
			Eg. 
			Barack Obama -> Ex-President of -> _resource_uri would yield ex-president of as the relation
		'''
		if not nlutils.has_url(_resource_uri):
			warnings.warn("The passed resource %s is not a proper URI but is in shorthand. This is strongly discouraged." % _resource_uri)
			_resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		sparql.setQuery(GET_PROPERTIES_ON_RESOURCE % {'target_resource':_resource_uri} )
		sparql.setReturnFormat(JSON)
		response = sparql.query().convert()


	def get_properties_of_resource(self,_resource_uri,_with_connected_resource = False):
		'''
			This function can fetch the properties connected to this '_resource', in the format - _resource -> R -> O
			The boolean flag can be used if we want to return the (R,O) tuples instead of just R

			Return Type 
				if _with_connected_resource == True, [ [R,O], [R,O], [R,O] ...]
				else [ R,R,R,R...]
		'''
		#Check if the resource URI is shorthand or a proper URI
		if not nlutils.has_url(_resource_uri):
			warnings.warn("The passed resource %s is not a proper URI but is in shorthand. This is strongly discouraged." % _resource_uri)
			_resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

		#Prepare the SPARQL Request
		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		# with SPARQLWrapper(self.sparql_endpoint) as sparql:
		_resource_uri = '<'+_resource_uri+'>'
		if _with_connected_resource:
			sparql.setQuery(GET_PROPERTIES_OF_RESOURCE_WITH_OBJECTS % {'target_resource':_resource_uri} )
		else:
			sparql.setQuery(GET_PROPERTIES_OF_RESOURCE % {'target_resource':_resource_uri} )
		sparql.setReturnFormat(JSON)
		response = sparql.query().convert()

		try:
			if _with_connected_resource:
				property_list = [ [x[u'property'][u'value'].encode('ascii','ignore'), x[u'resource'][u'value'].encode('ascii','ignore')] for x in response[u'results'][u'bindings'] ]
			else:
				property_list = [x[u'property'][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings']]
		except:
			#TODO: Find and handle exceptions appropriately 
			traceback.print_exc()
			# pass

		return property_list

	def get_entities_of_class(self, _class_uri):
		'''
			This function can fetch the properties connected to the class passed as a function parameter _class_uri.

			Return Type
				[ S,S,S,S...]
		'''
		#Check if the resource URI is shorthand or a proper URI
		if not nlutils.has_url(_class_uri):
			warnings.warn("The passed class %s is not a proper URI but is in shorthand. This is strongly discouraged." % _class_uri)
			_class_uri = nlutils.convert_shorthand_to_uri(_class_uri)

		#Preparing the SPARQL Query
		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		# with SPARQLWrapper(self.sparql_endpoint) as sparql:
		_class_uri = '<'+_class_uri+'>'
		sparql.setQuery(GET_ENTITIES_OF_CLASS % {'target_class':_class_uri} )
		sparql.setReturnFormat(JSON)
		response = sparql.query().convert()

		try:
			entity_list = [ x[u'entity'][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings'] ]
		except:
			#TODO: Find and handle exceptions appropriately
			traceback.print_exc()
			# pass

		return entity_list

	def get_type_of_resource(self, _resource_uri, _filter_dbpedia = False):
		'''
			Function fetches the type of a given entity
			and can optionally filter out the ones of DBPedia only
		'''

		if not nlutils.has_url(_resource_uri):
			warnings.warn("The passed resource %s is not a proper URI but probably a shorthand. This is strongly discouraged." % _resource_uri)
			_resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

		#Perparing the SPARQL Query
		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		_resource_uri = '<'+_resource_uri+'>'
		sparql.setQuery(GET_TYPE_OF_RESOURCE % {'target_resource': _resource_uri} )
		sparql.setReturnFormat(JSON)
		response = sparql.query().convert()

		try:
			type_list = [ x[u'type'][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings'] ]
		except:
			traceback.print_exc()



		#If we need only DBPedia's types
		if _filter_dbpedia:
			filtered_type_list = [x for x in type_list if x[:28] in ['http://dbpedia.org/ontology/','http://dbpedia.org/property/'] ]
			return filtered_type_list

		return type_list

	def get_answer(self, _sparql_query):
		'''
			Function used to shoot a query and get the answers back. Easy peasy.

			Return - array of values of first variable of query
			NOTE: Only give it queries with one variable
		'''

		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		sparql.setQuery(_sparql_query)
		sparql.setReturnFormat(JSON)
		try:
			response = sparql.query().convert()
		except:
			traceback.print_exc()

		#Now to parse the response
		variables = [x for x in response[u'head'][u'vars']]

		#NOTE: Assuming that there's only one variable
		values = {}
		for index in xrange(0,len(variables)):
			value = [ x[variables[index]][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings'] ]
			values[variables[index]] = value 
		return values

	def get_label(self, _resource_uri):
		'''
			Function used to fetch the english label for a given resource.
			Not thoroughly tested tho.

			Always returns one value
		'''

		if not nlutils.has_url(_resource_uri):
			warnings.warn("The passed resource %s is not a proper URI but probably a shorthand. This is strongly discouraged." % _resource_uri)
			_resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

		#Preparing the Query
		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		_resource_uri = '<'+_resource_uri+'>'
		sparql.setQuery(GET_LABEL_OF_RESOURCE % {'target_resource': _resource_uri} )
		sparql.setReturnFormat(JSON)
		try:
			response = sparql.query().convert()
		except:
			traceback.print_exc()

		#Parsing the results
		try:
			results = [x[u'label'][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings'] ]
		except:
			traceback.print_exc()

		return results[0]

	def shoot_custom_query(self, _custom_query):
		'''	
			Shoot any custom query and get the SPARQL results as a dictionary
		'''
		sparql = SPARQLWrapper(self.select_sparql_endpoint())
		sparql.setQuery(_custom_query)
		sparql.setReturnFormat(JSON)
		return sparql.query().convert()

	def get_most_specific_class(self, _resource_uri):
		'''
			Query to find the most specific DBPedia Ontology class given a URI.
			Limitation: works only with resources.
			@TODO: Extend this to work with ontology (not entities) too. Or properties.
		'''
		if not nlutils.has_url(_resource_uri):
			warnings.warn("The passed resource %s is not a proper URI but probably a shorthand. This is strongly discouraged." % _resource_uri)
			_resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

		#Get the DBpedia classes of resource
		classes = self.get_type_of_resource(_resource_uri, _filter_dbpedia = True)

		'''debug'''
		# print "resource uri is " + _resource_uri
		# print "returned classes are " + str(len(classes))
		# for x in classes:
		# 	print x
		
		length_array = []	#A list of tuples, it's use explained below

		#For every class, find the length of path to owl:Thing.
		for class_uri in classes:

			#Preparing the query
			sparql =  SPARQLWrapper(self.select_sparql_endpoint())
			target_class = '<'+class_uri+'>'
			sparql.setQuery(GET_CLASS_PATH % {'target_class':target_class} )
			sparql.setReturnFormat(JSON)
			try:
				response = sparql.query().convert()
			except:
				traceback.print_exc()

			#Parsing the Result
			try:
				results = [x[u'type'][u'value'].encode('ascii','ignore') for x in response[u'results'][u'bindings'] ]
			except:
				traceback.print_exc()

			#Count the number of returned classes and store it in treturn max(length_array,key=itemgetter(1))[0]he list.
			length_array.append( (class_uri,len(results)) )
		# pprint(length_array)
		if len(length_array) > 0:
			return max(length_array,key=itemgetter(1))[0]
		else:
			#if there is no results from the filter type , return it as owl Thing 
			return "http://www.w3.org/2002/07/owl#Thing"	
if __name__ == '__main__':
	pass
	# print "\n\nBill Gates"
	# pprint(dbp.get_type_of_resource('http://dbpedia.org/resource/Bill_Gates', _filter_dbpedia = True))
	# print "\n\nIndia"
	# pprint(dbp.get_type_of_resource('http://dbpedia.org/resource/India', _filter_dbpedia = True))
	# dbp = DBPedia()
	# q = 'SELECT DISTINCT ?uri, ?a WHERE { ?uri <http://dbpedia.org/ontology/birthPlace> <http://dbpedia.org/resource/Mengo,_Uganda> . ?uri <http://dbpedia.org/ontology/birthPlace> ?a }'
	# pprint(dbp.get_answer(q))

	
	# uri = 'http://dbpedia.org/resource/Donald_Trump'
	# print dbp.get_most_specific_class(uri)

	# q = 'http://dbpedia.org/ontology/birthPlace'
	# pprint(dbp.get_label(q))

	# q = 'http://dbpedia.org/resource/Bill_Gates'
	# pprint(dbp.get_label(q))
