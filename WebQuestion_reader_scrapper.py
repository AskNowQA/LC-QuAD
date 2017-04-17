'''file reads from WebQA dataset and converts the url into dbpedia url'''
import json
import utils.dbpedia_interface as db_interface

fname = '/home/gaurav/Downloads/dataset/WebQuestion/webquestions.examples.train.json' #exact file name + directory here

dbp = db_interface.DBPedia(_verbose=True)


with open(fname) as data_file:
	data = json.load(data_file)
dbPedia_url = []

for datum in data:
	freebase_url = str(datum[u"url"])
	freebase_label = " ".join(freebase_url.split("/")[-1].split("_"))
	dbr = "http://dbpedia.org/resource/" + "_".join(w.capitalize() for w in freebase_label.split())
	if dbp.is_Url(dbr):
		dbPedia_url.append(dbr)
print len(dbPedia_url)

urls = set(dbPedia_url)
f = open("resources/WebQA.txt","w")
for url in urls:
	f.write(url + "\n")
f.close()



