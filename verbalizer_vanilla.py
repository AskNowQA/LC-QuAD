'''
	Author: Priyansh Trivedi

	Script to verbalize the vanilla templates.
	Each template ID will have a different class.
		All extend the class created in verbalizer.py and edit it as per their requirements.

	Finally, a function will create an object of all of them and run it.
'''
import numpy as np
from pprint import pprint
from pattern.en import pluralize
import utils.natural_language_utilities as nlutils

import verbalizer
class Verbalizer_01(verbalizer.Verbalizer):

	template_id = 1
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = True
	question_templates = {
		
		'vanilla': 
			[ "%(prefix)s is the <%(uri)s> whose <%(e_to_e_out)s> is <%(e_out)s>?",
			"What <%(uri)s>'s <%(e_to_e_out)s> is <%(e_out)s>" ],

		'plural':
			[ "%(prefix)s are the <%(uri)s> whose <%(e_to_e_out)s> is <%(e_out)s>?",
			"What <%(uri)s>'s <%(e_to_e_out)s> is <%(e_out)s>" ]

	}

	def filter(self, _datum, _maps):
		#Just that hard filter thingy
		return self.hard_relation_filter(_maps['e_to_e_out'])

	def rules(self, _datum, _maps):
		'''
			Cardinality rule:
				If there are more than 3 answers to the URI, then use plural template. Otherwise use the singular template.

			Person rule:
				If the uri is a person, then change what to who.

		'''
		if _datum['answer_count']['uri'] > 3:
			#Plural rule
			try: 
				_maps['uri'] = pluralize(_maps['uri'])
			except:
				print "Cannot pluralize ", _maps['uri']

			question_format = np.random.choice(self.question_templates['plural'], p=[0.8,0.2])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'], p=[0.8,0.2])

		if 'http://dbpedia.org/ontology/Agent' in _datum['mapping_type']['uri'] and "http://dbpedia.org/ontology/Organisation" not in _datum['mapping_type']["uri"]:
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format





class Verbalizer_03(verbalizer.Verbalizer):

	template_id = 3
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = True
	has_uri = False
	question_templates = {
		'vanilla': ["What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"],
		'person': ["What is the <%(e_in_to_e)s> of the <%(x)s> who is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"]
	}

	def filter(self, _datum, _maps):
		#Just that hard filter thingy
		return self.hard_relation_filter(_maps['e_in_to_e'])

	def rules(self, _datum, _maps):
		'''
			Person Rule. If x has dbo:Agent but not have dbo:Organization.
				Have to check datum[mapping type] and  not maps
		'''
		if 'http://dbpedia.org/ontology/Agent' in _datum['mapping_type']['x'] and "http://dbpedia.org/ontology/Organisation" not in _datum['mapping_type']["x"]:
			question_format = np.random.choice(self.question_templates['person'])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'])

		return _maps, question_format


class Verbalizer_05(verbalizer.Verbalizer):

	template_id = 5
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = True
	has_uri = False
	question_templates = {
		'vanilla': { 
			'singular': 
				[ "What is the <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> ?" ],
			'plural': 
				[ "List the <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
				"What is the <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?" ]
		},

		'type': {
			'singular': 
				[ "What is the <%(e_in_to_e)s> of the <%(x)s> which is a <%(e_in_out)s> ?" ],
			'plural': 
				[ "List the <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>.", 
				"What is the <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>?" ]
		}
	}

	def filter(self, _datum, _maps):
		#Just that hard filter thingy
		return self.hard_relation_filter(_maps['e_in_to_e'])

	def rules(self, _datum, _maps):
		'''
			1. Normal Mode:
				1.a Cardinality:
					if there are more than #num of ?x, then stochastically select between a list and a what template.
					also pluralize ?x while doing this.
					p [list: 20%, vanilla: 80%]

			2. Type Mode:
				if e_in_to_e_in_out is type, use a type template
				2.a Cardinality. <same as above>

			Pseudocode:
				-> see if there are more than 2 ?x answers.
					-> yes?: see if the type rule is activated or not
						-> yes?: use type's plural template
						-> no?: use vanilla's plural template
					-> no?: see if type rule is activated
						-> yes? use type's singular
						-> no? vanilla's singular
		'''
		if len(_datum['answer']['x']) > 2:
			#Plural -> YES

			_maps['x'] = pluralize(_maps['x'])

			#Check for the type rule
			if _maps['e_in_to_e_in_out'].lower() == 'type':
				question_format = np.random.choice(self.question_templates['type']['plural'], p = [0.2,0.8])
			else:
				question_format = np.random.choice(self.question_templates['vanilla']['plural'], p = [0.2,0.8])

		else:
			#Plural -> NO

			#Check for the type rule
			if _maps['e_in_to_e_in_out'].lower() == 'type':
				question_format = np.random.choice(self.question_templates['type']['singular'])
			else:
				question_format = np.random.choice(self.question_templates['vanilla']['singular'])

		return _maps, question_format


class Verbalizer_06(verbalizer.Verbalizer):
	
	template_id = 6
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = True
	question_templates = {

		'vanilla': { 
			'singular': 
				["%(prefix)s is the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?"],
			'plural':
				[ "%(prefix)s are the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
				"List the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>." ]
			},

		'type': {
			'singular':
				[ "%(prefix)s is the <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?",
			   "%(prefix)s is the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?" ],
		   'plural': 
				[ "%(prefix)s are the <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?", 
				 "%(prefix)s are the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?",
				 "List the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?",
				 "List the <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?", ]
		}
	}

	def filter(self, _datum, _maps):
		return self.hard_relation_filter(_maps['e_to_e_out'])

	def rules(self, _datum, _maps):
		'''
			1. Singular Mode:  URI has less than three answers?
				1.a Vanilla Mode: if e_out_to_e_out_out is not 'type'?
					Select singular vanilla template.
				1.b Type Mode:	if e_out_to_e_out_out is 'type'?
					Select one of the singular plural template. Stochastically.
					p = 0.5, 0.5
			2. Plural mode
				2.a same as 1.a
					p = 0.8, 0.2
				2.b same as 1.b
					p = 0.4, 0.4, 0.1, 0.1

			<finally> if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.

			Pseudocode:
				-> see if there are more than 3 ?uri answers.
					-> yes?: see if the type rule is activated or not
						-> yes?: use type's plural template
						-> no?: use vanilla's plural template
					-> no?: see if type rule is activated
						-> yes? use type's singular
						-> no? vanilla's singular

				-> see if uri is person/people
					-> yes?: set maps's prefix to 'who'
					-> no?: set maps's preix to 'what'
		'''

		#Check for cardinality rule
		if len(_datum['answer']['uri']) > 3:
			#Plural -> YES

			_maps['uri'] = pluralize(_maps['uri'])

			#Check for the type rule
			if _maps['e_out_to_e_out_out'].lower() == 'type':
				question_format = np.random.choice(self.question_templates['type']['plural'], p = [0.4,0.4,0.1,0.1])
			else:
				question_format = np.random.choice(self.question_templates['vanilla']['plural'], p = [0.8,0.2])

		else:
			#Plural -> NO

			#Check for the type rule
			if _maps['e_out_to_e_out_out'].lower() == 'type':
				question_format = np.random.choice(self.question_templates['type']['singular'])
			else:
				question_format = np.random.choice(self.question_templates['vanilla']['singular'])

		#Check for the What/Who rule
		if _maps['uri'].lower() in ['people','person']:
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format


class Verbalizer_07(verbalizer.Verbalizer):
	template_id = 7
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = True
	question_templates = {

		'preposition': 
			["What is <%(e_to_e_out)s> <%(e_out_1)s> and <%(e_out_2)s>?"],

		'vanilla': {
			'singular': 
				[ "Whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?",
				"%(prefix)s is the <%(uri)s> whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?" ],
			'plural':
				[ "Whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?",
				"%(prefix)s are the <%(uri)s> whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?" ]
		}
	}

	def filter(self, _datum, _maps):
		return self.hard_relation_filter(_maps['e_to_e_out'])

	def rules(self, _datum, _maps):
		'''
			1. Preposition Rule: if e_to_e_out ends in a 'by'
				Select preposition template
			2. Singular/Plural rule:
				uri has less than or equal to 3 answers?
					stochastically select between the vanilla singular templates
					p = 0.25, 0.75
				uri has more than 3 answers?
					stochastically select between the vanilla plural templates
					p = 0.25, 0.75

			<finally> if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.			

			Pseudocode:
				-> see if the preposition rule is activated
					-> yes? use preposition template
					-> no? see if more than 3 ?uri answers
						-> yes? use vanilla's plural template
						-> no? use vanilla's singular template

				-> see if uri is person/people
					-> yes?: set maps's prefix to 'who'
					-> no?: set maps's preix to 'what'
		'''
		if _maps['e_to_e_out'].split()[-1].lower() == 'by':

			question_format = self.question_templates['preposition']

		else:

			#In this template, e_to_e_out needs to be plural.
			_maps['e_to_e_out'] = pluralize(_maps['e_to_e_out'])

			#Check for singular or plural ?uri
			if len(_datum['answer']['uri']) > 3:
				_maps['uri'] = pluralize(_maps['uri'])
				question_format = np.random.choice(self.question_templates['vanilla']['plural'], p=[0.25,0.75])
			else:
				question_format = np.random.choice(self.question_templates['vanilla']['singular'], p=[0.25,0.75])

		#Person Rule Condition: If the question has a 'What' as it's first word.    
		if _maps['uri'].lower() in ["person","people"]:
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format


class Verbalizer_08(verbalizer.Verbalizer):
	
	template_id = 8
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = True
	question_templates = {

		'vanilla': {
			'singular':
				["%(prefix)s is the <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?"],
			'plural':
				["%(prefix)s are the <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?"]
		},	

		'type': {

			'e_to_e_out_1': {
				'singular': 
					[ "%(prefix)s is the <%(uri)s> which is a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?" ],
				'plural': 
					[ "%(prefix)s are the <%(uri)s> which are a <%(e_out_1)s> and <%(e_to_e_out_2)s> is <%(e_out_2)s>?" ]
			},

			'e_to_e_out_2': {
				'singular': 
					[ "%(prefix)s is the <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which is a <%(e_out_2)s>?" ],
				'plural': 
					[ "%(prefix)s are the <%(uri)s> whose <%(e_to_e_out_1)s> is <%(e_out_1)s> and which are a <%(e_out_2)s>?" ]
			},

			'both': {
				'singular': 
					[ "%(prefix)s is the <%(uri)s> which is a <%(e_out_1)s> and a <%(e_out_2)s>?" ],	
				'plural': 
					[ "%(prefix)s are the <%(uri)s> which are a <%(e_out_1)s> and a <%(e_out_2)s>?" ]	
			}
		}
	}

	def filter(self, _datum, _maps):
		#@TODO: Discuss this filter
		return self.hard_relation_filter(_maps['e_to_e_out_1'])

	def rules(self, _datum, _maps):
		'''
			1. Type Rule (if either of the rel is a type, change the template appropriately)
				1.a R1 is type
					1.a.a Singular/Plural
				1.b R2 is type
					1.b.a Singular/Plural
				1.c both are type
					1.c.a Singular/Plural
			2. Vanilla Rule:
				if no type, use vanilla template
				2.a Singular/Plural

			<finally> if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.			

			Pseudocode:
				-> see if R1 and R2 are type:
					-> yes? is uri's answers more than 3?
						-> yes? use type's both's plural
						-> no? use type's both's singular
					-> no? see if R1 is type:
						-> yes? is uri's answers more than 3?
							-> yes? use type's e_to_e_out_1 template's plural version
							-> yes? use type's e_to_e_out_1 template's singular version
						-> no? see if R2 is a type:
							-> yes? is uri's answers more than 3?
								-> yes? use type's e_to_e_out_2 template's plural version
								-> no? use type's e_to_e_out_2 template's singular version
							-> no? is uri's answers more than 3?
								-> yes? use vanilla template's plural version
								-> no? use vanilla template's singular version

				-> see if uri is person/people
						-> yes?: set maps's prefix to 'who'
						-> no?: set maps's preix to 'what'
		'''

		#Checking for 'type' in the 'e_to_e_out_1'
		if _maps['e_to_e_out_1'].lower() == 'type' and _maps['e_to_e_out_2'].lower() == 'type':
			if len(_datum['answer']['uri']) > 3:
				#Plural
				_maps['uri'] = pluralize(_maps['uri'])
				question_format = np.random.choice(self.question_templates['type']['both']['plural'])
			else:
				#Singular
				question_format = np.random.choice(self.question_templates['type']['both']['singular'])
		elif _maps['e_to_e_out_1'].lower() == 'type':
			if len(_datum['answer']['uri']) > 3:
				#Plural
				_maps['uri'] = pluralize(_maps['uri'])
				question_format = np.random.choice(self.question_templates['type']['e_to_e_out_1']['plural'])
			else:
				#Singular
				question_format = np.random.choice(self.question_templates['type']['e_to_e_out_1']['singular'])
		elif _maps['e_to_e_out_2'].lower() == 'type':
			if len(_datum['answer']['uri']) > 3:
				#Plural
				_maps['uri'] = pluralize(_maps['uri'])
				question_format = np.random.choice(self.question_templates['type']['e_to_e_out_2']['plural'])
			else:
				#Singular
				question_format = np.random.choice(self.question_templates['type']['e_to_e_out_2']['singular'])
		else:
			if len(_datum['answer']['uri']) > 3:
				#Plural
				_maps['uri'] = pluralize(_maps['uri'])
				question_format = np.random.choice(self.question_templates['vanilla']['plural'])
			else:
				#Singular
				question_format = np.random.choice(self.question_templates['vanilla']['singular'])

		#Person Rule Condition: If the question has a 'What' as it's first word.    
		if _maps['uri'].lower() in ["person","people"]:
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format


class Verbalizer_09(verbalizer.Verbalizer):
	
	template_id = 9
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = True
	has_uri = True
	question_templates = {
		'vanilla': 
			[ "%(prefix)s is <%(e_in_to_e)s> of the <%(x)s> who is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s>" ],
	}

	def filter(self, _datum, _maps):
		return self.hard_relation_filter(_maps['e_in_to_e'])

	def rules(self, _datum, _maps):
		'''
			if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.			

			Pseudocode:
				-> see if uri is person/people
						-> yes?: set maps's prefix to 'who'
						-> no?: set maps's preix to 'what'
		'''

		question_format = np.random.choice(self.question_templates['vanilla'])

		if _maps['uri'].lower() == 'person':
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format

class Verbalizer_11(verbalizer.Verbalizer):

	template_id = 11
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = True
	has_uri = False
	question_templates = {
		'vanilla': 
			[ "List the other <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
			"What are the other <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>>" ],

		'type': 
			[ "List the other <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>.", 
			"What are the other <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>?" ]
		
	}

	def filter(self, _datum, _maps):
		#Specific to this template, if the answers to the query are less than or equal to two (or if too many answers), it won't make sense to pose this question.
		if _datum['answer_count']['uri'] <= 2 or _datum['answer_count']['uri'] > 10:
			return False

		#Just that hard filter thingy
		return self.hard_relation_filter(_maps['e_in_to_e'])

	def rules(self, _datum, _maps):
		'''
			1. Normal Mode:
	
			2. Type Mode:
				if e_in_to_e_in_out is type, use a type template

			Pseudocode:
				-> yes?: see if the type rule is activated or not
						-> yes?: use type's plural template
						-> no?: use vanilla's plural template
		'''

		_maps['x'] = pluralize(_maps['x'])

		#Check for the type rule
		if _maps['e_in_to_e_in_out'].lower() == 'type':
			question_format = np.random.choice(self.question_templates['type'], p = [0.2,0.8])
		else:
			question_format = np.random.choice(self.question_templates['vanilla'], p = [0.2,0.8])

		return _maps, question_format

class Verbalizer_15(verbalizer.Verbalizer):
	
	template_id = 15
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = True
	question_templates = {
		'vanilla': {
			'singular': [ "%(prefix)s is the <%(e_in_to_e)s> of the <%(e_in_1)s> and <%(e_in_2)s>" ],
			'plural': [ "%(prefix)s are the <%(e_in_to_e)s> of the <%(e_in_1)s> and <%(e_in_2)s>" ],
		}
	}

	def filter(self, _datum, _maps):
		return self.hard_relation_filter(_maps['e_in_to_e'])

	def rules(self, _datum, _maps):
		'''
			if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.			

			Pseudocode:
				-> see if uri is person/people
						-> yes?: set maps's prefix to 'who'
						-> no?: set maps's preix to 'what'
		'''
		if len(_datum['answer']['uri']) > 3:
			_maps['uri'] = pluralize(_maps['uri'])
			question_format = np.random.choice(self.question_templates['vanilla']['plural'])
		else:
			question_format = np.random.choice(self.question_templates['vanilla']['singular'])

		if _maps['uri'].lower() == 'person':
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format

class Verbalizer_16(verbalizer.Verbalizer):
	
	template_id = 16
	template_type = 'Vanilla'
	template_id_offset = 0
	has_x = False
	has_uri = True
	question_templates = {
		'vanilla': {
			'singular': 
				[ "%(prefix)s is the <%(e_in_to_e_1)s> of the <%(e_in_1)s> and <%(e_in_to_e_2)s> of the <%(e_in_2)s>" ],
			'plural': 
				[ "%(prefix)s are the <%(e_in_to_e_1)s> of the <%(e_in_1)s> and <%(e_in_to_e_2)s> of the <%(e_in_2)s>" ],
		}
	}

	def filter(self, _datum, _maps):
		return self.hard_relation_filter(_maps['e_in_to_e_1'])

	def rules(self, _datum, _maps):
		'''
			if type of URI is person, AND the question begins with 'what', change 'what' to 'who'.
			Cardinality check too!			

			Pseudocode:
				-> see if uri's answer is more than 3,
					-> yes?: use plural template
					-> no?: use singular template
				-> see if uri is person/people
						-> yes?: set maps's prefix to 'who'
						-> no?: set maps's preix to 'what'
		'''
		if len(_datum['answer']['uri']) > 3:
			_maps['uri'] = pluralize(_maps['uri'])
			question_format = np.random.choice(self.question_templates['vanilla']['plural'])
		else:
			question_format = np.random.choice(self.question_templates['vanilla']['singular'])

		if _maps['uri'].lower() in ['person','people']:
			_maps['prefix'] = 'Who'
		else:
			_maps['prefix'] = 'What'

		return _maps, question_format


if __name__ == "__main__":

	template1verbalizer = Verbalizer_01()
	template3verbalizer = Verbalizer_03()
	template5verbalizer = Verbalizer_05()
	template6verbalizer = Verbalizer_06()
	template7verbalizer = Verbalizer_07()
	template8verbalizer = Verbalizer_08()
	template9verbalizer = Verbalizer_09()
	template11verbalizer = Verbalizer_11()
	template15verbalizer = Verbalizer_15()
	template16verbalizer = Verbalizer_16()


		
