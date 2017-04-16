'''
	Author: Priyansh Trivedi

	Class: Verbalizer

	Since every template verbalizing was a little different, we started with individual scripts for each template. 
		However, there was a lot of code repetition and while changing anything, things could go really really bad. 

	This class is thus responsible for taking data from the output folder, and verbalizing it, based on what kind of template it is. 

'''

class Verbalizer:

	question_templates = {}		#Placeholder to keep all the templates here. In the form key: list, key:list

	def __init__(self, _template_id, _has_x = False, _has_uri = True, _template_id_offset = 0, _template_type = 'Vanilla'):
		'''
			Parameters:
				template_id: the template ID (corresponds to the file from where we pick sparqls. Corresponds to ID in templates.py)
				has_x: if the x (or x's type) has been generated and expected to be in the mapping. 
				has_uri: same for URI
				template type: vanilla (for not count/filter/ask), count, filter_a, filter_b, ask (@TODO: Add a reference of this on the Doc)
				template id offset: if it's a vanilla then 0, 100 for count... 

			-> Open the template file with this ID. Convert to [JSON,JSON..]
				-> Pass the JSON from the filter
				-> Select a template based on rules
				-> Put a map on the template to verbalize a question
			-> Write the JSONs to file
		'''

		sparqls = []			#Holds the un-verbalized data
		questions = []			#Holds the verbalized data

		with open('output/template%s.txt' % _template_id) as data_file:
			for line in data_file:
				sparqls.append(json.loads(line.rstrip('\n')))

				
		for counter in range(len(data)):

			#Declate the verbalized flag
			data[counter]['verbalized'] = False

			datum = data[counter]
			maps = datum["mapping"]

			if _has_uri:
				try:
					uri = datum["answer_type"]["uri"]
					maps["uri"] = uri
				except:
					continue

			if _has_x:
				try:
					x = datum["answer_type"]["x"]
					maps["x"] = x
				except:
					continue

			#See if you want this filtered
			if filter(_datum = datum, _maps = maps):
				#Don't bother verbalizing this
				continue

			#Select a template for this question
			maps, question_format = rules(_maps = maps,_datum = datum)

			data[counter]['verbalized_question'] = question_format % maps
			data[counter]['verbalized'] = True
			data[counter]['id'] = _template_id + _template_id_offset
			data[counter]['type'] = _template_type

		#Writing everything to file
		id = _template_id + _template_id_offset
		fo = open('output/verbalized_template%s.txt' % id, 'w+')
		for datum in data:
			if datum['verbalized'] == True:
    			fo.writelines(json.dumps(datum) + "\n")
		fo.close()

		questions = 0
		with open('output/verbalized_template%s_readable.txt' % id,'w+') as output_file:
    		for datum in data:
        		try:
            		output_file.write(datum['verbalized_question'].encode('utf-8')+'\n')
            		output_file.write(datum['query'].encode('utf-8')+'\n\n')
            		questions += 1
        		except:
            		continue

        #Count the number of verbalized questions
        print "Template ID: ", id
        print "Generated Questions: ", questions
		print "Total data items: ", len(data)

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
		'''

