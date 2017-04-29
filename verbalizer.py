'''
	Author: Priyansh Trivedi

	Class: Verbalizer

	Since every template verbalizing was a little different, we started with individual scripts for each template. 
		However, there was a lot of code repetition and while changing anything, things could go really really bad. 

	This class is thus responsible for taking data from the output folder, and verbalizing it, based on what kind of template it is. 
	NOTE: this is an abstract class and will be used in different places

'''

import csv
import json
import random
import numpy as np
import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils
from pattern.en import pluralize
from pprint import pprint


class Verbalizer:

	'''
		Class variables. 
			template_id: the template ID (corresponds to the file from where we pick sparqls. Corresponds to ID in templates.py)
			has_x: if the x (or x's type) has been generated and expected to be in the mapping. 
			has_uri: same for URI
			template type: vanilla (for not count/filter/ask), count, filter_a, filter_b, ask (@TODO: Add a reference of this on the Doc)
			template id offset: if it's a vanilla then 0, 100 for count... 
	'''
	template_id = 0
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = False
	question_templates = {}		#Placeholder to keep all the templates here. In the form key: list, key:list

	
	def __init__(self):
		'''
			-> Open the template file with this ID. Convert to [JSON,JSON..]
				-> Pass the JSON from the filter
				-> Select a template based on rules
				-> Put a map on the template to verbalize a question
			-> Write the JSONs to file
		'''

		sparqls = []			#Holds the un-verbalized data
		questions = []			#Holds the verbalized data

		self.hard_relation_filter_map = {} 		#Keeps count of relations and limits. (Used in filter class)
		self.dbp = db_interface.DBPedia(_verbose=True) 	#To be used to fetch labels

		with open('sparqls/template%s.txt' % self.template_id) as data_file:
			for line in data_file:
				try:
					jsn = json.loads(line.replace('\n',""))
					sparqls.append(jsn)
				except:
					print line
					# raw_input("Waiting for input to continue")
					traceback.print_exc()

		#Shuffling the sparqls list to promote diversity
		random.shuffle(sparqls)

		for counter in range(len(sparqls)):

			#Declate the verbalized flag
			sparqls[counter]['verbalized'] = False

			datum = sparqls[counter]
			maps = datum["mapping"]

			if self.has_uri:
				try:
					uri = datum["answer_type"]["uri"]
					maps["uri"] = uri
				except:
					continue

			if self.has_x:
				try:
					x = datum["answer_type"]["x"]
					maps["x"] = x
				except:
					continue

			#See if you want this filtered
			if not self.filter(_datum = datum, _maps = maps):
				#Don't bother verbalizing this
				continue

			#Convert the URIs to their corresponding labels
			#@TODO: Use dbpedia labels to do this.
			for element in maps:
				# maps[element] = nlutils.get_label_via_parsing(maps[element], lower = True)  #Get their labels
				maps[element] = self.dbp.get_label(maps[element])  #Get their labels

			#Select a template for this question
			maps, question_format = self.rules(_maps = maps,_datum = datum)

			sparqls[counter]['verbalized_question'] = question_format % maps
			sparqls[counter]['verbalized'] = True
			sparqls[counter]['id'] = self.template_id + self.template_id_offset
			sparqls[counter]['type'] = self.template_type

		#Writing everything to file
		id = self.template_id + self.template_id_offset
		fo = open('output/verbalized_template%s.txt' % id, 'w+')
		for datum in sparqls:
			if datum['verbalized'] == True:
				fo.writelines(json.dumps(datum) + "\n")
		fo.close()

		questions = 0
		with open('output/verbalized_template%s_readable.txt' % id,'w+') as output_file:
			for datum in sparqls:
				try:
					output_file.write(datum['verbalized_question'].encode('utf-8')+'\n')
					output_file.write(datum['query'].encode('utf-8')+'\n\n')
					questions += 1
				except:
					continue

		#Count the number of verbalized questions
		# print "Template ID: ", id
		# print "Generated Questions: ", questions
		# print "Total data items: ", len(sparqls), 
		print ' '.join([str(id),str(questions),str(len(sparqls))])
		print "\n"

	def rules(self, _maps, _datum):
		'''
			Define the rules to select a question template here

			Also pluralize what needs pluralizing.

			Return the selected template. Return updated maps
		'''

		pass

	def filter(self, _datum, _maps):
		'''
			Put in all the conditions here which might stop a template from getting verbalized.

			Return type: Boolean
				Semantics:
					True: verbalize
					False: don't verbalize
		'''
		pass

	def hard_relation_filter(self, _pred1,_pred2 = None, _limit = 1, _limit_rels = 3):
		'''
			Keep the track of one of the predicates appearing in the mapping, and then only allow one question per predicate
			Uses a class variable (like a global var)

			USAGE: MANUAL! invoke in the filter class if needed

			Params:
				_pred: type: string. 
				_limit: the number of questions permitted per relation. Should be more than 1

			Return type: Boolean
				Semantics:
					True: verbalize
					False: don't verbalize
		'''
		if not _pred2:
			try:
				if self.hard_relation_filter_map[_pred1] >= _limit:
					return False
				self.hard_relation_filter_map[_pred1] += 1
			except:
				self.hard_relation_filter_map[_pred1] = 1
			return True

		else:
			try:
				if self.hard_relation_filter_map[_pred1][_pred2] >= _limit:
					return False
				self.hard_relation_filter_map[_pred1][_pred2] += 1
			except KeyError:
				#Either [_pred1][_pred2] does not exist, or [_pred1] does and [_pred2] does not.
				try:
					if len(self.hard_relation_filter_map[_pred1].keys()) > _limit_rels:
						return False

					#If here, then pred1 exists in the map. But pred2 does not. Also not more than 3 pred2 exist wrt to pred1. Hence, put pred1 in the list too
					self.hard_relation_filter_map[_pred1][_pred2] = 1
				except KeyError:
					self.hard_relation_filter_map[_pred1] = {_pred2 : 1} 
			return True

	def meine_family_filter(self,_pred1,_pred2):
		'''
			Implementing a general rule that 
				if either of the relations down there in 'family_relations' are in one of the predicates,
				and the other one is 'relation', return false

				else return true
		'''
		family_relations = ['spouse','father','mother','child','husband','wife']
		rel1 = _pred1.split('/')[-1]
		rel2 = _pred2.split('/')[-1]

		if rel1 == 'relation' or rel2 == 'relation':
			if rel1 in family_relations or rel2 in family_relations:
				# print rel1, rel2
				# raw_input()
				return False
			return True
		else:
			return True


