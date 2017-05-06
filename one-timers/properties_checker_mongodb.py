# result = posts.delete_many({u"corrected": u"false",u"id":8})
import json, traceback
from pymongo import MongoClient
import pickle
#database conneections 
client = MongoClient('localhost', 27017)
db = client.document_database
posts = db.posts


delete = posts.find({u"corrected":"true",u"delete":"true"}).count()
counter = posts.find({u"id":1}).count()
print counter
# print delete
question = posts.find({u"corrected":"true"}).count()
# ques = []
# for q in question:
# 	ques.append(q)
# print type(ques)
# pickle.dump(ques,open("corrected_question.dat","w"))
# print delete
print question - delete