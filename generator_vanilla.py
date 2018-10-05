'''
    This file generates subgraphs and SPARQL for a given set of entites.

    Changelog:
        -> Removed probabilistic filtering (for easier deployment)
'''

# Importing some external libraries
from pprint import pprint
import networkx as nx
import numpy as np
import traceback
import warnings
import pickle
import random
import json
import copy
import uuid
import time


# Importing internal classes/libraries
from utils.exceptions import *
import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
import utils.subgraph as subgraph

random.seed(42)

# DBpedia interface object #To be instantiated when the code is run by main script/unit testing script
dbp = None

# Contains the whitelisted props types
predicates = open('resources/relations.txt', 'r').read().split('\n')

# Contains whitelisted entities classes
entity_classes = open('resources/entity_classes.txt', 'r').read().split('\n')

# Contains list of entites for which the question would be asked
entities = open('resources/entities.txt', 'r').read().split('\n')

# Contains all the SPARQL templates existing in templates.py
templates = json.load(open('templates.json'))

entity_went_bad = []
sparqls = {}  # Dict of the generated SPARQL Queries.

# Some macros because hardcoding kills puppies
DEBUG = True
NUM_ANSWER_COUNTABLE = 7
NUM_ANSWER_MAX = 10
FLUSH_THRESHOLD = 100


''' 
    A dictionary of properties. 
    **key** parent entity 
    **value** a dictionary {'predicate':count}
        **key** of property and **value** being number of times it has already occured .
    {"/agent" : [ {"/birthPlace" : 1 }, {"/deathPlace" : 2}] }

    This needs to be pickled. @TODO: When?
'''
try:
    predicates_count = pickle.load(open('resources/properties_count.pickle', 'rb'))
except:
    warnings.warn("Cannot find pickled properties count.")
    traceback.print_exc()
    predicates_count = {}


'''
    Some SPARQL Queries.
    Since this part of the code requires sending numerous convoluted queries to DBpedia,
        we best not clutter the DBpedia interface class and rather simply declare them here.

    Note: The names here can be confusing. Refer to the diagram (resources/nomenclature.png) 
        to know what each SPARQL query tries to do.
'''
one_triple_right = '''
            SELECT DISTINCT ?p ?e ?type
            WHERE {
                <%(e)s> ?p ?e .
                ?e <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
            }'''

one_triple_left = '''
            SELECT DISTINCT ?e ?p ?type
            WHERE {
                ?e ?p <%(e)s> .
                ?e <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
            }'''


def filter(_results,
           _keep_no_results=None,
           _filter_predicates=True,
           _filter_literals=True,
           _filter_entities=False,
           _filter_count=False,
           _k=5
           ):
    '''
    Implements pruing in the results.
    Used to push the results of different queries into the subgraph.

    Logic:
        It First prunes based on properties and entite classes.
        After this if the result length is still more than _keep_no_result,
            randomly selects _keep_no_results from the result list.
        The output can then be sent to be put in the graph.

    @TODO: implement _filter_entities filter

    :param _results: list: a result list which contains the sparql variables '?e', '?p', '?type'.
                They can be of either left or right queries as the defined above.
    :param _keep_no_results: int: a hard limit to the length of list. Leave if want unbounded.
    :param _filter_predicates: bool: if True, only properties existing in properties whitelist will be returned.
    :param _filter_literals: bool: if True, no literals will be returned.
    :param _filter_entities: bool: if True, only entities belonging to `entity_classes` will be returned.
    :param _filter_count: bool: if True, we ensure that only _k instances of a property alongwith entity type are returned
    :param _k: int: limit on _filter_count

    :return: A list of results which can directly be used for inserting into a graph
    '''
    global predicates_count

    results_list = []

    for result in _results[u'results'][u'bindings']:
        pred = result[u'p'][u'value']
        ent = result[u'e'][u'value']
        cls = dbp.get_most_specific_class(ent) if not nlutils.is_literal(ent) else None

        # Put in filters
        if _filter_predicates and not pred in predicates: continue
        if _filter_literals and nlutils.is_literal(ent): continue
        if _filter_entities and not cls in entity_classes: continue

        # Log this in property count
        predicate_count_obj = predicates_count.setdefault(cls, {})
        count = predicate_count_obj.setdefault(pred, 0)
        if _filter_count and count > _k:
            continue
        else:
            predicates_count[cls][count] += 1

        results_list.append(result)

    if _keep_no_results and (len(results_list) > _keep_no_results):
        return random.sample(results_list, _keep_no_results)

    return results_list


def insert_triple_in_subgraph(G,
                              _results,
                              _labels,
                              _direction,
                              _origin_node):
    """
        Function used to push the results of different queries into the subgraph.
        USAGE: only within the get_local_subgraph function.

    :param G: the subgraph object within which the triples are to be pushed
    :param _results: a result list which contains the sparql variables 'e' and 'p'.
                They can be of either left or right queries as the cell above.
    :param _labels: a tuple with three strings, which depict the nomenclature of the resources to be pushed
    :param _direction: True -> one triple right; False -> one triple left
    :param _origin_node: the results variable only gives us one p and one e.
                Depending on the direction, this node will act as the other e to complete the triple
    :return: Nothing
    """

    for result in _results:
        # Parse the results into local variables (for readibility)

        # A bit of cleaning here might help

        prop = result[u'p'][u'value']
        ent = result[u'e'][u'value']

        if not nlutils.is_clean_url(ent):
            continue

        if not nlutils.is_clean_url(prop):
            continue

        if _direction == True:
            # Right
            subgraph.insert(G=G, data=[(_labels[0], _origin_node), (_labels[1], prop), (_labels[2], ent)])

        elif _direction == False:
            # Left
            subgraph.insert(G=G, data=[(_labels[0], ent), (_labels[1], prop), (_labels[2], _origin_node)])


def generate_sparqls(_uri, dbp):
    try:
        uri = _uri

        # Generate the local subgraph
        graph = generate_subgraph(uri)

        # Generate SPARQLS based on subgraph
        fill_templates(graph, _uri=uri)

    except:
        traceback.print_exc()


def fill_specific_template(_template_id, _mapping):
    '''
        Function to fill a specific template.
        Given the template ID, it is expected to fetch the template from the set
            and juxtapose the mapping on the template.

        Moreover, it also has certain functionalities that help the future generation of verbalizings.
             -> Returns the answer of the query, and the answer type
             -> In some templates, it also fetches the intermediate hidden variable and it's types too.

        -> create copy of template from the list
        -> get the needed metadata
        -> push it in the list
        :param _template_id: int: ID of template (from templates.json)
        :param _mapping: dict: things to put on the template

        :return @TODO: fill this.
    '''

    global sparqls, templates

    # Create a copy of the template
    template = [x for x in templates if x['id'] == _template_id][0]
    template = copy.copy(template)

    # From the template, make a rigid query using mappings
    try:
        template['query'] = template['template'] % _mapping
        template['_id'] = uuid.uuid4().hex
        template['corrected'] = 'false'
    except KeyError:
        raise InvalidTemplateMappingError("Something doesn't fit right.")

    # Include the mapping within the template object
    template['mapping'] = _mapping

    # Get the Answer of the query
    answer = dbp.get_answer(template['query'])
    for key in answer.keys():
        """
            Based on answers, you make the following decisions:
                > If the query has 7 or more answers, we claim that this is a good count query. 
                    Less than that, and its a bad idea.
                    
                > If a variable has more than ten values matched to it, clamp it to 9   
        
            Note: expected keys here: x; uri
        """

        #For count templates
        if key == "uri":
            #can act as a count query
            template['countable'] = "true" if len(answer[key]) > NUM_ANSWER_COUNTABLE else "false"

        #Store the number of answers in the data too. Will help, act as a good filter and everything.
        template['answer_count'] = {key: len(list(set(answer[key])))}

        # Clamp the answes at NUM_ANSWERS_MAX
        answer[key] = answer[key][:max(len(answer[key]), NUM_ANSWER_MAX)]

    template['answer'] = answer
    
    """
        ATTENTION: This can create major problems in the future.
        We are assuming that the most specific type of one 'answer' would be the most specific type of all answers.
        In cases where answers are like Bareilly (City), Uttar Pradesh (State) and India (Country),
            the SPARQL and NLQuestion would not be the same.
            (We might expect all in the answers, but the question would put a domain restriction on answer.)

        [Fixed] @TODO: attend to this? No, lets let it be. For the sake of performance.
        @TODO: Why do we store only one answer in template['mapping']?
    """
    # Get the most specific type of the answers.
    template['answer_type'] = {variable: dbp.get_most_specific_class(variable[0]) for variable in template['answer']}
    template['mapping'] = {variable: variable[0] for variable  in template['answer']}

    # Also get the classes of all the things we're putting in our SPARQL
    template['mapping_type'] = {key: dbp.get_type_of_resource(key,_filter_dbpedia = True)
                    for key in template['mapping']}
    if DEBUG:
        print(template)

    # FINALLY, Put this SPARQL in
    sparqls[_template_id] = sparqls.setdefault(_template_id, []).append(template)

    # Just check if we have more than 100 SPARQLs for that template, flush them.
    if len(sparqls[_template_id]) > FLUSH_THRESHOLD:
        # @TODO: put a lock here, if making it parallel

        with open('sparqls/template%d.txt' % _template_id, 'a+') as f:
            for value in sparqls[_template_id]:
                fo.writelines(json.dumps(value) + "\n")

    return True


def fill_templates(_graph, _uri):
    '''
        This function is programmed to traverse through the Subgraph and create mappings for templates

        Per template traverse the graph, and pick out the needed stuff in local variables

        @TODO: make this fn generic. I.E. automatically make a nice dict to fill all templates
    '''

    global dbp

    access = subgraph.accessGraph(_graph)
 
    ''' 
        Template #1: 
            SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> } 
        Find e_out and e_to_e_out.
    '''

    print "Generating Template 1 now"
    
    #Query the graph for outnodes from e
    op = access.return_outnodes('e')
    counter_template1 = 0
    try:
        for triple in op[0]:
            
            #Making the variables explicit (for the sake of readability)
            e_out = triple[1].getUri()
            e_to_e_out = triple[2]['object'].getUri()
        
            #Create a mapping (in keeping with the templates' placeholder names)
            mapping = {'e_out': e_out, 'e_to_e_out': e_to_e_out }
            
            #Throw it to a function who will put it in the list with appropriate bookkeeping
            try:
                fill_specific_template(_template_id=1, _mapping=mapping)
                counter_template1 += 1
                if counter_template1 > 500:
                    pass
            except:
                print "check error stack"
                traceback.print_exc()
                continue
    except:
        print _uri, '1'
        entity_went_bad.append(_uri)
        # traceback.print_exc()
    
    ''' 
        Template #2: 
            SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri }
        Find e_in and e_in_to_e.
    '''
    
    print "Generating Template 2 now"

    #Query the graph for outnodes from e
    op = access.return_innodes('e')
    counter_template2 = 0

    try:    
        for triple in op[0]:
        
            #Making the variables explicit (for the sake of readability)
            e_in = triple[0].getUri()
            e_in_to_e = triple[2]['object'].getUri()
            
            #Create a mapping (in keeping with the templates' placeholder names)
            mapping = {'e_in':e_in, 'e_in_to_e': e_in_to_e}
            
            #Throw it to a function who will put it in the list with appropriate bookkeeping
            try:
                fill_specific_template( _template_id=2, _mapping=mapping)
                if counter_template2 > 500:
                    pass
            except:
                print "check error stack"
                traceback.print_exc()
                continue
    except:
        print _uri, '2'
        entity_went_bad.append(_uri)


    '''
        Template #3:
            SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri }
        Find e_in and e_in_to_e.
    '''

    print "Generating Template 3 now"

    # Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')
    #DEBUG print "length of innodes is " , str(len(op))
    counter_template3 = 0
    # Create a list of all these (e_in, e_in_to_e)
    try:
        one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}
        # pprint(one_triple_left)

        # Collect all e_in_in and e_in_in_to_e_in
        op = access.return_innodes('e_in')
        # print "length of innodes is ", str(len(op))

        # This 'op' has the e_in_in and the prop for all e_in's. We now need to map one to the other.
        for list_of_triples in op:

            # Some triple are simply empty. Ignore them.
            if len(list_of_triples) == 0:
                continue

            ### Mapping e_in_in's to relevant e_in's ###

            # Pick one triple from the list.
            e_in = list_of_triples[0][1].getUri()
            e_in_to_e = one_triple_left_map[e_in]
            # Find the relevant property from the map

            # Given this information, lets create mappings of template three
            for triple in list_of_triples:

                # Making the variables explicit (for the sake of readability)
                e_in_in = triple[0].getUri()
                e_in_in_to_e_in = triple[2]['object'].getUri()

                # Create a mapping (in keeping with the templates' placeholder names)
                mapping = {'e_in_in': e_in_in, 'e_in_in_to_e_in': e_in_in_to_e_in, 'e_in_to_e': e_in_to_e, 'e_in': e_in}
                mapping_type = {}
                
                # Throw it to a function who will put it in the list with appropriate bookkeeping
                try:
                    fill_specific_template(_template_id=3, _mapping=mapping)
                    counter_template3 = counter_template3 + 1
                    if counter_template3 > 500:
                        pass

                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue
    except:
        print _uri, '3'
        entity_went_bad.append(_uri)


    '''
        Template 5
        SELECT DISTINCT ?uri WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri }
    '''
    
    print "Generating Template 5 now"

    # Query the graph for outnodes from e and relevant properties
    op = access.return_innodes('e')
    counter_template5 = 0

    try:
        # Create a list of all these (e_in,e_in_to_e)
        one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}

        # Collect all e_out_in and e_in_to_e_in_out
        op = access.return_outnodes('e_in')

        # This 'op' has the e_out_in and the prop for all e_out's. We now need to map one to the other.
        for list_of_triples in op:

            # Some triple are simply empty. Ignore them.
            if len(list_of_triples) == 0:
                continue

            ### Mapping e_out_in's to relevant e_out's ###

            # Pick one triple from the list.
            e_in = list_of_triples[0][0].getUri()
            e_in_to_e = one_triple_left_map[e_in]  # Find the relevant property from the map

            # Given this information, lets create mappings of template four
            for triple in list_of_triples:

                #This ought not happen. :/ 
                if triple[1].getUri() == _uri:
                    continue

                # Making the variables explicit (for the sake of readability)
                e_in_out = triple[1].getUri()
                e_in_to_e_in_out = triple[2]['object'].getUri()

                # Create a mapping (in keeping with the templates' placeholder names)
                mapping = {'e_in_out': e_in_out, 'e_in_to_e_in_out': e_in_to_e_in_out, 'e_in_to_e': e_in_to_e,
                           'e_in': e_in}

                #Skipping duplicate e_in_to_e_in_out and e_in_to_e
                if e_in_to_e_in_out.split('/')[-1] == e_in_to_e.split('/')[-1]:
                    continue

                # Throw it to a function who will put it in the list with appropriate bookkeeping
                try:
                    fill_specific_template(_template_id=5, _mapping=mapping, _debug=False)
                    counter_template5 = counter_template5 + 1
                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue
                if counter_template5 > 10:
                    pass
    except:
        print _uri, '5'
        entity_went_bad.append(_uri)

    '''
        Template 6
        SELECT DISTINCT ?uri WHERE { ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x }
    '''

    print "Generating Template 6 now"

    # Query the graph for outnodes from e and relevant properties
    op = access.return_outnodes('e')
    counter_template6 = 0

    try:
        # Create a list of all these (e_in,e_in_to_e)
        one_triple_right_map = {triple[1].getUri(): triple[2]['object'].getUri() for triple in op[0]}

        # Collect all e_out_in and e_in_to_e_in_out
        op = access.return_outnodes('e_out')

        # This 'op' has the e_out_in and the prop for all e_out's. We now need to map one to the other.
        for list_of_triples in op:

            # Some triple are simply empty. Ignore them.
            if len(list_of_triples) == 0:
                continue

            ### Mapping e_out_in's to relevant e_out's ###

            # Pick one triple from the list.
            e_out = list_of_triples[0][0].getUri()
            e_to_e_out = one_triple_right_map[e_out]  # Find the relevant property from the map

            # Given this information, lets create mappings of template six
            for triple in list_of_triples:

                # Making the variables explicit (for the sake of readability)
                e_out_out = triple[1].getUri()
                e_out_to_e_out_out = triple[2]['object'].getUri()

                # Create a mapping (in keeping with the templates' placeholder names)
                mapping = {'e_out_out': e_out_out, 'e_out_to_e_out_out': e_out_to_e_out_out, 'e_to_e_out': e_to_e_out,
                           'e_out': e_out}

                #Keep the duplicates away
                if e_out_to_e_out_out.split('/')[-1] == e_to_e_out.split('/')[-1]:
                    continue

                # Throw it to a function who will put it in the list with appropriate bookkeeping
                try:
                    fill_specific_template(_template_id=6, _mapping=mapping, _debug=False)
                    counter_template6 = counter_template6 + 1
                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue
    except:
        print _uri, '6'
        entity_went_bad.append(_uri)
            

    '''
        Template 7
        SELECT DISTINCT ?uri WHERE { ?uri <%(e_to_e_out)s> <%(e_out_1)s> . ?uri <%(e_to_e_out)s> <%(e_out_2)s>}
    '''

    print "Generating Template 7 now"

    op = access.return_outnodes('e')
    counter_template7 = 0

    try:
        for triple_1 in op[0]:

            #Forming the first triple
            e_out_1 =  triple_1[1].getUri()
            e_to_e_out = triple_1[2]['object'].getUri()

            #Now to find another triple with the same e_to_e_out
            for triple_2 in op[0]:

                #Check condition
                if triple_2[2]['object'].getUri() ==  e_to_e_out and not triple_2[1].getUri() == e_out_1:

                    e_out_2 = triple_2[1].getUri()

                    #Creating a mapping
                    mapping = {'e_out_1': e_out_1, 'e_out_2':  e_out_2, 'e_to_e_out': e_to_e_out }

                    #Throw it in a functoin which will put it in the list with appropriate bookkeeping
                    try:
                        fill_specific_template(_template_id= 7, _mapping = mapping)
                        counter_template7 += 1

                        if counter_template7 > 500:
                            pass
                    except:
                        print "check error stack"
                        traceback.print_exc()
                        continue
    except:
        print _uri, '7'
        entity_went_bad.append(_uri)


    '''
        Template 8:
            SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out_1)s> <%(e_out_1)s> . ?uri <%(e_to_e_out_2)s> <%(e_out_2)s> } ",
    '''

    print "Generating Template 8 now"

    op = access.return_outnodes('e')
    counter_template8 = 0

    try:
        for triple_1 in op[0]:

            #Forming the first triple
            e_out_1 =  triple_1[1].getUri()
            e_to_e_out_1 = triple_1[2]['object'].getUri()

            #Now to find another triple with the same e_to_e_out
            for triple_2 in op[0]:

                #Check condition
                if not triple_2[2]['object'].getUri() ==  e_to_e_out_1:

                    #Forming the second triple
                    e_out_2 = triple_2[1].getUri()
                    e_to_e_out_2 = triple_2[2]['object'].getUri()

                    '''
                        @TODO: 
                        Issue:
                            say we encounter this triple:
                             ?uri a b
                             ?uri c d

                            Later we might encounter
                             ?uri c d
                             ?uri a b

                        Solution: have a set of (ab,cd) triples and select the unique ones only. 
                    '''
                    #Creating a mapping
                    mapping = {'e_out_1': e_out_1, 'e_out_2':  e_out_2, 'e_to_e_out_1': e_to_e_out_1, 'e_to_e_out_2': e_to_e_out_2 }

                    #Throw it in a functoin which will put it in the list with appropriate bookkeeping
                    try:
                        fill_specific_template(_template_id= 8, _mapping = mapping)
                        counter_template8 += 1

                        if counter_template8 > 500:
                            pass
                    except:
                        print "check error stack"
                        traceback.print_exc()
                        continue
    except:
        print _uri, '8'
        entity_went_bad.append(_uri)

    '''
        Template 9:
            SELECT DISTINCT ?uri WHERE { <%(e_in_in)s>  <%(e_in_in_to_e_in)s> ?x .  ?x <%(e_in_to_e)s> ?uri}
            but where e_in_in_to_e_in and e_in_to_e must be same.

            Reuse code of template 3 but with a check
    '''

    print "Generating Template 9 now"

    # Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')
    #DEBUG print "length of innodes is " , str(len(op))
    counter_template9 = 0

    try:
        # Create a list of all these (e_in, e_in_to_e)
        one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}
        # pprint(one_triple_left)

        # Collect all e_in_in and e_in_in_to_e_in
        op = access.return_innodes('e_in')
        # print "length of innodes is ", str(len(op))

        # This 'op' has the e_in_in and the prop for all e_in's. We now need to map one to the other.
        for list_of_triples in op:

            # Some triple are simply empty. Ignore them.
            if len(list_of_triples) == 0:
                continue

            ### Mapping e_in_in's to relevant e_in's ###

            # Pick one triple from the list.
            e_in = list_of_triples[0][1].getUri()
            e_in_to_e = one_triple_left_map[e_in]
            # Find the relevant property from the map

            # Given this information, lets create mappings of template three
            for triple in list_of_triples:

                # Making the variables explicit (for the sake of readability)
                e_in_in = triple[0].getUri()
                e_in_in_to_e_in = triple[2]['object'].getUri()

                #Check constraint
                if not e_in_in_to_e_in == e_in_to_e:
                    continue

                # Create a mapping (in keeping with the templates' placeholder names)
                mapping = {'e_in_in': e_in_in, 'e_in_in_to_e_in': e_in_in_to_e_in, 'e_in_to_e': e_in_to_e, 'e_in': e_in}
                mapping_type = {}
                
                # Throw it to a function who will put it in the list with appropriate bookkeeping
                try:
                    fill_specific_template(_template_id=9, _mapping=mapping)
                    counter_template9 = counter_template9 + 1
                    if counter_template9 > 500:
                        pass

                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue
    except:
        print _uri, '9'
        entity_went_bad.append(_uri)

    '''
        TEMPLATE 11: SELECT DISTINCT ?uri WHERE { ?x ?x <%(e_in_to_e)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri }
        Like template 5 but where the R1 and R2 are the same.

        Copying the code :]
    '''

    print "Generating Template 11 now"

    # Query the graph for outnodes from e and relevant properties
    op = access.return_innodes('e')
    counter_template11 = 0

    try:
        # Create a list of all these (e_in,e_in_to_e)
        one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}

        # Collect all e_out_in and e_in_to_e_in_out
        op = access.return_outnodes('e_in')

        # This 'op' has the e_out_in and the prop for all e_out's. We now need to map one to the other.
        for list_of_triples in op:

            # Some triple are simply empty. Ignore them.
            if len(list_of_triples) == 0:
                continue

            ### Mapping e_out_in's to relevant e_out's ###

            # Pick one triple from the list.
            e_in = list_of_triples[0][0].getUri()
            e_in_to_e = one_triple_left_map[e_in]  # Find the relevant property from the map

            # Given this information, lets create mappings of template four
            for triple in list_of_triples:

                #The core challenge is not have e_in_out be same as uri
                if triple[1].getUri() == _uri:
                    continue

                # Making the variables explicit (for the sake of readability)
                e_in_out = triple[1].getUri()
                e_in_to_e_in_out = triple[2]['object'].getUri()

                #Checking duplicate e_in_to_e_in_out and e_in_to_e (specific to template 11)
                if not e_in_to_e_in_out.split('/')[-1] == e_in_to_e.split('/')[-1]:
                    continue



                # Create a mapping (in keeping with the templates' placeholder names)
                mapping = {'e_in_out': e_in_out, 'e_in_to_e': e_in_to_e, 'e_in_to_e_in_out': e_in_to_e_in_out}


                # Throw it to a function who will put it in the list with appropriate bookkeeping
                try:
                    fill_specific_template(_template_id=11, _mapping=mapping, _debug=False)
                    counter_template11 = counter_template11 + 1
                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue
                if counter_template5 > 10:
                    pass

    except:
        print _uri, '11'
        entity_went_bad.append(_uri)

    '''
        Template 12
        SELECT DISTINCT ?uri WHERE { ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x }
    '''

    print "Generating Template 12 now"

    # Query the graph for outnodes from e and relevant properties
    op = access.return_outnodes('e')
    counter_template12 = 0

    try:
        # Create a list of all these (e_in,e_in_to_e)
        one_triple_right_map = {triple[1].getUri(): triple[2]['object'].getUri() for triple in op[0]}

        # Collect all e_out_in and e_in_to_e_in_out
        op = access.return_outnodes('e_out')

        # This 'op' has the e_out_in and the prop for all e_out's. We now need to map one to the other.
        for list_of_triples in op:

            # Some triple are simply empty. Ignore them.
            if len(list_of_triples) == 0:
                continue

            ### Mapping e_out_in's to relevant e_out's ###

            # Pick one triple from the list.
            e_out = list_of_triples[0][0].getUri()
            e_to_e_out = one_triple_right_map[e_out]  # Find the relevant property from the map

            # Given this information, lets create mappings of template six
            for triple in list_of_triples:

                #Ensure that e_out_out and uri are not the same
                if triple[1].getUri() == _uri:
                    continue

                # Making the variables explicit (for the sake of readability)
                e_out_out = triple[1].getUri()
                e_out_to_e_out_out = triple[2]['object'].getUri()

                # Create a mapping (in keeping with the templates' placeholder names)
                mapping = {'e_out_out': e_out_out, 'e_out_to_e_out_out': e_out_to_e_out_out, 'e_to_e_out': e_to_e_out,
                           'e_out': e_out}

                #Keep the duplicates away
                if not e_out_to_e_out_out.split('/')[-1] == e_to_e_out.split('/')[-1]:
                    continue

                # Throw it to a function who will put it in the list with appropriate bookkeeping
                try:
                    fill_specific_template(_template_id=12, _mapping=mapping, _debug=False)
                    counter_template12 = counter_template12 + 1
                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue
    except:
        print _uri, '12'
        entity_went_bad.append(_uri)

    '''
        Template 13: SELECT DISTINCT ?uri WHERE { ?uri <%(e_to_e_out_1)s> <%(e_out)s> . ?uri <%(e_to_e_out_2)s> <%(e_out)s> }
            Two level loops
            Let's not to a  right triple map

    '''    

    print "Generating Template 13 now"

    # Query the graph for innode to e and relevant properties
    op = access.return_outnodes('e')
    counter_template13 = 0

    # Create a list of all these (e_in, e_in_to_e)
    # one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}
    try:

        for triple_a in op[0]:

            #Collecting the first terminal
            e_out = triple_a[1].getUri()
            e_to_e_out_1 = triple_a[2]['object'].getUri()

            #Second Loop
            for triple_b in op[0]:

                #Check Conditions
                if triple_b[1].getUri() ==  e_out and not triple_b[2]['object'].getUri() == e_to_e_out_1:

                    #Getting stuff for the second triple
                    e_to_e_out_2 = triple_b[2]['object'].getUri()

                    #Create a mapping
                    mapping = { 'e_out': e_out, 'e_to_e_out_1':e_to_e_out_1, 'e_to_e_out_2':e_to_e_out_2, 'uri': _uri}

                    #Throw it in a functoin which will put it in the list with appropriate bookkeeping
                    try:
                        print "Filling Template 13"
                        fill_specific_template(_template_id=13, _mapping = mapping)
                        counter_template13 += 1
                    except:
                        print "check error stack"
                        traceback.print_exc()
                        continue
    
    except:
        print _uri, '13'
        entity_went_bad.append(_uri)

    '''
        TEMPLATE 14: SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e_1)s> ?uri. <%(e_in)s> <%(e_in_to_e_2)s> ?uri} 
        
            Take return in nodes
            Two level loop. 
            Let's not do a left triple map.

    '''            

    print "Generating Template 14 now"

    # Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')
    counter_template14 = 0

    try:

        # Create a list of all these (e_in, e_in_to_e)
        # one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}
        for triple_a in op[0]:

            #Collecting the first terminal
            e_in = triple_a[0].getUri()
            e_in_to_e_1 = triple_a[2]['object'].getUri()

            #Second Loop
            for triple_b in op[0]:

                #Check Conditions
                if triple_b[0].getUri() ==  e_in and not triple_b[2]['object'].getUri() == e_in_to_e_1:

                    #Getting stuff for the second triple
                    e_in_to_e_2 = triple_b[2]['object'].getUri()

                    #Create a mapping
                    mapping = { 'e_in': e_in, 'e_in_to_e_1':e_in_to_e_1, 'e_in_to_e_2':e_in_to_e_2, 'uri': _uri}

                    #Throw it in a functoin which will put it in the list with appropriate bookkeeping
                    try:
                        print "Filling Template 14"
                        fill_specific_template(_template_id=14, _mapping = mapping)
                        counter_template14 += 1

                        if counter_template14 > 500:
                            pass
                    except:
                        print "check error stack"
                        traceback.print_exc()
                        continue
    except:
        print _uri, '14'
        entity_went_bad.append(_uri)


    '''
        Template 15:
            SELECT DISTINCT ?uri WHERE { <%(e_in_1)s> <%(e_in_to_e)s> ?uri. <%(e_in_2)s> <%(e_in_to_e)s> ?uri} 
            
            Same as template 14, but different conditions
    '''

    print "Generating Template 15 now"

    # Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')
    counter_template15 = 0

    try:

        # Create a list of all these (e_in, e_in_to_e)
        # one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}

        for triple_a in op[0]:

            #Collecting the first terminal
            e_in_1 = triple_a[0].getUri()
            e_in_to_e = triple_a[2]['object'].getUri()

            #Second Loop
            for triple_b in op[0]:

                #Check Conditions
                if not triple_b[0].getUri() ==  e_in_1 and triple_b[2]['object'].getUri() == e_in_to_e:

                    #Getting stuff for the second triple
                    e_in_2 = triple_b[0].getUri()

                    #Create a mapping
                    mapping = { 'e_in_1': e_in_1, 'e_in_2':e_in_2, 'e_in_to_e':e_in_to_e, 'uri': _uri}

                    #Throw it in a functoin which will put it in the list with appropriate bookkeeping
                    try:
                        fill_specific_template(_template_id=15, _mapping = mapping)
                        counter_template15 += 1

                        if counter_template15 > 500:
                            break
                    except:
                        print "check error stack"
                        traceback.print_exc()
                        continue
    except:
        print _uri, '15'
        entity_went_bad.append(_uri)

    '''
        Template 16:
            SELECT DISTINCT ?uri WHERE { <%(e_in_1)s> <%(e_in_to_e_1)s> ?uri. <%(e_in_2)s> <%(e_in_to_e_2)s> ?uri} 
            
            Same as template 14, but different conditions
    '''

    print "Generating Template 16 now"

    # Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')
    counter_template16 = 0

    try:

        # Create a list of all these (e_in, e_in_to_e)
        # one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]}

        for triple_a in op[0]:

            #Collecting the first terminal
            e_in_1 = triple_a[0].getUri()
            e_in_to_e_1 = triple_a[2]['object'].getUri()

            #Second Loop
            for triple_b in op[0]:

                #Check Conditions
                if not triple_b[0].getUri() ==  e_in_1 and not triple_b[2]['object'].getUri() == e_in_to_e_1:

                    #Getting stuff for the second triple
                    e_in_2 = triple_b[0].getUri()
                    e_in_to_e_2 = triple_b[2]['object'].getUri()

                    #Create a mapping
                    mapping = { 'e_in_1': e_in_1, 'e_in_2':e_in_2, 'e_in_to_e_2':e_in_to_e_2, 'e_in_to_e_1':e_in_to_e_1, 'uri': _uri}

                    #Throw it in a functoin which will put it in the list with appropriate bookkeeping
                    try:
                        fill_specific_template(_template_id=16, _mapping = mapping)
                        counter_template16 += 1

                        if counter_template16 > 500:
                            break
                    except:
                        print "check error stack"
                        traceback.print_exc()
                        continue
    except:
        print _uri, '16'
        entity_went_bad.append(_uri)


def generate_subgraph(_uri, dbp):
    """
        Returns a JSON of the sort:

    :param _uri:
    :return:
    """

    # Create a new graph
    G = nx.DiGraph()
    access = subgraph.accessGraph(G)

    ########### e ?p ?e (e_to_e_out and e_out) ###########
    start = time.clock()
    results = dbp.shoot_custom_query(one_triple_right % {'e': _uri})
    # print "shooting custom query to get one triple right from the central entity e" , str(time.clock() - start)
    # print "total number of entities in right of the central entity is e ", str(len(results))
    labels = ('e', 'e_to_e_out', 'e_out')

    # Insert results in subgraph
    # print "inserting triples in right graph "
    start = time.clock()
    results = pruning(_results=results, _keep_no_results=10, _filter_properties=True, _filter_literals=True, _filter_entities=False)
    insert_triple_in_subgraph(G, _results=results,
                              _labels=labels, _direction=True,
                              _origin_node=_uri, _filter_properties=True)
    # print "inserting the right triple took " , str(time.clock() - start)
    ########### ?e ?p e (e_in and e_in_to_e) ###########
    # raw_input("check for right")
    results = dbp.shoot_custom_query(one_triple_left % {'e': _uri})
    labels = ('e_in', 'e_in_to_e', 'e')
    # print "total number of entity left of the central entity e is " , str(len(results))
    # Insert results in subgraph
    # print "inserting into left graph "
    start = time.clock()
    results = pruning(_results=results, _keep_no_results=100, _filter_properties=True, _filter_literals=True,
                      _filter_entities=False)
    insert_triple_in_subgraph(G, _results=results,
                              _labels=labels, _direction=False,
                              _origin_node=_uri, _filter_properties=True)
    # print "inserting triples for left of the central entity  took ", str(time.clock() - start)
    ########### e p eout . eout ?p ?e (e_out_to_e_out_out and e_out_out) ###########

    # Get all the eout nodes back from the subgraph.
    start = time.clock()
    e_outs = []
    op = access.return_outnodes('e')
    for x in op:
        for tup in x:
            e_outs.append(tup[1].getUri())

    labels = ('e_out', 'e_out_to_e_out_out', 'e_out_out')

    # print "insert into e_out_to_e_out_out", str(len(e_outs))
    # raw_input("check !!")
    for e_out in e_outs:
        start = time.clock()
        results = dbp.shoot_custom_query(one_triple_right % {'e': e_out})
        # Insert results in subgraph
        results = pruning(_results=results, _keep_no_results=100, _filter_properties=True, _filter_literals=True,
                          _filter_entities=False)
        insert_triple_in_subgraph(G, _results=results,
                                  _labels=labels, _direction=True,
                                  _origin_node=e_out, _filter_properties=True)

    ########### e p eout . ?e ?p eout  (e_out_in and e_out_in_to_e_out) ###########

    # Use the old e_outs variable
    labels = ('e_out_in', 'e_out_in_to_e_out', 'e_out')
    # print "insert into e_out_in_to_e_out_out", str(len(e_outs))
    for e_out in e_outs:
        results = dbp.shoot_custom_query(one_triple_left % {'e': e_out})

        # Insert results in subgraph
        results = pruning(_results=results, _keep_no_results=20, _filter_properties=True, _filter_literals=True,
                          _filter_entities=False)
        insert_triple_in_subgraph(G, _results=results,
                                  _labels=labels, _direction=False,
                                  _origin_node=e_out, _filter_properties=True)

    ########### ?e ?p ein . ein p e  (e_in_in and e_in_in_to_e_in) ###########

    # Get all the ein nodes back from subgraph
    e_ins = []
    op = access.return_innodes('e')
    for x in op:
        for tup in x:
            e_ins.append(tup[0].getUri())

    labels = ('e_in_in', 'e_in_in_to_e_in', 'e_in')

    for e_in in e_ins:
        results = dbp.shoot_custom_query(one_triple_left % {'e': e_in})

        # Insert results in subgraph
        results = pruning(_results=results, _keep_no_results=20, _filter_properties=True, _filter_literals=True,
                          _filter_entities=False)
        insert_triple_in_subgraph(G, _results=results,
                                  _labels=labels, _direction=False,
                                  _origin_node=e_in, _filter_properties=True)
    ########### ein ?p ?e . ein p e  (e_in_to_e_in_out and e_in_out) ###########

    # Use the old e_ins variable
    labels = ('e_in', 'e_in_to_e_in_out', 'e_in_out')
    for e_in in e_ins:
        results = dbp.shoot_custom_query(one_triple_right % {'e': e_in})

        # Insert results in subgraph
        results = pruning(_results=results, _keep_no_results=10, _filter_properties=True, _filter_literals=True,
                          _filter_entities=False)
        insert_triple_in_subgraph(G, _results=results,
                                  _labels=labels, _direction=True,
                                  _origin_node=e_in, _filter_properties=True)


    print "Done generating subgraph for entity ", _uri

    # Pushed all the six kind of nodes in the subgraph. Done!
    return G



'''
    Testing the ability to create subgraph given a URI
    Testing the ability to generate sparql templates
'''
sparqls = {}
dbp = db_interface.DBPedia(_verbose=True)


for entity in list_of_entities:
    try:
        generate_sparqls(entity, dbp)
    except:
        print traceback.print_exc()
        continue

# Commented it out to help the case of cluttered output folder        
# for key in sparqls:
#     with open('output/template%d.txt' % key, 'a+') as out:
#         pprint(sparqls[key], stream=out)

print "Pickling properties count to file"
pickle.dump(predicates_count, open('resources/properties_count.pickle', 'w+'))
print "DONE"

print "Trying to write to file!"
for key in sparqls:
    fo = open('sparqls/template%d.txt' % key, 'a+')
    for value in sparqls[key]:
        fo.writelines(json.dumps(value) + "\n")
    fo.close()

print "These entities did not generating something"
pprint(list(set(entity_went_bad)))