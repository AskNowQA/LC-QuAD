'''file should read from text file and add it to the index '''
#read from the file and convert it into json
import json, traceback
from pymongo import MongoClient

#database conneections 
client = MongoClient('localhost', 27017)
db = client.document_database
posts = db.posts
#read from file and form a list of json 

def read_from_file(_file_name):
	data = []
	with open(_file_name) as data_file:
		for line in data_file:
			data.append(json.loads(line.rstrip('\n')))
	print len(data)		
	return data

def insert_into_db(data):
	#bulk insert
	try:
		result = posts.insert_many(data)
		return True 
	except:
		print traceback.print_exc()
		return False

def insert_into_db_single(data):
	for datum in data:
		print "for"
		if retriveQuestion(datum['query']):
			try:
				result = posts.insert_one(datum)
				print "done"
			except:
				print traceback.print_exc()
				continue
		else:
			print "here"
			continue	
	return True

def retriveQuestion(sparql):
	'''connects to a database and retrives question based on template type'''
	question = posts.find_one({u"query":sparql.encode('utf-8')})
	if question:
		return False
	else:
		return True


print insert_into_db_single(read_from_file("verbalized_template1.txt"))
print insert_into_db_single(read_from_file("verbalized_template3.txt"))
print insert_into_db_single(read_from_file("verbalized_template5.txt"))
print insert_into_db_single(read_from_file("verbalized_template6.txt"))
print insert_into_db_single(read_from_file("verbalized_template7.txt"))
print insert_into_db_single(read_from_file("verbalized_template8.txt"))
print insert_into_db_single(read_from_file("verbalized_template9.txt"))
print insert_into_db_single(read_from_file("verbalized_template11.txt"))
print insert_into_db_single(read_from_file("verbalized_template15.txt"))
print insert_into_db_single(read_from_file("verbalized_template16.txt"))
#For searching:- pprint.pprint(posts.find_one({u"id":"6"}))