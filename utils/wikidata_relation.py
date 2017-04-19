import dbpedia_interface as db_interface
from pprint import pprint
import traceback
import pickle
dbp = db_interface.DBPedia(_verbose=True)

answer = dbp.shoot_custom_query(''' select ?url ?prop where { ?url owl:equivalentProperty ?prop FILTER(regex(?prop, "^http://www.wikidata.org")) } ''')

dict = {}
for x in answer['results']['bindings']:
	try:
		dict[x['prop']['value'].split("/")[-1]] = x['url']['value'].split("/")[-1]
	except:
		continue

# for key in dict:
# 	print key,dict[key]
# 	# raw_input()

filelocation = "/home/gaurav/codes/relationWikidata/asknow-UI-master/wikidata-properties"

# f = open(filename).read().split('\n')

rel_dict = {}

for key in dict:
	print key, dict[key]
	try:
		f = filelocation + "/" + key + ".txt"
		try:
			content = open(f).read().split('\n')
			rel_dict[dict[key]] = content
		except:
			print traceback.print_exc()
	except:
		print traceback.print_exc()

rel_dict_set = {}
for key in rel_dict:
	rel_dict_set[key] = list(set(rel_dict[key]))

pprint(rel_dict_set)

pickle.dump(rel_dict_set,open("wiki_rel.pickle","w"))