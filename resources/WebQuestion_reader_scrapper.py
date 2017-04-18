'''file reads from WebQA dataset and converts the url into dbpedia url'''
import json

#dbpedia interface
import utils.dbpedia_interface as db_interface
fname = 'webquestions.examples.train.json' #exact file name + directory here
with open(fname) as data_file:
	data = json.load(data_file)
dbPedia_url = []

for datum in data:
	freebase_url = str(datum[u"url"])
	freebase_label = " ".join(freebase_url.split("/")[-1].split("_"))
	dbr = "_".join(w.capitalize() for w in s.split()) 
	print dbr
	dbPedia_url.append(dbr)



