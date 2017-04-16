'''
	Author: Priyansh Trivedi

	Script to verbalize the vanilla templates.
	Each template ID will have a different class.
		All extent the class created in verbalizer.py and edit it as per their requirements.

	Finally, a function will create an object of all of them and run it.
'''
import numpy as np
from pprint import pprint
from pattern.en import pluralize
import utils.natural_language_utilities as nlutils

import verbalizer

class Verbalizer_03(verbalizer.Verbalizer):

	question_templates = {
		'vanilla': ["What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"],
		'person': ["What is the <%(e_in_to_e)s> of the <%(x)s> who is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"]
		}

	def filter(self, _datum, _maps):
		#Just that hard filter thingy
		return self.hard_relation_filter(_maps['e_in_to_e'])

	def rules(self, _maps, _datum):
		'''
			Person Rule. If x has dbo:Agent but not have dbo:Organization.
				Have to check datum[mapping type] and  not maps
		'''
		if 'http://dbpedia.org/ontology/Agent' in _datum['mapping_type']['x'] and "http://dbpedia.org/ontology/Organisation" not in _datum['mapping_type']["x"]:
			return _maps, np.random.choice(self.question_templates['person'])
		else:
			return _maps, np.random.choice(self.question_templates['vanilla'])


if __name__ == "__main__":

	template3verbalizer = Verbalizer_03(_template_id = 3, _has_x = True, _template_id_offset = 0, _template_type = "Vanilla")


		
