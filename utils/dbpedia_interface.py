"""
    In case of a goofup, kill - Priyansh (pc.priyansh@gmail.com)
    This file is used to quench all the LOD desires of the main scripts. So, mostly a class with several DBPedia functions.

    FAQ:
    Q: Why is every sparql request under a "with" block?
    A: With ensures that the object is thrown away when the request is done.
        Since we choose a different endpoint at every call, it's a good idea to throw it away after use.
        I'm just being finicky probably, but it wouldn't hurt

    Q: Ew this looks ugly.
    A: I just discovered PEP8, go easy on me senpai.

    Q: Typesafe?
    A: No. If its an error, it'll throw a big wild error.
"""
from SPARQLWrapper import SPARQLWrapper, JSON
from operator import itemgetter
from functools import partial
from pprint import pprint
import numpy as np
import traceback
import textwrap
import warnings
import pickle
import atexit
import redis
import json
import re

# Our scripts

try:
    import natural_language_utilities as nlutils
except ImportError:
    from utils import natural_language_utilities as nlutils

try:
    from goodies import *
except ImportError:
    from utils.goodies import *

# GLOBAL MACROS
# DBPEDIA_ENDPOINTS = 'http://dbpedia.org/sparql/'
DBPEDIA_ENDPOINT = 'http://localhost:8890/sparql/'
# DBPEDIA_ENDPOINTS = 'http://131.220.153.66:7890/sparql'
# DBPEDIA_ENDPOINTS = 'http://localhost:8164/sparql/'
# DBPEDIA_ENDPOINTS = 'http://sda-srv01.iai.uni-bonn.de:8164/sparql'
# REDIS_HOSTNAME = 'sda-srv01'
REDIS_HOSTNAME  = '127.0.0.1'
MAX_WAIT_TIME = 10.0
ASK_RE_PATTERN = '(?i)ask\s*where'

LABELS_LOC = 'resources/labels.pickle'
CLASSES_LOC = 'resources/classes.json'


'''
Endpoint information for sda-srv04 - might/not work
DBPEDIA_ENDPOINTS = ['http://sda-srv01:8890/sparql']
REDIS_HOSTNAME = 'sda-srv01'
#REDIS_HOSTNAME  = '127.0.0.1'
MAX_WAIT_TIME = 1.0
'''

'''
Endpoint information for QROWDGPU
# GLOBAL MACROS
# DBPEDIA_ENDPOINTS = ['http://dbpedia.org/sparql/']
DBPEDIA_ENDPOINTS = ['http://localhost:8164/sparql/']
# DBPEDIA_ENDPOINTS = ['http://131.220.153.66:7890/sparql']
#DBPEDIA_ENDPOINTS = ['http://sda-srv01:8890/sparql']
REDIS_HOSTNAME = 'sda-srv01'
#REDIS_HOSTNAME  = '127.0.0.1'
MAX_WAIT_TIME = 1.0
'''

# SPARQL Templates
GET_RIGHT_PROPERTIES_OF_RESOURCE = '''SELECT DISTINCT ?property WHERE { %(target_resource)s ?property ?useless_resource }'''

GET_LEFT_PROPERTIES_OF_RESOURCE = '''SELECT DISTINCT ?property WHERE { ?useless_resource ?property %(target_resource)s }'''

GET_PROPERTIES_ON_RESOURCE = '''SELECT DISTINCT ?property WHERE { ?useless_resource  ?property %(target_resource)s }'''

GET_RIGHT_PROPERTIES_OF_RESOURCE_WITH_OBJECTS = '''SELECT DISTINCT ?property ?resource WHERE { %(target_resource)s ?property ?resource	}'''

GET_LEFT_PROPERTIES_OF_RESOURCE_WITH_OBJECTS = '''SELECT DISTINCT ?property ?resource WHERE { ?resource ?property %(target_resource)s }'''

GET_ENTITIES_OF_CLASS = '''SELECT DISTINCT ?entity WHERE {	?entity <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %(target_class)s } '''

GET_LABEL_OF_RESOURCE = '''SELECT DISTINCT ?label WHERE { %(target_resource)s <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER (lang(?label) = 'en')	} '''

GET_TYPE_OF_RESOURCE = '''SELECT DISTINCT ?type WHERE { %(target_resource)s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type } '''

GET_CLASS_PATH = '''SELECT DISTINCT ?type WHERE { %(target_class)s rdfs:subClassOf* ?type }'''

GET_SUPERCLASS = '''SELECT DISTINCT ?type WHERE { %(target_class)s rdfs:subClassOf ?type }'''

CHECK_URL = '''ASk {<%(target_resource)s> a owl:Thing} '''

GET_SUBJECT = '''SELECT DISTINCT ?entity WHERE { ?entity %(property)s %(target_resource)s } '''

GET_OBJECT = '''SELECT DISTINCT ?entity WHERE {	%(target_resource)s %(property)s ?entity } '''

GET_SAME_AS = '''SELECT DISTINCT ?entity WHERE {?entity owl:sameAs %(target_resource)s}'''

GET_LEFT_RIGHT_PROPERTIES_OF_RESOURCE_WITH_RIGHT_PROPERTY = '''SELECT DISTINCT ?property1 ?property2 
                                                                WHERE {   
                                                                %(target_resource)s  %(property)s ?useless_resource .
                                                                {optional {?useless_resource ?property1 ?useless_resource_2}}
                                                                UNION
                                                                {optional {?useless_resource_3 ?property2 ?useless_resource}}
                                                                FILTER(!isLiteral(?useless_resource) && !isLiteral(?useless_resource_2) && !isLiteral(?useless_resource_3))
                                                                } LIMIT 10000 OFFSET %(offset)s '''
GET_LEFT_RIGHT_PROPERTIES_OF_RESOURCE_WITH_LEFT_PROPERTY = '''SELECT DISTINCT ?property1 ?property2 
                                                                WHERE {   
                                                                ?useless_resource   %(property)s  %(target_resource)s.
                                                                {optional {?useless_resource ?property1 ?useless_resource_2}}
                                                                UNION
                                                                {optional {?useless_resource_3 ?property2 ?useless_resource}}
                                                                FILTER(!isLiteral(?useless_resource) && !isLiteral(?useless_resource_2) && !isLiteral(?useless_resource_3))
                                                                } LIMIT 10000 OFFSET %(offset)s'''


formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
    formatwarning_orig(textwrap.fill(str(message)), category, filename, lineno, line="")


def save_to_disk(obj, ctr, loc, msg):
    if len(obj) > ctr:
        with open(loc, 'w+') as f:
            json.dump(obj, f)
            print(msg)


class DBPedia:

    def __init__(self, _verbose=False, _db_name=0, _endpoint=None, _caching=True):

        if not _endpoint:
            self.sparql_endpoint = DBPEDIA_ENDPOINT
        else:
            self.sparql_endpoint = DBPEDIA_ENDPOINT
        self.global_endpoint = 'http://dbpedia.org/sparql'

        self.verbose = _verbose
        if _caching:
            self.r = redis.StrictRedis(host=REDIS_HOSTNAME, port=6379, db=_db_name)
        else:
            self.r = False

        # Try pulling URI surface forms from disk.
        try:
            self.labels = pickle.load(open(LABELS_LOC, 'rb'))
        except (UnicodeDecodeError, IOError, FileNotFoundError) as e:
            warnings.warn("Label cache can't be loaded from %s. Creating a new one" % LABELS_LOC)
            self.labels = {}
        finally:
            self.org_labels_num = len(self.labels)

        # Try pulling URI class list from disk
        try:
            self.classes = json.load(open(CLASSES_LOC))
        except (UnicodeDecodeError, IOError, FileNotFoundError, EOFError) as e:
            warnings.warn("Specific Classes cache can't be loaded from %s. Creating a new one" % LABELS_LOC)
            self.classes = {}
        finally:
            self.org_classes_num = len(self.classes)

        # At exit, send some things to disk
        atexit.register(save_to_disk, self.classes, self.org_classes_num, CLASSES_LOC, "Written classes dict to file.")
        # atexit.register(save_to_disk, self.labels, self.org_labels_num, CLASSES_LOC, "Written labels dict to file.")

    def _prep_query_(self, _custom_query, _at_global=False):
        if not _at_global:
            sparql = SPARQLWrapper(self.sparql_endpoint)
        else:
            sparql = SPARQLWrapper(self.global_endpoint)
        sparql.setQuery(_custom_query.replace('\n', '').replace('  ', ' '))
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(MAX_WAIT_TIME)
        return sparql

    @staticmethod
    def _prep_uri_(_uri):
        if not nlutils.has_url(_uri):
            warnings.warn(
                "The passed resource %s is not a proper URI but is in shorthand. Strongly discouraged." % _uri)
            _uri = nlutils.is_dbpedia_shorthand(_uri, _convert=True)

        if not _uri[0] == '<': _uri = '<' + _uri
        if not _uri[-1] == '>': _uri = _uri + '>'

        return _uri

    def shoot_custom_query(self, _custom_query, _long=False, _at_global=False):
        """
            Shoot any custom query and get the SPARQL results as a dictionary.
        """
        if self.r:
            answer = self.r.get(_custom_query)
            if answer:
                return json.loads(answer)

        # Either caching is disabled, or the query isn't cached.
        sparql = self._prep_query_(_custom_query, _at_global)
        answer = sparql.query().convert()
        if self.r: self.r.set(_custom_query, json.dumps(answer))

        return answer

    def get_properties_on_resource(self, _resource_uri):
        """
            Fetch properties that point to this resource.
            Eg.
            Barack Obama -> Ex-President of -> _resource_uri would yield ex-president of as the relation

            # @TODO: process the answers further and return dict/list
        """
        _resource_uri = self._prep_uri_(_resource_uri)
        response = self.shoot_custom_query(GET_PROPERTIES_ON_RESOURCE % {'target_resource': _resource_uri})
        return response

    def get_properties_of_resource(self, _resource_uri, _with_connected_resource=False, _outgoing=True):
        """
        This function can fetch the properties connected to this '_resource', in the format - _resource -> R -> O
            The boolean flag can be used if we want to return the (R,O) tuples instead of just R

            Return Type
                if _with_connected_resource == True, [ [R,O], [R,O], [R,O] ...]
                else [ R,R,R,R...]

        :param _resource_uri: str: uri of resource whose properties are to be found.
        :param _with_connected_resource: bool: flag. True -> return pred and end, else only pred
        :param _outgoing: bool: flag. True -> need outgoing pred; False -> need incoming pred.
        """
        # Check if the resource URI is shorthand or a proper URI
        _resource_uri = self._prep_uri_(_resource_uri)

        if _with_connected_resource:
            if _outgoing:
                temp_query = GET_RIGHT_PROPERTIES_OF_RESOURCE_WITH_OBJECTS % {'target_resource': _resource_uri}
            else:
                temp_query = GET_LEFT_PROPERTIES_OF_RESOURCE_WITH_OBJECTS % {'target_resource': _resource_uri}
        else:
            if _outgoing:
                temp_query = GET_RIGHT_PROPERTIES_OF_RESOURCE % {'target_resource': _resource_uri}
            else:
                temp_query = GET_LEFT_PROPERTIES_OF_RESOURCE % {'target_resource': _resource_uri}

        response = self.shoot_custom_query(temp_query)

        # Parse and prep response
        try:
            if _with_connected_resource:
                property_list = [[x[u'property'][u'value'].encode('utf-8', 'ignore'),
                                  x[u'resource'][u'value'].encode('utf-8', 'ignore')] for x in
                                 response[u'results'][u'bindings']]
            else:
                property_list = [x[u'property'][u'value'].encode('utf-8', 'ignore') for x in
                                 response[u'results'][u'bindings']]
        except:
            # TODO: Find and handle exceptions appropriately
            traceback.print_exc()
            property_list = []

        return property_list

    def get_entities_of_class(self, _class_uri):
        """
        This function can fetch the properties connected to the class passed as a function parameter _class_uri.

        Return Type
            [ S,S,S,S...]
        """

        _class_uri = self._prep_uri_(_class_uri)

        response = self.shoot_custom_query(GET_ENTITIES_OF_CLASS % {'target_class': _class_uri})

        entity_list = [x[u'entity'][u'value'].encode('ascii', 'ignore')
                       for x in response[u'results'][u'bindings']]

        return entity_list

    def get_type_of_resource(self, _resource_uri, _filter_dbpedia=False):
        """
            Function fetches the type of a given entity
            and can optionally filter out the ones of DBPedia only
        """
        _resource_uri = self._prep_uri_(_resource_uri)
        response = self.shoot_custom_query(GET_TYPE_OF_RESOURCE % {'target_resource': _resource_uri})
        type_list = [x[u'type'][u'value'] for x in response[u'results'][u'bindings']]

        # If we need only DBPedia's types
        if _filter_dbpedia:
            filtered_type_list = [x for x in type_list if
                                  x[:28] in ['http://dbpedia.org/ontology/']]
            return filtered_type_list

        return type_list

    def get_answer(self, _sparql_query):
        """
            Function used to shoot a query and get the answers back. Easy peasy.

            Return - array of values of first variable of query
            NOTE: Only give it queries with one variable

        """
        response = self.shoot_custom_query(_sparql_query)

        matcher = re.search(ASK_RE_PATTERN, _sparql_query, 0)
        values = {}
        if matcher:
            values['boolean'] = response['boolean']
            return values
        # Now to parse the response
        variables = [x for x in response[u'head'][u'vars']]

        # NOTE: Assuming that there's only one variable
        for index in range(0, len(variables)):
            value = [x[variables[index]][u'value'] for x in response[u'results'][u'bindings']]
            values[variables[index]] = value
        return values

    def get_label(self, _resource_uri):
        """
            Function used to fetch the english label for a given resource.
            Not thoroughly tested tho.

           @TODO: start getting labels from dbp instead of by parsing URL

            Always returns one value
        """
        # # First try finding it in file
        # try:
        #     label = self.labels[_resource_uri[1:-1]][0]
        #     # print "Label for %s found in cache." % _resource_uri
        #     return label
        #
        # except KeyError:
        #     # Label not found in file. Throw it as a query to DBpedia
        #     # print "####", "its a key error"
        #     try:
        #         # print _resource_uri
        #         response = self.shoot_custom_query(GET_LABEL_OF_RESOURCE % {'target_resource': _resource_uri})
        #
        #         results = [x[u'label'][u'value'].encode('ascii', 'ignore') for x in response[u'results'][u'bindings']]
        #         if len(results) > 0:
        #             self.labels[_resource_uri[1:-1]] = results
        #         else:
        #             p = results[0]  # Should raise exception
        #         self.fresh_labels += 1
        #
        #         if self.fresh_labels >= 10:
        #             f = open('resources/labels.pickle', 'w+')
        #             pickle.dump(self.labels, f)
        #             f.close()
        #             self.fresh_labels = 0
        #             print "Labels dumped to file."
        #
        #         return self.labels[_resource_uri[1:-1]][0]
        #     except IndexError as e:
        #         # print e
        #         # print _resource_uri, results
        #         # raw_input()
        #         return nlutils.get_label_via_parsing(_resource_uri)
        #
        #     except:
        #         # print "in Exception"
        #         traceback.print_exc()
        #         # raw_input()
        #         return nlutils.get_label_via_parsing(_resource_uri)
        #
        # except:
        #     return nlutils.get_label_via_parsing(_resource_uri)

        # print _resource_uri, "**"
        if not nlutils.has_url(_resource_uri):
            _resource_uri = nlutils.convert_shorthand_to_uri(_resource_uri)

        # Remove leading and trailing angle brackets
        _resource_uri = _resource_uri.replace('<', '').replace('>', '')

        # Preparing the Query
        _resource_uri = '<' + _resource_uri + '>'

        return nlutils.get_label_via_parsing(_resource_uri)

    def get_most_specific_class(self, _resource_uri):
        """
            Function which gets the deepest dbo:<ClassName> for a given resource.
        :param _resource_uri: str
        :return:
        """

        # Try to see if the we have it cached.
        try:
            return self.classes[_resource_uri]
        except KeyError:
            # Not found in cache
            cls = self._get_most_specific_class_(_resource_uri)
            self.classes[_resource_uri] = cls
            return cls

    def _get_most_specific_class_(self, _resource_uri):
        """
            Query to find the most specific DBPedia Ontology class given a URI.
            Limitation: works only with resources.
            @TODO: Extend this to work with ontology (not entities) too. Or properties.
        """

        # Get the DBpedia classes of resource
        classes = self.get_type_of_resource(_resource_uri, _filter_dbpedia=True)

        length_array = []  # A list of tuples, it's use explained below

        # For every class, find the length of path to owl:Thing.
        for class_uri in classes:

            # Preparing the query
            target_class = '<' + class_uri + '>'
            response = self.shoot_custom_query(GET_CLASS_PATH % {'target_class': target_class}, _at_global=True)

            # Parsing the Result
            results = [x[u'type'][u'value'] for x in response[u'results'][u'bindings']]

            # Count the number of returned classes and store it in
            length_array.append((class_uri, len(results)))

        if len(length_array) > 0:
            return max(length_array, key=itemgetter(1))[0]
        else:
            # If there is no results from the filter type , return it as owl Thing
            warnings.warn("Could not find classes for %s. Returning owl:Thing." % _resource_uri, EntityTypeNotFound)
            return "http://www.w3.org/2002/07/owl#Thing"

    def is_common_parent(self, _resource_uri_1, _resource_uri_2):
        specific_class_uri_1 = "<" + self.get_most_specific_class(_resource_uri_1) + ">"
        specific_class_uri_2 = "<" + self.get_most_specific_class(_resource_uri_2) + ">"
        try:
            response_uri_1 = self.shoot_custom_query(GET_SUPERCLASS % {'target_class': specific_class_uri_1})
            response_uri_2 = self.shoot_custom_query(GET_SUPERCLASS % {'target_class': specific_class_uri_2})
        except:
            traceback.print_exc()

        # Parsing the results
        try:
            results_1 = [x[u'type'][u'value'].encode('ascii', 'ignore') for x in
                         response_uri_1[u'results'][u'bindings']]
            results_2 = [x[u'type'][u'value'].encode('ascii', 'ignore') for x in
                         response_uri_2[u'results'][u'bindings']]
        except:
            traceback.print_exc()

        filtered_type_list_1 = [x for x in results_1 if
                                x[:28] in ['http://dbpedia.org/ontology/', 'http://dbpedia.org/property/']]
        filtered_type_list_2 = [x for x in results_2 if
                                x[:28] in ['http://dbpedia.org/ontology/', 'http://dbpedia.org/property/']]

        if filtered_type_list_1 == filtered_type_list_2:
            return True
        else:
            return False

    def get_parent(self, _resource_uri):
        specific_class_uri_1 = "<" + self.get_most_specific_class(_resource_uri) + ">"
        try:
            response_uri_1 = self.shoot_custom_query(GET_SUPERCLASS % {'target_class': specific_class_uri_1})
        except:

            print(traceback.print_exception())
        try:
            results_1 = [x[u'type'][u'value'].encode('ascii', 'ignore') for x in
                         response_uri_1[u'results'][u'bindings']]
        except:

            print(traceback.print_exception())
        filtered_type_list_1 = [x for x in results_1 if
                                x[:28] in ['http://dbpedia.org/ontology/', 'http://dbpedia.org/property/']]
        if len(filtered_type_list_1) >= 1:
            return filtered_type_list_1[0]
        else:
            if filtered_type_list_1:
                return filtered_type_list_1
            else:
                return "http://www.w3.org/2002/07/owl#Thing"

    def is_Url(self, url):
        response = self.shoot_custom_query(CHECK_URL % {'target_resource': url})
        return response["boolean"]

    def get_properties(self, _uri, _right=True, _left=True, label=True):
        """
            This method brings all the predicates at a distance of 1-hop from the given URI.

            @TODO: Function breaks if both are false :/

        :param _uri: The URI of the actual entity
        :param _right:  Whether or not to fetch outgoing predicates
        :param _left:   Whether or not to fetch incoming predicates
        :param label:   Whether to return the label of the URI or just the URI

        :return: Diff lists depending on input booleans (1/2)
        """
        if _right:
            right_properties = list(set(self.get_properties_of_resource(_resource_uri=_uri)))
            if label:
                right_properties = [nlutils.get_label_via_parsing(rel) for rel in right_properties]
        if _left:
            left_properties = list(set(self.get_properties_of_resource(_resource_uri=_uri, _outgoing=False)))
            if label:
                left_properties = [nlutils.get_label_via_parsing(rel) for rel in left_properties]
        if _right and _left:
            return right_properties, left_properties
        elif _right:
            return right_properties
        else:
            return left_properties

    def get_entity(self, _resource_uri, _relation, outgoing=True):
        _resource_uri = "<" + _resource_uri + ">"
        _relation = "<" + _relation[0] + ">"
        if outgoing:
            ''' Query is to find the object'''
            temp_query = GET_OBJECT % {'target_resource': _resource_uri, 'property': _relation}
        else:
            '''Query is to find subject '''
            temp_query = GET_SUBJECT % {'target_resource': _resource_uri, 'property': _relation}
        response = self.shoot_custom_query(temp_query)
        try:
            entity_list = [x[u'entity'][u'value'] for x in response[u'results'][u'bindings']]
            return entity_list
        except:
            # TODO: Find and handle exceptions appropriately

            print(traceback.print_exc())

    def get_dbpedia_URL(self, _uri):
        '''
            Give a freebase/wikidata/etc. uri gives the dbpedia uri; if it exists or none if it does not
        '''
        if _uri[0] != '<':
            if _uri[-1] != '>':
                url = "<" + _uri + ">"
            else:
                url = '<' + _uri
        query = GET_SAME_AS % {'target_resource':url}
        response = self.shoot_custom_query(query)
        entity_list = [x[u'entity'][u'value'].encode('ascii', 'ignore') for x in response[u'results'][u'bindings']]
        if entity_list:
            return entity_list
        else:
            return None

    def get_hop2_subgraph(self,_resource_uri,_property_uri,right=False):
        if _resource_uri[0] != '<':
            _resource_uri = '<' + _resource_uri + '>'
        if _property_uri[0] != '<':
            _property_uri = '<' + _property_uri + '>'

        offset = 0
        if right:
            query = GET_LEFT_RIGHT_PROPERTIES_OF_RESOURCE_WITH_RIGHT_PROPERTY % {'target_resource':_resource_uri,
                                                                                 'property':_property_uri,
                                                                                 'offset' : offset}
        else:
            query = GET_LEFT_RIGHT_PROPERTIES_OF_RESOURCE_WITH_LEFT_PROPERTY % {'target_resource': _resource_uri,
                                                                                 'property': _property_uri,
                                                                                 'offset': offset}

        final_response = self.shoot_custom_query(query)

        if len(final_response[u'results'][u'bindings']) > 10000:
            offset_flag = True
            while offset_flag:
                offset = offset + 10000
                if right:
                    query = GET_LEFT_RIGHT_PROPERTIES_OF_RESOURCE_WITH_RIGHT_PROPERTY % {
                        'target_resource': _resource_uri,
                        'property': _property_uri,
                        'offset': offset}
                else:
                    query = GET_LEFT_RIGHT_PROPERTIES_OF_RESOURCE_WITH_LEFT_PROPERTY % {
                        'target_resource': _resource_uri,
                        'property': _property_uri,
                        'offset': offset}
                response = self.shoot_custom_query(query)
                final_response[u'results'][u'bindings'] = final_response[u'results'][u'bindings'] + response[u'results'][u'bindings']

                if len(response[u'results'][u'bindings']) < 10000:
                    offset_flag = False

        right_property_list = [x[u'property1'][u'value'].encode('ascii', 'ignore') for x in
                               final_response[u'results'][u'bindings'] if 'property1' in x.keys()]

        left_property_list = [x[u'property2'][u'value'].encode('ascii', 'ignore') for x in
                              final_response[u'results'][u'bindings'] if 'property2' in x.keys()]

        return right_property_list, left_property_list


if __name__ == '__main__':
    pass
    # print "\n\nBill Gates"
    dbp = DBPedia(_caching=True)
    # pprint(dbp.get_type_of_resource('http://dbpedia.org/resource/M._J._P._Rohilkhand_University', _filter_dbpedia = True))
    # print "\n\nIndia"
    # pprint(dbp.get_type_of_resource('http://dbpedia.org/resource/India', _filter_dbpedia = True))
    #
    # q = 'SELECT DISTINCT ?uri, ?a WHERE { ?uri <http://dbpedia.org/ontology/birthPlace> <http://dbpedia.org/resource/Mengo,_Uganda> . ?uri <http://dbpedia.org/ontology/birthPlace> ?a }'
    # pprint(dbp.get_answer(q))
    #
    #
    uri = 'http://dbpedia.org/resource/Donald_Trump'
    # print dbp.get_most_specific_class(uri)
    #
    # q = 'http://dbpedia.org/ontology/birthPlace'
    # pprint(dbp.get_label(q))
    # q = 'http://dbpedia.org/resource/Mumbai'

    print(dbp.get_parent(uri))
    pprint(dbp.get_properties(uri))
# r = 'http://dbpedia.org/resource/India'


