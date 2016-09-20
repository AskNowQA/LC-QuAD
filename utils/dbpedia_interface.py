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
import traceback
import warnings
import random

#Our scripts
import natural_language_utilities as nlutils

#GLOBAL MACROS
DBPEDIA_ENDPOINTS = ['http://dbpedia.org/sparql/','http://de.dbpedia.org/sparql/','http://live.dbpedia.org/sparql/']
MAX_WAIT_TIME = 1.0

#SPARQL Templates
GET_PROPERTIES_OF_RESOURCE = '''SELECT DISTINCT ?property WHERE { %(target_resource)s ?property ?useless_resource }
'''

GET_PROPERTIES_OF_RESOURCE_WITH_OBJECTS = '''SELECT DISTINCT ?property ?resource WHERE { %(target_resource)s ?property ?resource	}'''

GET_LABEL_OF_RESOURCE = '''SELECT DISTINCT ?label WHERE { %(target_resource)s <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER (lang(?label) = 'en')	} '''

GET_ENTITIES_OF_CLASS = ''' SELECT DISTINCT ?entity WHERE {	?entity <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %(target_class)s } '''

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
			return DBPEDIA_ENDPOINTS[index+1] if index < len(DBPEDIA_ENDPOINTS) else DBPEDIA_ENDPOINTS[0]

		if self.selection_method == 'select-one':
			return self.sparql_endpoint

		if selection_method == 'random':
			return random.choice(DBPEDIA_ENDPOINTS)

	def get_properties_of_resource(self,_resource_uri,_with_connected_resource = False):
		'''
			This function can fetch the properties connected to this '_resource', in the format - _resource -> R -> O
			The boolean flag can be used if we want to return the (R,O) tuples instead of just R

			Return Type 
				if _with_connected_resource == True, [ (R,O), (R,O), (R,O) ...]
				else [ R,R,R,R...]
		'''

		#Check if the resource URI is shorthand or a proper URI
		if not nlutils.has_url(_resource_uri):
			warnings.warn("The passed resource %s is not a proper URI but is in shorthand. This is strongly discouraged." % _resource_uri)
			_resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

		#Prepare the SPARQL Request
		sparql = SPARQLWrapper(self.sparql_endpoint)
		# with SPARQLWrapper(self.sparql_endpoint) as sparql:
		if _with_connected_resource:
			_resource_uri = '<'+_resource_uri+'>'
			sparql.setQuery(GET_PROPERTIES_OF_RESOURCE_WITH_OBJECTS % {'target_resource':_resource_uri} )
		else:
			_resource_uri = '<'+_resource_uri+'>'
			sparql.setQuery(GET_PROPERTIES_OF_RESOURCE % {'target_resource':_resource_uri} )
		sparql.setReturnFormat(JSON)
		response = sparql.query().convert()

		try:
			if _with_connected_resource:
				property_list = [ (x[u'property'][u'value'].encode('ascii','ignore'), x[u'resource'][u'value'].encode('ascii','ignore')) for x in response[u'results'][u'bindings'] ]
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
		sparql = SPARQLWrapper(self.sparql_endpoint)
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







