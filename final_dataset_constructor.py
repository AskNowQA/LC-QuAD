from pymongo import MongoClient
import pickle
from bson.objectid import ObjectId
import json, traceback
import random
from pprint import pprint
#database conneections 
client = MongoClient('localhost', 27017)
db = client.document_database
posts = db.posts


def retrivedCorrectedQuestion():
	#reviewed:false has to be added to the database.
	question = posts.find({u"corrected" : u"true", u"verbalized":True})
	# print "***", question
	if question:
		return question
	else:
		return False

questions = retrivedCorrectedQuestion()
# print len(questions)
print "done"
ques= []
for question in questions:
	# print question
	# raw_input()
	ques.append(question)
random.shuffle(ques)
len(ques)
new_dict = []

# {u'_id': u'32 charachter long alpha-numeric ID',
#  u'corrected_answer': u'Verbalized form by the First reviewer',
#  u'id': "template id in integer",
#  u'query': u' The actual SPARQL queries',
#  u'template': u'The tempalte of the SPARQL Query ',
#  u'verbalized_question': u'Semi verbalized query'}


for q in ques:
	# print type(q)
	# pprint(q)
	# new_dict.append(map(q.pop, [u'answer',u'answer_count',u'answer_type',u'corrected',u'countable',u'mapping',u'mapping_type',u'n_entities',u'reviewed',u'type',u'username',u'verbalized']))
	new_dict.append(dict((k, q[k]) for k in (u'_id', u'corrected_answer', u'id', u'query', u'template', u'verbalized_question')))
	# pprint(new_dict)
	# raw_input()

with open('data_v2.json', 'w') as outfile:
    json.dump(new_dict, outfile)
