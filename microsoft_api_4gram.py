
from pprint import pprint
import httplib, urllib, base64, traceback, json
import operator
# above, across, after, at,

# around, before, behind,

# below, beside, between,

# by, down, during, for, from,

# in, inside, onto, of,

# off, on, out, through,

# to, under, up, with
#list of R

#MACRO
slots = "*rel"

R = ['is', 'at', 'between', 'by', 'for', 'from', 'in', 'of', 'off', 'on', 'out', 'through','to','has','with','are',]


headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '5bc7ceb862c44d96a6b0f41df10cb826',
}

params = urllib.urlencode({
    # Request parameters
    'model': 'query',
    'order': '3',
})


def create_question(question):
	question = question.strip().split(" ")	#list of individual word of the sentence.
	
	no_of_rel = 0
	for x in question:
		if x == "*rel":
			no_of_rel = no_of_rel + 1

	starting_question = question		#[(question,probability)]

	
	questions = []
	for i in range(len(starting_question)-3):

		w,w_1,w_2,w_3 = starting_question[i:i+4]

		if len(questions) == 0:

			if not slots in [w,w_1,w_2,w_3]:
				questions = [ (0,[w,w_1,w_2,w_3]) ]
				continue
			else:
				triples = [(w,w_1,w_2,w_3)]
				if w == slots:
					new_triples = []
					for triple in triples:
						new_triples += [(x,triple[1],triple[2],triple[3]) for x in R]
					triples = new_triples
				if w_1 == slots:
					new_triples = []
					for triple in triples:
						new_triples += [(triple[0],x,triple[2],triple[3]) for x in R]
					triples = new_triples
				if w_2 == slots:
					new_triples = []
					for triple in triples:
						new_triples += [(triple[0],triple[1],x,triple[3]) for x in R]
					triples = new_triples
				if w_3 == slots:
					new_triples = []
					for triple in triples:
						new_triples += [(triple[0],triple[1],triple[3],x) for x in R]
					triples = new_triples

		else:
			if not slots in [w,w_1,w_2,w_3]:
				for i in range(len(questions)):
					questions[i][1].append(w_3)

				continue
			else:
				triples = [(w,w_1,w_2,w_3)]
				if w_3 == slots:
					new_triples = []
					for triple in triples:
						new_triples += [(triple[0],triple[1],triple[2],x) for x in R]
					triples = new_triples					



		# From this list of triples, find the most probable ones using MS API
		#Triple has [(w,w_1,w_2,w_3),(w,w_1,w_2,w_3),(w,w_1,w_2,w_3)...]
		triples_tuple = filter_triples(triples,limit=4)			#n=4 means four best triples

		#Triples are now [((w,w_1,w_2),p), (w,w_1,w_2),p) ...]
		#Now fit these triples back into the question and append these questions

		if len(questions) == 0:
			#Push the entire three words with probability
			for triple in triples_tuple:
				questions.append((triple[1], list(triple[0])))

			
		else:
			#Now just push the last word
			new_questions = []
			for q_i in range(len(questions)):
				q = questions.pop()
				#q = (-5,(w,w_1,w_2))

				for triple in triples_tuple:
					new_questions.append((q[0]+triple[1],q[1] + [triple[0][3]]))


			questions =  new_questions

		# #PRINTING THE SHIT
		# for q in questions:
		# 	print q
		# print "GO AGAIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

		# raw_input()




		
		
		# for each_question_tuple in probable_questions_backup:		
		# 	question = each_question_tuple[0]
		# 	probability = each_question_tuple[1]
		# 	for i in xrange(0,len(question)-2):
		# 		word1,word2,word3 = question[i:i+3]
				
		# 		#either of any word is rel then do some stuff
		# 		triples = [(word1,word2,word3)]


		# 		if not slots in [word1,word2,word3]:
		# 			continue
		# 		else:
		# 			if word1 == slots:
		# 				new_triples = []
		# 				for triple in triples:
		# 					new_triples += [(x,triple[1],triple[2]) for x in R ]
		# 				triples = new_triples
		# 			if word2 == slots:
		# 				new_triples = []
		# 				for triple in triples:
		# 					new_triples +=[(triple[0],x,triple[2]) for x in R ]
		# 				triples = new_triples
		# 			if word3 == slots:
		# 				new_triples = []
		# 				for triple in triples:
		# 					new_triples +=[(triple[0],triple[1],x) for x in R ]
		# 				triples = new_triples

		# 		#From this list of triples, find the most probable ones using MS API
		# 		#Triple has [(w,w_1,w_2),(w,w_1,w_2),(w,w_1,w_2)...]
		# 		triples_tuple = filter_triples(triples,limit=4)			#n=4 means four best triples

		# 		#Triples are now [((w,w_1,w_2),p), (w,w_1,w_2),p) ...]
		# 		#Now fit these triples back into the question and append these questions

		# 		prefix = question[:i]
		# 		suffix = question[i+3:]
		# 		new_question = []

		# 		for triple in triples_tuple:
		# 			p = triple[1]
		# 			tokens = triple[0]
		# 			new_question.append((prefix+tokens+suffix,probability+p))
		# 		print question
		# 		print "NEW QUESTION##################"
		# 		pprint(new_question)
		# 		raw_input()
		# 		#Replace that question with new questions
		# 		probable_questions += new_question 	

	return questions
		


def filter_triples(triples,limit):
	#converting tuple to string (not list)
	for x in xrange(0,len(triples)):
		triples[x] = " ".join(triples[x])
	#converting list to json for sending the request
	body = json.dumps({"queries" : triples })
	data = json.loads(send_request(body))
	results = data["results"]
	probability_dict = {}
	counter = 0
	for x in results:
		probability_dict[x['words']] = x['probability']
	sorted_x = sorted(probability_dict.items(), key=operator.itemgetter(1))
	limit = limit * -1

	sorted_x = sorted_x[limit:]
	results = []
	for x in sorted_x:
		results.append((x[0].split(),x[1]))
	
	return results












						

					



# body = json.dumps({"queries":[ "is birthplace of","of birthplace of","at birthplace of","from birthplace of","by birthplace of"]})


def send_request(body):
	try:
	    conn = httplib.HTTPSConnection('api.projectoxford.ai')
	    conn.request("POST", "/text/weblm/v1.0/calculateJointProbability?%s" % params, body, headers)
	    response = conn.getresponse()
	    data = response.read()
	    # print(data)
	    conn.close()
	    return data
	except Exception:
		print traceback.print_exc()

if __name__ == '__main__':
	# question = "Uganda *rel birth place *rel what person whose genre *rel Afro"
	question = 'rihanna *rel associated musical artist *rel what musical artist whose origin *rel cleveland ohio united states'
	answers = create_question(question)
	answers = sorted(answers, key=lambda x:x[0])

	for answer in answers[-7:]:
		print answer[1], answer[0]
