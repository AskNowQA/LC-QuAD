'''
	Authro: Priyansh Trivedi

	Script to verbalize the count templates
	Each template ID will have a different class
		All extend the class created in verbalizer.py and edit it as per their requirements.

	Finally, a function will create an object of all of them and run it.

'''
import traceback
import numpy as np
from pprint import pprint
from pattern.en import pluralize
import utils.natural_language_utilities as nlutils

import verbalizer

class Verbalizer_01_Count(verbalizer.Verbalizer):

	template_id = 1
	template_type = 'Count'
	template_id_offset = 100
	has_x = False
	has_uri = True
	question_templates = {
		'vanilla':
			[ "How many <%(uri)s> are there whose <%(e_to_e_out)s> is <%(e_out)s>?",
			  "Give me a count of <%(uri)s> whose <%(e_to_e_out)s> is <%(e_out)s>?"]
	}

	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		return self.hard_relation_filter(_maps['e_to_e_out'])	

	def rules(self, _datum, _maps):
		'''
			Simple, just a simple template to work with.
		'''

		_maps['uri'] = pluralize(_maps['uri'])

		question_format = np.random.choice(self.question_templates['vanilla'])

		return _maps, question_format

class Verbalizer_02_Count(verbalizer.Verbalizer):

	template_id = 2
	template_type = 'Count'
	template_id_offset = 100
	has_x = False
	has_uri = False
	question_templates = {
		'vanilla':
			[ "Count the number of <%(e_in_to_e)s> in <%(e_in)s>?",
			  "Count the <%(e_in_to_e)s> in <%(e_in)s>?",
			  "How many <%(e_in_to_e)s> are there in <%(e_in)s>?"]
	}

	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		return self.hard_relation_filter(_maps['e_in_to_e'])	

	def rules(self, _datum, _maps):
		'''
			Simple, just a simple template to work with.
		'''

		question_format = np.random.choice(self.question_templates['vanilla'])

		return _maps, question_format

class Verbalizer_03_Count(verbalizer.Verbalizer):

	template_id = 3
	template_type = 'Count'
	template_id_offset = 100
	has_x = True
	has_uri = False
	question_templates = {
		'vanilla':
			[ "How many <%(e_in_to_e)s> are there of the <%(x)s> %(prefix)s is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?" ],
		'continous tense':
			[ "How many <%(e_in_to_e)s> are there of the <%(x)s> %(prefix)s is the <%(e_in_in_to_e_in)s> in <%(e_in_in)s> ?" ]
	}

	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		#The 'relation' vs 'father,mother...' rule
		if self.meine_family_filter(_maps['e_in_to_e'],_maps['e_in_in_to_e_in']):
			#Just that hard filter thingy
			return self.hard_relation_filter(_maps['e_in_to_e'],_maps['e_in_in_to_e_in'])
		else:
			return False

	def rules(self, _datum, _maps):
		'''
			Continous Tense Rule: if e_in_in_to_e_in has 'ing'?
				select continous tense template
			Else: vanilla template

			<finally> based on whether agent occurs in mapping type of x, change prefix (who/which)

			Pseudocode:
				-> see if 'ing' in e in in to e in
					-> yes?: use continous tense template
					-> no?: use vanilla template

				-> see if uri is person/people
					-> yes?: set maps's prefix to 'who'
					-> no?: set maps's preix to 'what'
		'''
		if 'ing' in _maps['e_in_in_to_e_in']:
			question_format = np.random.choice(self.question_templates['continous tense'])
		else: 
			question_format = np.random.choice(self.question_templates['vanilla'])

		if 'http://dbpedia.org/ontology/Agent' in _datum['mapping_type']['x'] and "http://dbpedia.org/ontology/Organisation" not in _datum['mapping_type']["x"]:
			_maps['prefix'] = 'who'
		else:
			_maps['prefix'] = 'which'

		return _maps, question_format

class Verbalizer_05_Count(verbalizer.Verbalizer):
	template_id = 5
	template_type = 'Count'
	template_id_offset = 100
	has_x = True
	has_uri = False
	question_templates = {
		'vanilla': 
			[ "Give the total number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"Count the <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"Count the number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"How many <%(e_in_to_e)s> are there, of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> ?",
			"How many <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>, are there ?",
			"What is the total number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> ?" ],

		'type': 
			[ "Give the total number of <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>.", 
			"Count the <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>.", 
			"Count the number of <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>.", 
			"How many <%(e_in_to_e)s> are there, of the <%(x)s> which are <%(e_in_out)s> ?", 
			"How many <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>, are there ?", 
			"What is the total nummber of <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s> ?" ]
	}
	
	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		#The 'relation' vs 'father,mother...' rule
		if self.meine_family_filter(_maps['e_in_to_e'],_maps['e_in_to_e_in_out']):
			#Just that hard filter thingy
			return self.hard_relation_filter(_maps['e_in_to_e'],_maps['e_in_to_e_in_out'])
		else:
			return False

	def rules(self, _datum, _maps):
		'''

			2. Type Mode:
				if e_in_to_e_in_out is type, use a type template
				else use vanilla template

			Pseudocode:

				-> see if the type rule is activated or not
					-> yes?: use type's plural template
					-> no?: use vanilla's plural template
		'''


		_maps['x'] = pluralize(_maps['x'])

		#Check for the type rule
		if _maps['e_in_to_e_in_out'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type'], p = [0.10,0.07,0.08,0.30,0.05,0.40])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'], p = [0.10,0.07,0.08,0.30,0.05,0.40])


		return _maps, question_format

class Verbalizer_06_Count(verbalizer.Verbalizer):
	template_id = 6
	template_type = 'Count'
	template_id_offset = 100
	has_x = False
	has_uri = True
	question_templates = {
		'vanilla': 
			[ "Give the total number of <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>.",
			"Count the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>.",
			"Count the number of <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>.",
			"How many <%(uri)s> are there whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s> ?",
			"How many <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s> are there?",
			"What is the total number of <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?"],

		'type': 
			[ "Give the total number of <%(uri)s> whose <%(e_to_e_out)s> is a kind of <%(e_out_out)s>.",
            "Give the total number of <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>." , 
            "Count the <%(uri)s> whose <%(e_to_e_out)s> is a kind of <%(e_out_out)s>.",
            "Count the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>." , 
            "Count the number of <%(uri)s> whose <%(e_to_e_out)s> is a kind of <%(e_out_out)s>.",
            "Count the number of <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>." , 
            "How many <%(uri)s> are there whose <%(e_to_e_out)s> is a kind of <%(e_out_out)s>?",
            "How many <%(uri)s> are there whose <%(e_to_e_out)s> is a <%(e_out_out)s>?" , 
            "How many <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s> are there?" , 
            "How many <%(uri)s> whose <%(e_to_e_out)s> is a kind of <%(e_out_out)s>, are there?",
            "What is the total number of <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?", 
            "What is the total number of <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?" ]
	}
	
	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		#The 'relation' vs 'father,mother...' rule
		if self.meine_family_filter(_maps['e_to_e_out'],_maps['e_out_to_e_out_out']):
			#Just that hard filter thingy
			return self.hard_relation_filter(_maps['e_to_e_out'],_maps['e_out_to_e_out_out'])
		else:
			return False

	def rules(self, _datum, _maps):
		'''

			2. Type Mode:
				if e_in_to_e_in_out is type, use a type template
				else use vanilla template

			Pseudocode:

				-> see if the type rule is activated or not
					-> yes?: use type's plural template
					-> no?: use vanilla's plural template
		'''


		_maps['uri'] = pluralize(_maps['uri'])

		#Check for the type rule
		if _maps['e_out_to_e_out_out'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type'], p = [0.05,0.05,0.035,0.035,0.04,0.04,0.15,0.15,0.025,0.025,0.2,0.2])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'], p = [0.1,0.07,0.08,0.3,0.05,0.4])

		return _maps, question_format


class Verbalizer_07_Count(verbalizer.Verbalizer):
	template_id = 7
	template_type = 'Count'
	template_id_offset = 100
	has_x = False
	has_uri = True
	question_templates = {
		
		'vanilla': 
			[ "Give me the total number of <%(uri)s> are there whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>.",
			"Count the <%(uri)s> are there whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>.",
			"Count the number of <%(uri)s> are there whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>.",
			"How many <%(uri)s> are there whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?",
			"What is the number of <%(uri)s> whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?" ]

	}

	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		if self.duplicate_prevention_filter(_maps['e_to_e_out'],_maps['e_out_1'],_maps['e_to_e_out'],_maps['e_out_2']):
			return self.hard_relation_filter(_maps['e_to_e_out'])
		else:
			return False
	
	def rules(self, _datum, _maps):
		'''
			No variations

			<finally> if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.			

			Pseudocode:
				-> pluralize the R, and the uri
		'''
		
		#In this template, e_to_e_out needs to be plural.
		_maps['e_to_e_out'] = pluralize(_maps['e_to_e_out'])
		_maps['uri'] = pluralize(_maps['uri'])

		question_format = np.random.choice(self.question_templates['vanilla'], p=[0.1,0.07,0.08,0.25,0.50])

		return _maps, question_format

class Verbalizer_08_Count(verbalizer.Verbalizer):
	template_id = 8
	template_type = 'Count'
	template_id_offset = 100
	has_x = False
	has_uri = True
	question_templates = {

		'vanilla': 
				[ "Give me the total number of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.",
				"Give me the count of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.",
				"Count the number of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.",  
				"Count the <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.",  
				"How many <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s> are there?", 
				"How many <%(uri)s> are there whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s> ?", 
				"What is the total number of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?" ],	
		'type': {

			'e_to_e_out_1': 
					[ "Give me the total number of <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.", 
					"Give me the count of <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.", 
					"Count the number of <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.", 
					"Count the <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>.", 
					"How many <%(uri)s> are there which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?",
					"How many <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s> are there.", 
					"Whatis the total number of <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?" ],
			'e_to_e_out_2': 
					[ 
					"Give me the total number of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>.", 
					"Give me the count of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>.", 
					"Count the number of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>.", 
					"Count the <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>.", 
					"How many <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s> are there?", 
					"How many <%(uri)s> are there whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>?",
					"What is the total number of <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>?" ],
			'both': 
					[ 
					"Give me the total number of of <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s>.", 
					"Give me the count of <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s>.", 
					"Count the number of <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s>.", 
					"Count the <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s>.", 
					"How many <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s> are there?", 
					"How many <%(uri)s> are there which are a <%(e_out_1)s> and a <%(e_out_2)s>?", 
					"What is the total number of <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s>?" 
					]	

		}
	}

	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		#The duplication rule
		if self.duplicate_prevention_filter(_maps['e_to_e_out_1'],_maps['e_out_1'],_maps['e_to_e_out_2'],_maps['e_out_2']):
			#The 'relation' vs 'father,mother...' rule
			if self.meine_family_filter(_maps['e_to_e_out_1'],_maps['e_to_e_out_2']):
				#Just that hard filter thingy
				return self.hard_relation_filter(_maps['e_to_e_out_1'],_maps['e_to_e_out_2'])
			else:
				return False
		else:
			return False

	def rules(self, _datum, _maps):
		'''
			1. Type Rule (if either of the rel is a type, change the template appropriately)
				1.a R1 is type
				1.b R2 is type
				1.c both are type
			2. Vanilla Rule:
				if no type, use vanilla template


			Pseudocode:
				-> see if R1 and R2 are type:
					-> yes? use type's both
					-> no? see if R1 is type:
						-> yes? use type's e_to_e_out_1 template
						-> no? see if R2 is a type:
							-> yes? use type's e_to_e_out_2 template
							-> no? use vanilla template

		'''

		_maps['uri'] = pluralize(_maps['uri'])

		if _maps['e_to_e_out_1'].lower() == 'type' and _maps['e_to_e_out_2'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type']['both'], p = [ 0.05,0.05,0.07,0.08,0.25,0.05,0.45])
		elif _maps['e_to_e_out_1'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type']['e_to_e_out_1'],p = [ 0.05,0.05,0.07,0.08,0.25,0.05,0.45])
		elif _maps['e_to_e_out_2'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type']['e_to_e_out_2'],p = [ 0.05,0.05,0.07,0.08,0.25,0.05,0.45])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'], p = [ 0.05,0.05,0.07,0.08,0.25,0.05,0.45])

		return _maps, question_format

class Verbalizer_11_Count(verbalizer.Verbalizer):
	template_id = 11
	template_type = 'Count'
	template_id_offset = 100
	has_x = True
	has_uri = False
	question_templates = {
		
		'vanilla': 
			[ "Give me the total number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"Give me the count of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"Count the other <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"Count the number of other <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"How many other <%(e_in_to_e)s> are there of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> ?",
			"How many other <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> are there?",
			"What is the total number of other <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?" ],

		'type': 
			[ "Give me the total number of other <%(e_in_to_e)s> are there of the <%(x)s> which are <%(e_in_out)s>.",
			"Give me the count of other <%(e_in_to_e)s> are there of the <%(x)s> which are <%(e_in_out)s>.",
			"Count the other <%(e_in_to_e)s> are there of the <%(x)s> which are <%(e_in_out)s>.",
			"Count the number of other <%(e_in_to_e)s> are there of the <%(x)s> which are <%(e_in_out)s>.",
			"How many other <%(e_in_to_e)s> are there of the <%(x)s> which are <%(e_in_out)s>?",
			"How many other <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s> are there?",
			"What is the total number of other <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>?" ]
	}

	def filter(self, _datum, _maps):
		if _datum['countable'] != 'true':
			return False

		#The 'relation' vs 'father,mother...' rule
		if self.meine_family_filter(_maps['e_in_to_e'],_maps['e_in_to_e_in_out']):
			#Just that hard filter thingy
			return self.hard_relation_filter(_maps['e_in_to_e'],_maps['e_in_to_e_in_out'])
		else:
			return False
	
	def rules(self, _datum, _maps):
		'''
			No variations

			<finally> if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.			

			Pseudocode:
				-> pluralize the R, and the uri
		'''
		
		_maps['x'] = pluralize(_maps['x'])

		if _maps['e_in_to_e_in_out'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type'], p=[0.05,0.05,0.07,0.08,0.25,0.05,0.45])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'], p=[0.05,0.05,0.07,0.08,0.25,0.05,0.45])

		return _maps, question_format

def run():
	nlqs = []
	spql = []	
	try:
		result = Verbalizer_01_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		# traceback.print_exc()
		# raw_input()
		print "Cannot verbalize template 1"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_02_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize template 2"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_03_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize template 3"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_03_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize template 3"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_05_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize Template 5"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_06_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize Template 6"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_07_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize Template 7"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_08_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize Template 8"
		nlqs.append(0)
		spql.append(0)
	try:
		result = Verbalizer_11_Count()
		nlqs.append(result.count_sparqls)
		spql.append(result.count_nlq)
	except:
		print "Cannot verbalize Template 11"
		nlqs.append(0)
		spql.append(0)

	return nlqs, spql

if __name__ == "__main__":
	counts = run()
	print counts
	f = open('resources_count.stats','a+')
	f.write( str(sum(counts[1])) + ' ' + str(sum(counts[0])) + '\n')
	f.close()