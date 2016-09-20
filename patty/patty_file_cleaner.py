'''
One time script, only for the purpose of cleaning the https://raw.githubusercontent.com/qcl/master-research/master/patty/patty.dbpedia.Relations.json relations file of Patty relations
'''
from pprint import pprint
import string
f = open("patty.dbpedia.Relations.json")
fr = f.read().replace('"','').replace(',','').replace('\t','').split('\n')[1:]

output = []
output_file = open("patty.dbpedia.Relations.txt","w+")
for rel in fr:
	if rel.isalpha():
		output.append(rel)

output_file.write('\n'.join(output))
f.close()
output_file.close()