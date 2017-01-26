#Importing some external libraries
from pprint import pprint
import networkx as nx
import pickle
import json
import copy

#Importing internal classes/libraries
import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
import utils.subgraph as subgraph

#@TODO: put this class there



'''
    Initializing some stuff. Namely: DBpedia interface class.
    Reading the list of 'relevant' properties.
'''

dbp = None  #DBpedia interface object #To be instantiated when the code is run by main script/unit testing script
relevant_properties = open('resources/relation_whitelist.txt').read().split('\n')    #Contains the whitelisted props types
templates = json.load(open('templates.py'))   #Contains all the templates existing in templates.py
sparqls = []   #List of the generated SPARQL Queries. It will be a good idea to write them to disk once in a while.


'''
    Some SPARQL Queries.
    Since this part of the code requires sending numerous convoluted queries to DBpedia, 
        we best not clutter the DBpedia interface class and rather simply declare them here.
        
    Note: The names here can be confusing. Refer to the diagram above to know what each SPARQL query tries to do.
'''

one_triple_right = '''
            SELECT DISTINCT ?p ?e 
            WHERE { 
                <%(e)s> ?p ?e 
            }'''

one_triple_left = '''
            SELECT DISTINCT ?e ?p
            WHERE {
                ?e ?p <%(e)s>
            }'''

'''
    This cell houses the script which will build a subgraph as shown in picture above for each a given URI.
    @TODO: do something in cases where certain nodes of the local subgraph are not found. 
            Will the code throw errors? How to you take care of them?
'''

def insert_triple_in_subgraph(G, _results, _labels, _direction, _origin_node, _filter_properties = True, _filter_literals = True):
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
    '''
    
    
    for result in _results[u'results'][u'bindings']:
        #Parse the results into local variables (for readibility)
        prop = result[u'p'][u'value']
        ent = result[u'e'][u'value']
        
        if _filter_literals:
            if nlutils.has_literal(ent):
                continue

        if _filter_properties:
            
            #Filter results based on important properties
            if not prop.split('/')[-1] in relevant_properties:
                continue
        
        #Finally, insert, based on direction
        if _direction == True:
            #Right
            subgraph.insert(G=G, data=[ (_labels[0],_origin_node), (_labels[1],prop), (_labels[2],ent) ])
            
        elif _direction == False:
            #Left
            subgraph.insert(G=G, data=[(_labels[0],ent), (_labels[1],prop), (_labels[2],_origin_node) ])       

            
            
def get_local_subgraph(_uri):
    #Collecting required variables: DBpedia interface, and a new subgraph
    global dbp
    
    #Create a new graph
    G = nx.DiGraph()
    access = subgraph.accessGraph(G)
    
    
    ########### e ?p ?e (e_to_e_out and e_out) ###########
    
    results = dbp.shoot_custom_query(one_triple_right % {'e': _uri})
    labels = ('e','e_to_e_out','e_out')

    #Insert results in subgraph
    insert_triple_in_subgraph(G, _results=results, 
                             _labels=labels, _direction=True, 
                             _origin_node=_uri, _filter_properties=True)
    
    ########### ?e ?p e (e_in and e_in_to_e) ###########
    
    results = dbp.shoot_custom_query(one_triple_left % {'e':_uri} )
    labels = ('e_in', 'e_in_to_e','e')
    
    #Insert results in subgraph
    insert_triple_in_subgraph(G, _results=results, 
                             _labels=labels, _direction=False, 
                             _origin_node=_uri, _filter_properties=True)
                        
#     ########### e p eout . eout ?p ?e (e_out_to_e_out_out and e_out_out) ###########
    
#     #Get all the eout nodes back from the subgraph.
#     e_outs = []
#     op = access.return_outnodes('e')
#     for x in op: 
#         for tup in x:
#             e_outs.append(tup[1].getUri())
            
#     labels = ('e_out','e_out_to_e_out_out','e_out_out')
    
#     for e_out in e_outs:
#         results = dbp.shoot_custom_query(one_triple_right % {'e' : e_out})
        
#         #Insert results in subgraph
#         insert_triple_in_subgraph(G, _results=results, 
#                                  _labels=labels, _direction=True, 
#                                  _origin_node=e_out, _filter_properties=True)
    
#     ########### e p eout . ?e ?p eout  (e_out_in and e_out_in_to_e_out) ###########
    
#     #Use the old e_outs variable
#     labels = ('e_out_in','e_out_in_to_e_out','e_out')
    
#     for e_out in e_outs:
#         results = dbp.shoot_custom_query(one_triple_left % {'e' : e_out})
        
#         #Insert results in subgraph
#         insert_triple_in_subgraph(G, _results=results, 
#                                  _labels=labels, _direction=False, 
#                                  _origin_node=e_out, _filter_properties=True)
        
#     ########### ?e ?p ein . ein p e  (e_in_in and e_in_in_to_e_in) ###########
    
#     #Get all the ein nodes back from subgraph
#     e_ins = []
#     op = access.return_innodes('e')
#     for x in op:
#         for tup in x:
#             e_ins.append(tup[0].getUri())
    
    
#     labels = ('e_in_in','e_in_in_to_e_in','e_in')
    
#     for e_in in e_ins:
#         results = dbp.shoot_custom_query(one_triple_left % {'e': e_in})
        
#         #Insert results in subgraph
#         insert_triple_in_subgraph(G, _results=results, 
#                                  _labels=labels, _direction=False, 
#                                  _origin_node=e_in, _filter_properties=True)
        
#     ########### ein ?p ?e . ein p e  (e_in_to_e_in_out and e_in_out) ###########
    
#     #Use the old e_ins variable
#     labels = ('e_in','e_in_to_e_in_out','e_in_out')
    
#     for e_in in e_ins:
#         results = dbp.shoot_custom_query(one_triple_right % {'e': e_in })
        
#         #Insert results in subgraph
#         insert_triple_in_subgraph(G, _results=results, 
#                                  _labels=labels, _direction=True, 
#                                  _origin_node=e_in, _filter_properties=True)
    
    
    #Pushed all the six kind of nodes in the subgraph. Done!
    return G


def fill_specific_template(_template_id, _mapping):
    '''
        Function to fill a specific template.
        Given the template ID, it is expected to fetch the template from the set 
            and juxtapose the mapping on the template
    
         -> create copy of template from the list
         -> push it in the list
         -> periodic writes to disk (of the list)
    '''
    
    global sparql, templates
    
    #Create a copy of the template
    template = [x for x in templates if x['id'] == _template_id][0]
    template = copy.copy(template)
    try:
        template['query'] = template['template'] % _mapping
    except KeyError:
        print "fill_specific_template: ERROR. Mapping does not match."
        print "************************* ERROR DETAILS:" 
        print "id: ", _template_id
        print "mapping",
        pprint(_mapping)
        print "************************* END." 
    template['mapping'] = _mapping
    
    #DEBUG
    pprint(template)
    raw_input()
    
    #Push it onto the SPARQL List
    sparqls.append(template)

    #@TODO: Periodic writes to disk
    
    return True


def fill_templates(_graph):
    '''
        This function is programmed to traverse through the Subgraph and create mappings for templates

        Per template traverse the graph, and pick out the needed stuff in local variables
    '''
    
    access = subgraph.accessGraph(_graph)


    ''' 
        Template #1: 
            SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> } 
        Find e_out and e_to_e_out.
    '''
    
    #Query the graph for outnodes from e
    op = access.return_outnodes('e')
    
    for triple in op[0]:
        
        #Making the variables explicit (for the sake of readability)
        e_out = triple[1].getUri()
        e_to_e_out = triple[2]['object'].getUri()
    
        #Create a mapping (in keeping with the templates' placeholder names)
        mapping = {'e_out': e_out, 'e_to_e_out': e_to_e_out }
        
        #Throw it to a function who will put it in the list with appropriate bookkeeping
        fill_specific_template(_template_id=1, _mapping=mapping)
        
    
    ''' 
        Template #2: 
            SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri }
        Find e_in and e_in_to_e.
    '''
    
    #Query the graph for outnodes from e
    op = access.return_innodes('e')
    
    for triple in op[0]:
    
        #Making the variables explicit (for the sake of readability)
        e_in = triple[0].getUri()
        e_in_to_e = triple[2]['object'].getUri()
        
        #Create a mapping (in keeping with the templates' placeholder names)
        mapping = {'e_in':e_in, 'e_in_to_e': e_in_to_e}
        
        #Throw it to a function who will put it in the list with appropriate bookkeeping
        fill_specific_template( _template_id=2, _mapping=mapping)
        
        
if __name__ == '__main__':
    dbp =  db_interface.DBPedia(_verbose = True)
    uri = 'http://dbpedia.org/resource/Bareilly'
    graph = get_local_subgraph(uri)
    f = open('output/graph.pickle','w+')
    pickle.dump(graph,f)
    fill_templates(graph)