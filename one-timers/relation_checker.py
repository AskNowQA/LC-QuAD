'''file should read from text file and add it to the index '''
#read from the file and convert it into json
import json, traceback,collections
from pprint import pprint
from pymongo import MongoClient

#database conneections 
client = MongoClient('localhost', 27017)
db = client.document_database
posts = db.posts

rel_name = []

def read_from_file(_file_name):
	data = []
	with open(_file_name) as data_file:
		for line in data_file:
			data.append(json.loads(line.rstrip('\n')))
	# print len(data)		
	return data


def insert_into_db_single(data):
	for datum in data:
		query = datum["query"].split(" ")
		for q in query:
			if "http://dbpedia.org/ontology/" in q or "http://dbpedia.org/property/" in q:
				rel_name.append(q)


# insert_into_db_single(read_from_file("45/verbalized_template1.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template2.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template3.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template5.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template6.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template7.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template8.txt"))
# # insert_into_db_single(read_from_file("45/verbalized_template9.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template11.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template15.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template16.txt"))


# insert_into_db_single(read_from_file("oldOutPut/verbalized_template1.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template2.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template3.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template5.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template6.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template7.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template8.txt"))
# # insert_into_db_single(read_from_file("45/verbalized_template9.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template11.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template15.txt"))
# insert_into_db_single(read_from_file("oldOutPut/verbalized_template16.txt"))


# insert_into_db_single(read_from_file("144/verbalized_template1.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template2.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template3.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template5.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template6.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template7.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template8.txt"))
# # insert_into_db_single(read_from_file("45/verbalized_template9.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template11.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template15.txt"))
# insert_into_db_single(read_from_file("144/verbalized_template16.txt"))


# insert_into_db_single(read_from_file("690/verbalized_template1.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template2.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template3.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template5.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template6.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template7.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template8.txt"))
# # insert_into_db_single(read_from_file("45/verbalized_template9.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template11.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template15.txt"))
# insert_into_db_single(read_from_file("690/verbalized_template16.txt"))

insert_into_db_single(read_from_file("100_new_new/verbalized_template1.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template2.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template3.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template5.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template6.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template7.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template8.txt"))
# insert_into_db_single(read_from_file("45/verbalized_template9.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template11.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template15.txt"))
insert_into_db_single(read_from_file("100_new_new/verbalized_template16.txt"))


print len(rel_name)
print len((collections.Counter(rel_name)))
d = (collections.Counter(rel_name))
print d
large = open("large.txt","w")
smaller = open("smaller.txt","w")
counter = 0
for x in d:
	if d[x] > 30:
		large.write(x + "\n")
		counter = counter + 1
	else:
		smaller.write(x + "\n")
		pass
large.close()
smaller.close()
print counter	
