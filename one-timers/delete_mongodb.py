'''This can drop the dataset. So I am commenting the drop line. Uncomment'''
import json, traceback
from pymongo import MongoClient
import pickle
#database conneections 
client = MongoClient('localhost', 27017)
db = client.document_database
posts = db.posts



#delete everything which have not been corrected or edited. 
# result = posts.delete_many({u"corrected": u"false"})

delete = posts.find({u"corrected":"true"}).count()

print delete