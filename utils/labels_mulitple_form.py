'''
	Author: pc.priyansh@gmail.com

	This script is used to integrate multiple forms of relations we previously collected. 

	Pseudocode:
		-> open the pickled multiple formed file and load it to a variable.
		-> for every key value pair, use dbo and dbp prefix to turn the key into a valid relation URI and merge it with the labels file.
		-> pickle that pair, replacing the labels.pickle file
'''
import pickle

def merge_multiple_forms():
	try:
		labels = pickle.load(open('resources/labels.pickle','r'))
	except:
		f = open('resources/labels.pickle','w+')
		labels = {}

	forms = pickle.load(open('resources/relations_multiple_forms.pickle'))

	for key in forms.keys():
		try:
			labels[u'http://dbpedia.org/property/'+key] = list(set(labels[u'http://dbpedia.org/property/'+key]+forms[key]))
		except KeyError:
			labels[u'http://dbpedia.org/property/'+key] = forms[key]

		try:
			labels[u'http://dbpedia.org/ontology/'+key] = list(set(labels[u'http://dbpedia.org/ontology/'+key]+forms[key]))
		except KeyError:
			labels[u'http://dbpedia.org/ontology/'+key] = forms[key]
	print "here"
	pickle.dump(labels,f)