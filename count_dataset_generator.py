# Importing some external libraries
from pprint import pprint
import networkx as nx
import pickle
import json
import copy
import traceback
import random

# Importing internal classes/libraries
import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
import utils.subgraph as subgraph
import time

'''
    Initializing some stuff. Namely: DBpedia interface class.
    Reading the list of 'relevant' properties.
'''

dbp = None  # DBpedia interface object #To be instantiated when the code is run by main script/unit testing script
relevant_properties = open('resources/relation_whitelist.txt').read().split('\n')  # Contains the whitelisted props types
relevent_entity_classes = open('resources/entity_classes.txt').read().split('\n') #Contains whitelisted entities classes
list_of_entities = open('resources/single_entity.txt').read().split('\n')
'''contains list of entites for which the question would be asked '''

templates = json.load(open('templates.py'))  # Contains all the templates existing in templates.py
sparqls = {}  # Dict of the generated SPARQL Queries.
properties_count = {}
''' dictionary of properties. with key being the parent entity and value would be a dictionary with key peing name
    of property and value being number of times it has already occured .
    {"/agent" : [ {"/birthPlace" : 1 }, {"/deathPlace" : 2}] }
    '''
'''
    Some SPARQL Queries.
    Since this part of the code requires sending numerous convoluted queries to DBpedia,
        we best not clutter the DBpedia interface class and rather simply declare them here.

    Note: The names here can be confusing. Refer to the diagram above to know what each SPARQL query tries to do.
'''

one_triple_right = '''
            SELECT DISTINCT ?p ?e
            WHERE {
                <%(e)s> ?p ?e.

            }'''

one_triple_left = '''
            SELECT DISTINCT ?e ?p ?type
            WHERE {
                ?e ?p <%(e)s>.

            }'''

'''
    ?e <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type
    This cell houses the script which will build a subgraph as shown in picture above for each a given URI.
    @TODO: do something in cases where certain nodes of the local subgraph are not found.
            Will the code throw errors? How to you take care of them?
'''
def pruning(_results, _keep_no_results = 100, _filter_properties = True, _filter_literals = True, _filter_entities = True ):
    '''
Note- Updated the pruning rules.
    Function: Implements pruing in the results . used to push the results of different queries into the subgraph.
        >First prunes based on properties and entite classes. After this if the result length is still more than
        _keep_no_result , randomly selects _keep_no_results from the result list. The output can then be sent for insertion in the graph

    :return: A list of results which can directly be used for inserting into a graph
    _results: a result list which contains the sparql variables 'e' and 'p'.
                They can be of either left or right queries as the cell above
        _labels: a tuple with three strings, which depict the nomenclature of the resources to be pushed
        _direction: True -> one triple right; False -> one triple left
        _origin_node: the results variable only gives us one p and one e.
                Depending on the direction, this node will act as the other e to complete the triple
        _filter_properties: if True, only properties existing in properties whitelist will be pushed in.
        _filter_entities: if True, only entites belonging to a particular classes present in the whitelist will be pushed in.

    '''
    print "@pruning"
    temp_results = []
    # properties_count = {}
    results_list = []
    for result in _results[u'results'][u'bindings']:
        prop = result[u'p'][u'value']
        if _filter_properties:
            if not prop.split('/')[-1] in relevant_properties:
                continue
        results_list.append(result)
    if len(results_list) > 500:
        results_list = random.sample(results_list,500)
    print len(results_list)
    for result in results_list:
        # Parse the results into local variables (for readibility)
        prop = result[u'p'][u'value']
        ent = result[u'e'][u'value']
        # ent_type = result[u'type'][u'value']
        # print ent_type
        if _filter_literals:
            if nlutils.has_literal(ent):
                continue

        if _filter_properties:
            # Filter results based on important properties


            if not prop.split('/')[-1] in relevant_properties:
                continue

        if _filter_entities:
            # filter entities based on class
            if not [i for i in dbp.get_type_of_resource(ent) if i in relevent_entity_classes]:
                continue
        # Finally, insert, in a temporary list for random pruning
        temp_results.append(result)

    # if (len(temp_results) > _keep_no_results):
    #     return random.sample(temp_results,_keep_no_results)
    # print len(temp_results)
    return temp_results

def insert_triple_in_subgraph(G, _results, _labels, _direction, _origin_node, _filter_properties=True,
                              _filter_literals=True,_filter_entities = False):
    '''
        Function used to push the results of different queries into the subgraph.
        USAGE: only within the get_local_subgraph function.

        INPUTS:
        _subgraph: the subgraph object within which the triples are to be pushed
        _results: a result list which contains the sparql variables 'e' and 'p'.
                They can be of either left or right queries as the cell above
        _labels: a tuple with three strings, which depict the nomenclature of the resources to be pushed
        _direction: True -> one triple right; False -> one triple left
        _origin_node: the results variable only gives us one p and one e.
                Depending on the direction, this node will act as the other e to complete the triple
        _filter_properties: if True, only properties existing in properties whitelist will be pushed in.
        _filter_entities: if True, only entites belonging to a particular classes present in the whitelist will be pushed in.
    '''

    for result in _results:
        # Parse the results into local variables (for readibility)

        prop = result[u'p'][u'value']
        ent = result[u'e'][u'value']

        if _direction == True:
            # Right
            subgraph.insert(G=G, data=[(_labels[0], _origin_node), (_labels[1], prop), (_labels[2], ent)])

        elif _direction == False:
            # Left
            subgraph.insert(G=G, data=[(_labels[0], ent), (_labels[1], prop), (_labels[2], _origin_node)])


def get_local_subgraph(_uri):
    # Collecting required variables: DBpedia interface, and a new subgraph
    ''' This subgraph is different from the one in the cumulative dataset . As it only concerns with
    the 1st level entites. The subgraph has been restricted because of the explosion in the size
    of the sub graph'''
    global dbp

    # Create a new graph
    G = nx.DiGraph()
    access = subgraph.accessGraph(G)

    ########### e ?p ?e (e_to_e_out and e_out) ###########
    start = time.clock()
    results = dbp.shoot_custom_query(one_triple_right % {'e': _uri})
    print "shooting custom query to get one triple right from the central entity e" , str(time.clock() - start)
    print "total number of entities in right of the central entity is e ", str(len(results))
    labels = ('e', 'e_to_e_out', 'e_out')

    # Insert results in subgraph
    print "inserting triples in right graph "
    start = time.clock()
    results = pruning(_results=results, _keep_no_results=10, _filter_properties=True, _filter_literals=True, _filter_entities=False)
    insert_triple_in_subgraph(G, _results=results,
                              _labels=labels, _direction=True,
                              _origin_node=_uri, _filter_properties=True)
    print "inserting the right triple took " , str(time.clock() - start)
    ########### ?e ?p e (e_in and e_in_to_e) ###########
    # raw_input("check for right")
    results = dbp.shoot_custom_query(one_triple_left % {'e': _uri})
    labels = ('e_in', 'e_in_to_e', 'e')
    print "total number of entity left of the central entity e is " , str(len(results))
    # Insert results in subgraph
    print "inserting into left graph "
    start = time.clock()
    results = pruning(_results=results, _keep_no_results=100, _filter_properties=True, _filter_literals=True,
                      _filter_entities=True)
    insert_triple_in_subgraph(G, _results=results,
                              _labels=labels, _direction=False,
                              _origin_node=_uri, _filter_properties=True)
    print "inserting triples for left of the central entity  took ", str(time.clock() - start)
    ########### e p eout . eout ?p ?e (e_out_to_e_out_out and e_out_out) ###########

    # Get all the eout nodes back from the subgraph.
    return G


def fill_specific_template(_template_id, _mapping,_debug=False):
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
    '''

    global sparql, templates, outputfile

    # Create a copy of the template
    template = [x for x in templates if x['id'] == _template_id][0]
    template = copy.copy(template)

    # From the template, make a rigid query using mappings
    try:
        template['query'] = template['template'] % _mapping
    except KeyError:
        print "fill_specific_template: ERROR. Mapping does not match."
        return False

    # Include the mapping within the template object
    template['mapping'] = _mapping

    # Get the Answer of the query
    # get_answer now returns a dictionary with appropriate variable bindings.
    template['answer'] = dbp.get_answer(template['query'])

    # Get the most specific type of the answers.
    '''
        ATTENTION: This can create major problems in the future.
        We are assuming that the most specific type of one 'answer' would be the most specific type of all answers.
        In cases where answers are like Bareilly (City), Uttar Pradesh (State) and India (Country),
            the SPARQL and NLQuestion would not be the same.
            (We might expect all in the answers, but the question would put a domain restriction on answer.)

        @TODO: attend to this!
    '''
    template['answer_type'] = {}
    for variable in template['answer']:
        template['answer_type'][variable] = dbp.get_most_specific_class(template['answer'][variable][0])
        template['mapping'][variable] = template['answer'][variable][0]

    mapping_type = {}
    for key in template['mapping']:
        mapping_type[key] = dbp.get_type_of_resource(template['mapping'][key],_filter_dbpedia = True)

    template['mapping_type'] = mapping_type
    if _debug:
        pprint(template)
    # Push it onto the SPARQL List
    # perodic write in file.
    # @TODO: instead of file use a database.
    try:
        sparqls[_template_id].append(template)
        print len(sparqls[_template_id])
        if len(sparqls[_template_id]) > 100000:
            print "in if condition"
            print "tempalte id is ", str(_template_id)
            with open('output/template%s.txt' % str(_template_id), "a+") as out:
                pprint(sparqls[_template_id], stream=out)
            with open('output/template%s.json' % str(_template_id), "a+") as out:
                json.dump(sparqls[_template_id], out)
            sparqls[_template_id] = []
    except:
        print traceback.print_exc()
        sparqls[_template_id] = [template]

    return True


def fill_templates(_graph, _uri):
    '''
        This function is programmed to traverse through the Subgraph and create mappings for templates

        Per template traverse the graph, and pick out the needed stuff in local variables
    '''

    global dbp

    access = subgraph.accessGraph(_graph)


    '''
        Template #20:
            SELECT DISTINCT count(?uri) WHERE { <%(e_in)s> <%(e_in_to_e)s> <%(e)s> . <%(e)s> <%(e_to_e_out)s> ?uri }
    '''

    # Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')         #e_in
    counter_template3 = 0
    # Create a list of all these (e_in, e_in_to_e)
    one_triple_left_map = {triple[0].getUri(): triple[2]['object'].getUri() for triple in op[0]} #dictionary of e_in , e_in_to_e

    # Collect all e_out
    op = access.return_outnodes('e')

    #A dictionary {property1 : [list of e_out], property2:[list of all e_out]}

    property_e_out = {}
    # pprint(op[0])
    for triple in op[0]:
        # print triple
        try:
            property_e_out[triple[2]['object'].getUri()].append(triple[1].getUri())
        except:
            # print traceback.print_exc()
            property_e_out[triple[2]['object'].getUri()] = []
            property_e_out[triple[2]['object'].getUri()].append(triple[1].getUri())
    counter_template1 = 0

    # This 'op' has the e_in_in and the prop for all e_in's. We now need to map one to the other.
    pprint(property_e_out)
    counter_template20 = 0
    for entity in one_triple_left_map:
        for property in property_e_out:
            '''SELECT DISTINCT count(?uri) WHERE { <%(e_in)s> <%(e_in_to_e)s> <%(e)s> . <%(e)s> <%(e_to_e_out)s> ?uri }'''
            # print len(property_e_out[property])
            # print property
            if len(property_e_out[property]) > 3:
                mapping = {'e_in':entity,'e_in_to_e':one_triple_left_map[entity],'e':_uri,'e_to_e_out':property}
                try:
                    fill_specific_template(_template_id=20, _mapping=mapping)
                    counter_template20 = counter_template20 + 1
                    print str(counter_template20), "tempalte20"
                    if counter_template20 > 500:
                        break
                        #                     break
                except:
                    print "check error stack"
                    traceback.print_exc()
                    continue

'''
    Testing the ability to create subgraph given a URI
    Testing the ability to generate sparql templates
'''
sparqls = {}
dbp = db_interface.DBPedia(_verbose=True)
def generate_answer(_uri, dbp):
    print _uri
    try:
        uri = _uri

        # Generate the local subgraph
        graph = get_local_subgraph(uri)
        print "the graph is completed"
        # Generate SPARQLS based on subgraph
        fill_templates(graph, _uri=uri)
        print "done with one entity"
    except:
        print traceback.print_exception()

for entity in list_of_entities:
    try:
        generate_answer(entity,dbp)
    except:
        print traceback.print_exc()
        continue
for key in sparqls:
    with open('output/template%d.txt' % key, 'a+') as out:
        pprint(sparqls[key], stream=out)
for key in sparqls:
    f = open('output/template%s.json' % key, 'a+')
    json.dump(sparqls[key], f)
    f.close()
for key in sparqls:
    fo = open('output/json_template%d.txt' % key, 'a+')
    for value in sparqls[key]:
        fo.writelines(json.dumps(value) + "\n")
    fo.close()


print "DONE"