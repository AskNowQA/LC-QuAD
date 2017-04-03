from pprint import pprint
import common_functionality as cf

def template4(access,):
    '''
            Template #4:
                SELECT DISTINCT ?uri WHERE { <%(e_out_in)s> <%(e_out_in_to_e_out)s> ?x . ?uri <%(e_to_e_out)s> ?x }
            Find e_in and e_in_to_e.
        '''

    # Query the graph for outnodes from e and relevant properties
    op = access.return_outnodes('e')
    counter_template4 = 0
    # Create a list of all these (e_to_e_out, e_out)
    one_triple_right_map = {triple[1].getUri(): triple[2]['object'].getUri() for triple in op[0]}
    pprint(one_triple_right_map)

    # Collect all e_out_in and e_out_in_to_e_out
    op = access.return_innodes('e_out')

    # This 'op' has the e_out_in and the prop for all e_out's. We now need to map one to the other.
    for list_of_triples in op:

        # Some triple are simply empty. Ignore them.
        if len(list_of_triples) == 0:
            continue

        ### Mapping e_out_in's to relevant e_out's ###

        # Pick one triple from the list.
        e_out = list_of_triples[0][1].getUri()
        e_to_e_out = one_triple_right_map[e_out]  # Find the relevant property from the map

        # Given this information, lets create mappings of template four
        for triple in list_of_triples:

            # Making the variables explicit (for the sake of readability)
            e_out_in = triple[0].getUri()
            e_out_in_to_e_out = triple[2]['object'].getUri()

            # Create a mapping (in keeping with the templates' placeholder names)
            mapping = {'e_out_in': e_out_in, 'e_out_in_to_e_out': e_out_in_to_e_out, 'e_to_e_out': e_to_e_out,
                       'e_out': e_out}

            # Throw it to a function who will put it in the list with appropriate bookkeeping
            try:
                cf.fill_specific_template(_template_id=4, _mapping=mapping, _debug=False)
                counter_template4 = counter_template4 + 1
                print str(counter_template4), "tempalte4"
            except:
                print "check error stack"
                continue
            if counter_template4 > 10:
                pass