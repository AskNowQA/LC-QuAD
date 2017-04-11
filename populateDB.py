'''file should read from text file and add it to the index '''
#read from the file and convert it into json
import json, traceback
from pymongo import MongoClient

#database conneections 
client = MongoClient('localhost', 27017)
db = client.test_database
posts = db.posts
#read from file and form a list of json 

def read_from_file(_file_name):
	data = []
	with open(_file_name) as data_file:
		for line in data_file:
			data.append(json.loads(line.rstrip('\n')))
	return data

def insert_into_db(data):
	#bulk insert
	try:
		result = posts.insert_many(data)
		return True 
	except:
		print traceback.print_exc()
		return False

print insert_into_db(read_from_file("json_template6.txt"))
#For searching:- pprint.pprint(posts.find_one({u"id":"6"}))