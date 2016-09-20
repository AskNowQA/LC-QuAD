'''
If this script wins a nobel for Theatre, send dem trophies (and cheques) to - Priyansh (pc.priyansh@gmail.com)

Using this script to find SPARQL Queries from qald's JSON file, and trying to parse and extract the predicats from the tuples. 

If you're trying to recreate this, run this file first.
'''

import json

#Loading the JSON file in memory
qald_file = open('qald-6-train-multilingual.json','r')
qald_json = json.load(qald_file)

#Seperating the SPARQLs
qald_sparqls = [ x[u'query'][u'sparql'] for x in qald_json[u'questions'] if not x[u'query'] == {}]

# #Writing them to a file
# output = '\n'.join(qald_sparqls)
# output_file = open('qald-6-train-sparqls.txt','w+')
# output_file.write(output)

# output_file.close()
# qald_file.close()

# for sparql in qald_sparqls:
# 	within_braces = sparql.split('{')[1].strip()
# 	tuples = within_braces.split('.')
# 	for tup in tuples:
# 		tup.split()
