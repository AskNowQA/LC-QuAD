#Importing some external libraries
from pprint import pprint
import networkx as nx
import pickle
import json
import copy
import traceback

#Importing internal classes/libraries
import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
import utils.subgraph as subgraph

#@TODO: put this class there

'''
    Initializing some stuff. Namely: DBpedia interface class.
    Reading the list of 'relevant' properties.
'''

dbp = None	#DBpedia interface object #To be instantiated when the code is run by main script/unit testing script
relevant_properties = open('resources/relation_whitelist.txt').read().split('\n')    #Contains the whitelisted props types
templates = json.load(open('templates.py'))   #Contains all the templates existing in templates.py
sparqls = {}   #Dict of the generated SPARQL Queries.


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
                        
    ########### e p eout . eout ?p ?e (e_out_to_e_out_out and e_out_out) ###########
    
    #Get all the eout nodes back from the subgraph.
    e_outs = []
    op = access.return_outnodes('e')
    for x in op: 
        for tup in x:
            e_outs.append(tup[1].getUri())
            
    labels = ('e_out','e_out_to_e_out_out','e_out_out')
    
    for e_out in e_outs:
        results = dbp.shoot_custom_query(one_triple_right % {'e' : e_out})
        
        #Insert results in subgraph
        insert_triple_in_subgraph(G, _results=results, 
                                 _labels=labels, _direction=True, 
                                 _origin_node=e_out, _filter_properties=True)
    
    ########### e p eout . ?e ?p eout  (e_out_in and e_out_in_to_e_out) ###########
    
    #Use the old e_outs variable
    labels = ('e_out_in','e_out_in_to_e_out','e_out')
    
    for e_out in e_outs:
        results = dbp.shoot_custom_query(one_triple_left % {'e' : e_out})
        
        #Insert results in subgraph
        insert_triple_in_subgraph(G, _results=results, 
                                 _labels=labels, _direction=False, 
                                 _origin_node=e_out, _filter_properties=True)
        
    ########### ?e ?p ein . ein p e  (e_in_in and e_in_in_to_e_in) ###########
    
    #Get all the ein nodes back from subgraph
    e_ins = []
    op = access.return_innodes('e')
    for x in op:
        for tup in x:
            e_ins.append(tup[0].getUri())
    
    
    labels = ('e_in_in','e_in_in_to_e_in','e_in')
    
    for e_in in e_ins:
        results = dbp.shoot_custom_query(one_triple_left % {'e': e_in})
        
        #Insert results in subgraph
        insert_triple_in_subgraph(G, _results=results, 
                                 _labels=labels, _direction=False, 
                                 _origin_node=e_in, _filter_properties=True)
        
    ########### ein ?p ?e . ein p e  (e_in_to_e_in_out and e_in_out) ###########
    
    #Use the old e_ins variable
    labels = ('e_in','e_in_to_e_in_out','e_in_out')
    
    for e_in in e_ins:
        results = dbp.shoot_custom_query(one_triple_right % {'e': e_in })
        
        #Insert results in subgraph
        insert_triple_in_subgraph(G, _results=results, 
                                 _labels=labels, _direction=True, 
                                 _origin_node=e_in, _filter_properties=True)
    
    
    #Pushed all the six kind of nodes in the subgraph. Done!
    return G

def fill_specific_template(_template_id, _mapping, _debug = False):
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
    
    #Create a copy of the template
    template = [x for x in templates if x['id'] == _template_id][0]
    template = copy.copy(template)
    
    #From the template, make a rigid query using mappings
    try:
        template['query'] = template['template'] % _mapping
    except KeyError:
        print "fill_specific_template: ERROR. Mapping does not match."
        return False
    
    #Include the mapping within the template object
    template['mapping'] = _mapping
    
    #Get the Answer of the query
    #get_answer now returns a dictionary with appropriate variable bindings. 
    template['answer'] = dbp.get_answer(template['query'])
    
    #Get the most specific type of the answers.
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
    
    
    if _debug:
        pprint(template)
    
    #Push it onto the SPARQL List
    #perodic write in file. 
    #@TODO: instead of file use a database.
    try:
        sparqls[_template_id].append(template)
        print len(sparqls[_template_id])
        if len(sparqls[_template_id]) > 100:
            print "in if condition"
            print "tempalte id is " , str(_template_id)
            with open('output/template%s.txt' % str(_template_id), "a+") as out:
                pprint(sparqls[_template_id], stream=out)
            with open('output/template%s.json' % str(_template_id), "a+") as out:
                json.dump(sparqls[_template_id],out)
            sparqls[_template_id] = []
    except:
        print traceback.print_exc()
        sparqls[_template_id] = [ template ]

    
    return True

def fill_templates(_graph,_uri):
    '''
        This function is programmed to traverse through the Subgraph and create mappings for templates

        Per template traverse the graph, and pick out the needed stuff in local variables
    '''
    
    global dbp
    
    access = subgraph.accessGraph(_graph)
    
    ''' 
        Template #1: 
            SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> } 
        Find e_out and e_to_e_out.
    '''
    counter_template1 = 0
    
    #Query the graph for outnodes from e
    op = access.return_outnodes('e')
    
    for triple in op[0]:
        
        #Making the variables explicit (for the sake of readability)
        e_out = triple[1].getUri()
        e_to_e_out = triple[2]['object'].getUri()
    
        #Create a mapping (in keeping with the templates' placeholder names)
        mapping = {'e_out': e_out, 'e_to_e_out': e_to_e_out }
        
        #Throw it to a function who will put it in the list with appropriate bookkeeping
        try:
            fill_specific_template(_template_id=1, _mapping=mapping)
            print str(counter_template1) , "tempalte1"
            counter_template1 = counter_template1 + 1
        except:
            print "check error stack"
            continue
        if counter_template1 > 10:
            pass
#             break
    
    ''' 
        Template #2: 
            SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri }
        Find e_in and e_in_to_e.
    '''
    
    #Query the graph for innodes to e
    op = access.return_innodes('e')
    counter_template2 = 0
    for triple in op[0]:
    
        #Making the variables explicit (for the sake of readability)
        e_in = triple[0].getUri()
        e_in_to_e = triple[2]['object'].getUri()
        
        #Create a mapping (in keeping with the templates' placeholder names)
        mapping = {'e_in':e_in, 'e_in_to_e': e_in_to_e}
        
        #Throw it to a function who will put it in the list with appropriate bookkeeping
        try:
            fill_specific_template( _template_id=2, _mapping=mapping)
            counter_template2 = counter_template2 + 1
            print str(counter_template2) , "tempalte2"
        except:
            print traceback.print_exc()
            continue
        if counter_template2 > 10:
            pass
#             break
        
    ''' 
        Template #3: 
            SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri }
        Find e_in and e_in_to_e.
    '''
    
    #Query the graph for innode to e and relevant properties
    op = access.return_innodes('e')
    counter_template3 = 0
    #Create a list of all these (e_in, e_in_to_e)
    one_triple_left_map = { triple[0].getUri(): triple[2]['object'].getUri()  for triple in op[0] }
    pprint(one_triple_left)
        
    #Collect all e_in_in and e_in_in_to_e_in 
    op = access.return_innodes('e_in')
        
    #This 'op' has the e_in_in and the prop for all e_in's. We now need to map one to the other.
    for list_of_triples in op:

        #Some triple are simply empty. Ignore them.
        if len(list_of_triples) == 0:
            continue

        ### Mapping e_in_in's to relevant e_in's ###
        
        #Pick one triple from the list.
        e_in = list_of_triples[0][1].getUri()
        e_in_to_e = one_triple_left_map[e_in]
        #Find the relevant property from the map
        
        #Given this information, lets create mappings of template three 
        for triple in list_of_triples:
            
            #Making the variables explicit (for the sake of readability)
            e_in_in = triple[0].getUri()
            e_in_in_to_e_in = triple[2]['object'].getUri()
            
            #Create a mapping (in keeping with the templates' placeholder names)
            mapping = { 'e_in_in':e_in_in, 'e_in_in_to_e_in': e_in_in_to_e_in, 'e_in_to_e':e_in_to_e, 'e_in': e_in }
        
            #Throw it to a function who will put it in the list with appropriate bookkeeping
            try:
                fill_specific_template( _template_id=3, _mapping=mapping)
                counter_template3 = counter_template3 + 1
                print str(counter_template3) , "tempalte3"
                if counter_template1 > 10:
                    pass
#                     break
            except:
                print "check error stack"
                traceback.print_exc()
                continue
    ''' 
        Template #4: 
            SELECT DISTINCT ?uri WHERE { <%(e_out_in)s> <%(e_out_in_to_e_out)s> ?x . ?uri <%(e_to_e_out)s> ?x }
        Find e_in and e_in_to_e.
    '''       
    
    #Query the graph for outnodes from e and relevant properties
    op = access.return_outnodes('e')
    counter_template4 = 0
    #Create a list of all these (e_to_e_out, e_out)
    one_triple_right_map = { triple[1].getUri(): triple[2]['object'].getUri() for triple in op[0] }
    pprint(one_triple_right_map)
    
    #Collect all e_out_in and e_out_in_to_e_out 
    op = access.return_innodes('e_out')
    
    #This 'op' has the e_out_in and the prop for all e_out's. We now need to map one to the other.
    for list_of_triples in op:

        #Some triple are simply empty. Ignore them.
        if len(list_of_triples) == 0:
            continue

        ### Mapping e_out_in's to relevant e_out's ###
    
        #Pick one triple from the list.
        e_out = list_of_triples[0][1].getUri()
        e_to_e_out = one_triple_right_map[e_out]   #Find the relevant property from the map
        
         #Given this information, lets create mappings of template four 
        for triple in list_of_triples:
            
            #Making the variables explicit (for the sake of readability)
            e_out_in = triple[0].getUri()
            e_out_in_to_e_out = triple[2]['object'].getUri()
            
            #Create a mapping (in keeping with the templates' placeholder names)
            mapping = { 'e_out_in':e_out_in, 'e_out_in_to_e_out': e_out_in_to_e_out, 'e_to_e_out':e_to_e_out, 'e_out': e_out }
        
            #Throw it to a function who will put it in the list with appropriate bookkeeping
            try:
                fill_specific_template( _template_id=4, _mapping=mapping, _debug=False)
                counter_template4 = counter_template4 + 1
                print str(counter_template4) , "tempalte4"
            except:
                print "check error stack"
                continue    
            if counter_template4 > 10:
                pass
#                 break

'''
    Testing the ability to create subgraph given a URI
    Testing the ability to generate sparql templates
'''
sparqls = {}
dbp =  db_interface.DBPedia(_verbose = True)
uri = 'http://dbpedia.org/resource/Chicago'

#Generate the local subgraph
graph = get_local_subgraph(uri)

#Generate SPARQLS based on subgraph
fill_templates(graph,_uri=uri)

#Write the SPARQLs to disk in Pretty Print format
for i in range(1,5):
    with open('output/template%d.txt' % i, 'wt') as out:
        pprint(sparqls[i], stream=out)
for i in range(1,5):
    f = open('output/template%s.json' % i, 'wt')
    json.dump(sparqls[i],f)
    f.close()
print "DONE"