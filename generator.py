"""
    This file generates subgraphs and SPARQL for a given set of entites.

    Changelog:
        -> Removed probabilistic filtering (for easier deployment)

        @TODO: Figure out why _fill_one_template_ fucks up answer and answer type, num
"""

# Importing some external libraries
from pprint import pprint
from oset import oset
from tqdm import tqdm
import textwrap
import warnings
import pickle
import random
import json
import copy
import uuid

# Importing internal classes/libraries
from utils.goodies import *
import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
from utils import subgraph

formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
    formatwarning_orig(textwrap.fill(str(message)), category, filename, lineno, line="")

random.seed(42)

# LOCATION
DONE_SPARQLS_LOC = "sparqls/template%d.txt"
DONE_ENTITIES_DONE_LOC = './sparqls/entities.txt'
RES_RELATION_LOC = 'resources/relations.txt'
RES_ENTITIY_CLASSES_LOC = 'resources/entity_classes.txt'
RES_ENTITIES_LOC = 'resources/entities.txt'
RES_TEMPLATES_LOC = 'templates.json'
RES_PREDICATE_COUNT_LOC = 'resources/properties_count.pickle'

# Contains the whitelisted props types
predicates = open(RES_RELATION_LOC, 'r').read().split('\n')

# Contains whitelisted entities classes
entity_classes = open(RES_ENTITIY_CLASSES_LOC, 'r').read().split('\n')

# Contains list of entities for which the question would be asked
entities = oset(open(RES_ENTITIES_LOC, 'r').read().split('\n'))
entities_done = oset(open(DONE_ENTITIES_DONE_LOC, 'r+').read().split('\n'))
entities = list(entities - entities_done)

# Contains all the SPARQL templates existing in templates.py
templates = json.load(open(RES_TEMPLATES_LOC))

# Some global vars to be filled in later.
entity_went_bad = []
sparqls = {}
dbp = None

# Some macros because hardcoding params kills puppies
DEBUG = True
NUM_ANSWER_COUNTABLE = 7
NUM_ANSWER_MAX = 10
FLUSH_THRESHOLD = 100
FILTER_PRED, FILTER_LITERAL, FILTER_ENT = True, True, False
DBP_NMSP = 'http://dbpedia.org/'  # DBpedia namespace
SUBG_MAX_RESULTS = 50

'''
    A dictionary of properties. 
    **key** parent entity 
    **value** a dictionary {'predicate':count}
        **key** of property and **value** being number of times it has already occurred .
    {"/agent" : [ {"/birthPlace" : 1 }, {"/deathPlace" : 2}] }

    This needs to be pickled. @TODO: When?
'''
try:
    predicates_count = pickle.load(open(RES_PREDICATE_COUNT_LOC, 'rb'))
except FileNotFoundError:
    warnings.warn("Cannot find pickled properties count at %s." % RES_PREDICATE_COUNT_LOC)
    # traceback.print_exc()
    predicates_count = {}


'''
    Some SPARQL Queries.
    Since this part of the code requires sending numerous convoluted queries to DB
pedia,
        we best not clutter the DBpedia interface class and rather simply declare them here.

    Note: The names here can be confusing. Refer to the diagram (resources/nomenclature.png) 
        to know what each SPARQL query tries to do.
'''
one_triple_right = '''
            SELECT DISTINCT ?p ?e
            WHERE {
                <%(e)s> ?p ?e .
            }'''

one_triple_left = '''
            SELECT DISTINCT ?e ?p
            WHERE {
                ?e ?p <%(e)s> .
            }'''


def filter_triples(_results,
                   _keep_no_results=None,
                   _filter_dbpedia=False,
                   _filter_predicates=True,
                   _filter_literals=True,
                   _filter_entities=False,
                   _filter_count=False,
                   _k=5
                   ):
    """
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
    :param _filter_dbpedia: bool: if True, only things starting with http://dbpedia.org/... will be returned.
    :param _filter_predicates: bool: if True, only properties existing in properties whitelist will be returned.
    :param _filter_literals: bool: if True, no literals will be returned.
    :param _filter_entities: bool: if True, only entities belonging to `entity_classes` will be returned.
    :param _filter_count: bool: if True we ensure that only _k instances of a property alongwith entitytype are returned
    :param _k: int: limit on _filter_count

    :return: A list of results which can directly be used for inserting into a graph
    """
    global predicates_count

    results_list = []

    for result in _results[u'results'][u'bindings']:
        pred = result[u'p'][u'value']
        ent = result[u'e'][u'value']

        # Put in filters
        if _filter_dbpedia and (not pred.startswith(DBP_NMSP) or not ent.startswith(DBP_NMSP)):
            continue
        if _filter_predicates and pred not in predicates:
            continue
        if _filter_literals and nlutils.is_literal(ent):
            continue

        cls = dbp.get_most_specific_class(ent) if not nlutils.is_literal(ent) else None

        # Log this in property count
        count = predicates_count.setdefault(cls, {}).setdefault(pred, 0)
        if _filter_count and count > _k:
            continue
        else:
            predicates_count[cls][pred] += 1

        results_list.append(result)

    if _keep_no_results and (len(results_list) > _keep_no_results):
        return random.sample(results_list, _keep_no_results)

    return results_list


def insert_triples_in_subgraph(subg, _results, _outgoing, _origin, _save_classes=False):
    """
        Function used to push the results of different queries into the subgraph.
        USAGE: only within the get_local_subgraph function.

    :param subg: the subgraph object within which the triples are to be pushed
    :param _results: a result list which contains the sparql variables 'e' and 'p'.
                They can be of either left or right queries as the cell above.
    :param _outgoing: True -> one triple right; False -> one triple left
    :param _origin: the results variable only gives us one p and one e.
                Depending on the direction, this node will act as the other e to complete the triple
    :param _save_classes: boolL True -> also store the rdftype value of the entites
    :return: Nothing
    """

    for result in _results:
        # Parse the results into local variables (for readibility)

        # A bit of cleaning here might help

        pred = result[u'p'][u'value']
        enty = result[u'e'][u'value']
        cls = dbp.get_most_specific_class(enty) if _save_classes else ''

        if not nlutils.is_clean_url(enty):
            continue

        if not nlutils.is_clean_url(pred):
            continue

        # Push the data in subgraph
        subg.insert([subgraph.PredEntTuple(pred, enty, cls)], _origin=_origin, _outgoing=_outgoing)


def _generate_sparqls_(_uri, _dbp):
    """
        Internal fn which orchestrates everything. Calls fn to gen subgraph,
            and then generates SPARQL based on the subgraph

    :param _uri: str of entity
    :param _dbp: dbpedia interface obj
    :return:
    """
    print(f"{_uri}: Started.")
    with Timer() as timed:
        # Generate the local subgraph
        graph = generate_subgraph(_uri, _dbp=_dbp)
    print("%(ent)s: Done generating subgraph. Time: %(time).03f." % {'ent': _uri, 'time': timed.interval})

    with Timer() as timed:
        # Generate the local subgraph
        fill_templates(graph, _dbp=_dbp)
    print("%(ent)s: Done generating sparqls. Time: %(time).03f." % {'ent': _uri, 'time': timed.interval})
    print("%(ent)s: Time spent inside subG: %(time).03f." % {'ent': _uri, 'time': graph.time_maps})


def _fill_one_template_(_template, _map, _graph, _dbp):
    """
        Function to fill a given template.
            by juxtaposing the mapping on the template.

        Moreover, it also has certain functionalities that help the down the line.
             -> Returns the answer of the query, and the answer type
             -> In some templates, it also fetches the intermediate hidden variable and it's types too.

        Reject:
            -> if count template and less answers, reject.
            -> if not rdf constraints based template, and some answers have no common class with _graph.uri, reject.

        -> create copy of template from the list
        -> get the needed metadata
        -> push it in the list
        :param _template: dict: one of the template from `templates.json`
        :param _map: dict: of vars needed in template. (maybe more)
        :param _graph: Subgraph obj
        :param _dbp: dbpedia obj

        :return _template: dict.
    """

    # Create a copy of the template
    template = copy.copy(_template)

    # From the template, make a rigid query using mappings
    try:
        template['query'] = template['template'] % _map
        template['_id'] = uuid.uuid4().hex
        template['corrected'] = 'false'
        template['entity'] = _graph.uri
    except KeyError:
        raise InvalidTemplateMappingError("Something doesn't fit right. Var Map %s" % str(_map))

    # Include the mapping within the template object
    template['mapping'] = _map

    # @TODO: try finding it in the subgraph, and getting the class from there.
    # Also get the classes of all the things we're putting in our SPARQL
    template['mapping_type'] = {key: dbp.get_most_specific_class(value)
                                for key, value in _map.items()}

    # Get the Answer of the query
    answer = dbp.get_answer(template['query'])
    classes_uri = dbp.get_type_of_resource(template['entity'], _filter_dbpedia=True)
    template['answer_type'] = classes_uri

    # Check for reject condition 1
    if template["type"] == "count":
        if (int(answer[list(answer.keys())[0]][0])) < NUM_ANSWER_COUNTABLE:
            return None

    if 'uri' in answer.keys():
        classes_answer = [dbp.get_type_of_resource(uri, _filter_dbpedia=True) for uri in answer['uri']
                          if not nlutils.is_literal(uri)]

        # Check for reject condition 2
        if 300 >= template['template_id']:
            # If not a template with rdf type constraint
            for cls in classes_answer:
                if not classes_uri & set(cls):
                    # No common class
                    return None

    # Store answers accordingly
    if template['type'] == 'ask':
        template['answer_num'] = -1
    else:
        # Clamp the answers at NUM_ANSWERS_MAX and put in template IF NOT BOOLEAN
        answer = {k: v[:max(len(list(set(v))), NUM_ANSWER_MAX)] for k, v in answer.items()}
        if template['type'] == 'count':
            template['answer_num'] = -1
        else:
            template['answer_num'] = len(list(set(answer['uri'])))

    template['answer'] = answer

    return template


def get_vars(_template):
    _vars = _template.get('vars', nlutils.get_variables(_template['template']))
    _vars += ['class_uri'] if 'class_uri' not in _vars else []
    return _vars


def add(_data):
    """
        Safely store generated template obj (full with SPARQL and whatnot) in a global var.

    :param _data: dict
    :return: None
    """
    global sparqls
    if _data:
        sparqls[_data['template_id']] = sparqls.get(_data['template_id'], []) + [_data]
    return True


def flush(_uri):
    """
        @TODO: Need a lock here

        :param _uri: str of the entity in question
        :return: Nothing
    """
    global sparqls

    print(f"\tFlushing sparqls for {_uri}")
    for t_id, data in sparqls.items():

        with open(DONE_SPARQLS_LOC % t_id, "a+") as fo:
            for value in data:
                fo.writelines(json.dumps(value) + "\n")

    sparqls = {}

    # Also put the entity in the list
    with open(DONE_ENTITIES_DONE_LOC, "a+") as fo:
        fo.writelines(_uri+'\n')


def fill_templates(_graph, _dbp):
    """
        Will generate valid SPARQLs for different templates, based on the keys that the SPARQL needs.
        Expects a populated Subgraph object.

        :param _graph: Subgraph obj
        :param _dbp: dbpedia interface obj
        :return List of strings (SPARQL)
    """
    for template in templates:
        mappings = _graph.gen_maps(get_vars(template), template.get('equal', []))[:template.get('max', None)]

        for mapping in tqdm(mappings):
            add(_data=_fill_one_template_(_template=template, _map=mapping, _graph=_graph, _dbp=_dbp))

    # Write everything to disk
    flush(_graph.uri)


def generate_subgraph(_uri, _dbp):
    """
        Returns a subgraph object.

    :param _uri: str of entity
    :param _dbp: dbpedia object
    :return:
    """

    # Create a new graph
    g = subgraph.Subgraph(_uri, _type=_dbp.get_most_specific_class(_uri))

    # ########## e ?p ?e (e_to_e_out and e_out) ##########
    with Timer() as timer:

        results = _dbp.shoot_custom_query(one_triple_right % {'e': _uri})
        results = filter_triples(_results=results,
                                 _keep_no_results=SUBG_MAX_RESULTS,
                                 _filter_dbpedia=True,
                                 _filter_predicates=FILTER_PRED,
                                 _filter_literals=FILTER_LITERAL,
                                 _filter_entities=FILTER_ENT,
                                 _filter_count=False)
        insert_triples_in_subgraph(g, _results=results, _outgoing=True, _origin=_uri, _save_classes=True)

    if DEBUG:
        print("GenSub: 1-hop right for %(uri)s. Time: %(time).03f. Len: %(len)d" %
              {'uri': _uri, 'time': timer.interval, 'len': len(results)})

    # ########## ?e ?p e (e_in and e_in_to_e) ##########
    with Timer() as timer:

        results = _dbp.shoot_custom_query(one_triple_left % {'e': _uri})
        results = filter_triples(_results=results,
                                 _keep_no_results=SUBG_MAX_RESULTS,
                                 _filter_dbpedia=True,
                                 _filter_predicates=FILTER_PRED,
                                 _filter_literals=FILTER_LITERAL,
                                 _filter_entities=FILTER_ENT,
                                 _filter_count=False)
        insert_triples_in_subgraph(g, _results=results, _outgoing=False, _origin=_uri, _save_classes=True)

    if DEBUG:
        print("GenSub: 1-hop left for %(uri)s. Time: %(time).03f. Len: %(len)d" %
              {'uri': _uri, 'time': timer.interval, 'len': len(results)})

    # ########## e p eout . eout ?p ?e (e_out_to_e_out_out and e_out_out) ##########
    with Timer() as timer:

        # Get all the e_out nodes back from the subgraph.
        e_outs = g.right.entities
        len_res = 0
        for e_out in e_outs:
            results = _dbp.shoot_custom_query(one_triple_right % {'e': e_out})
            results = filter_triples(_results=results,
                                     _keep_no_results=SUBG_MAX_RESULTS,
                                     _filter_dbpedia=True,
                                     _filter_predicates=FILTER_PRED,
                                     _filter_literals=FILTER_LITERAL,
                                     _filter_entities=FILTER_ENT,
                                     _filter_count=False)
            len_res = len(results)
            insert_triples_in_subgraph(g, _results=results, _outgoing=True, _origin=e_out, _save_classes=True)

    if DEBUG:
        print("GenSub: 2-hop right (e_out_to_e_out_out and e_out_out) for %(uri)s. Time: %(time).03f. Len: %(len)d" %
              {'uri': _uri, 'time': timer.interval, 'len': len_res})

    # ########## e p eout . ?e ?p eout  (e_out_in and e_out_in_to_e_out) ##########
    with Timer() as timer:

        e_outs = g.right.entities
        len_res = 0
        for e_out in e_outs:
            results = _dbp.shoot_custom_query(one_triple_left % {'e': e_out})
            results = filter_triples(_results=results,
                                     _keep_no_results=SUBG_MAX_RESULTS,
                                     _filter_dbpedia=True,
                                     _filter_predicates=FILTER_PRED,
                                     _filter_literals=FILTER_LITERAL,
                                     _filter_entities=FILTER_ENT,
                                     _filter_count=False)
            len_res += len(results)
            # print("Here ",len(results), e_out)
            insert_triples_in_subgraph(g, _results=results, _outgoing=False, _origin=e_out, _save_classes=True)

    if DEBUG:
        print("GenSub: 2-hop left (e_out_in and e_out_in_to_e_out) for %(uri)s. Time: %(time).03f. Len: %(len)d" %
              {'uri': _uri, 'time': timer.interval, 'len': len_res})

    # ########## ?e ?p ein . ein p e  (e_in_in and e_in_in_to_e_in) ##########
    with Timer() as timer:

        e_ins = g.left.entities
        len_res = 0
        for e_in in e_ins:
            results = _dbp.shoot_custom_query(one_triple_left % {'e': e_in})
            results = filter_triples(_results=results,
                                     _keep_no_results=SUBG_MAX_RESULTS,
                                     _filter_dbpedia=True,
                                     _filter_predicates=FILTER_PRED,
                                     _filter_literals=FILTER_LITERAL,
                                     _filter_entities=FILTER_ENT,
                                     _filter_count=False)
            len_res += len(results)
            insert_triples_in_subgraph(g, _results=results, _outgoing=False, _origin=e_in, _save_classes=True)

    if DEBUG:
        print("GenSub: 2-hop left (e_in_in and e_in_in_to_e_in) for %(uri)s. Time: %(time).03f. Len: %(len)d" %
              {'uri': _uri, 'time': timer.interval, 'len': len_res})

    # ########## ein ?p ?e . ein p e  (e_in_to_e_in_out and e_in_out) ##########
    with Timer() as timer:

        e_ins = g.left.entities
        len_res = 0
        for e_in in e_ins:
            results = _dbp.shoot_custom_query(one_triple_right % {'e': e_in})
            results = filter_triples(_results=results,
                                     _keep_no_results=SUBG_MAX_RESULTS,
                                     _filter_dbpedia=True,
                                     _filter_predicates=FILTER_PRED,
                                     _filter_literals=FILTER_LITERAL,
                                     _filter_entities=FILTER_ENT,
                                     _filter_count=False)
            len_res = len(results)
            insert_triples_in_subgraph(g, _results=results, _outgoing=True, _origin=e_in, _save_classes=True)

    if DEBUG:
        print("GenSub: 2-hop right (e_in_to_e_in_out and e_in_out) for %(uri)s. Time: %(time).03f. Len: %(len)d" %
              {'uri': _uri, 'time': timer.interval, 'len': len_res})

    # Pushed all the six kind of nodes in the subgraph. Done!
    return g


def generate_sparqls(_dbp):
    """
        The main function which generates and writes sparqls to file.

    :param _dbp: Dbpedia Interface obj.
    :return: @TODO: what indeed
    """

    print("Num ents: %d" % len(entities))

    for ent in entities:
        _generate_sparqls_(ent, _dbp)

    # Commented it out to help the case of cluttered output folder
    # for key in sparqls:
    #     with open('output/template%d.txt' % key, 'a+') as out:
    #         pprint(sparqls[key], stream=out)

    print("Pickling properties count to file")
    pickle.dump(predicates_count, open('resources/properties_count.pickle', 'w+'))

    print("Trying to write SPARQLs to file!")
    for key in sparqls:
        fo = open('sparqls/template%d.txt' % key, 'a+')
        for value in sparqls[key]:
            fo.writelines(json.dumps(value) + "\n")
        fo.close()

    print("These entities did not generating something")
    pprint(list(set(entity_went_bad)))


if __name__ == "__main__":

    # Suppress prints
    DEBUG = False
    warnings.simplefilter('once', EntityTypeNotFound)

    dbp = db_interface.DBPedia(_verbose=True, _caching=True)
    generate_sparqls(dbp)
