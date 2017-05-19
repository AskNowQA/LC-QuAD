'''The central server and orchestrator for the turk job.'''

from bottle import route, run, template, get, post, request, response, static_file, redirect
import pymongo, traceback
from pymongo import MongoClient
from pprint import pprint
from pprint import pformat
#database conneections 
client = MongoClient('localhost', 27017)
db = client.document_database
posts = db.posts

# intermediate_dict = {1:"uri",2:"uri",3:"",4}

intermediate_dict = {
	1:'uri',
	2:'uri',
	3:'x',
	4:'x',
	5:'uri',
	6:'uri',
	7:'uri',
	8:'uri',
	9:'x',
	11:'x',
	15:'uri',
	16:'uri',
	101:'uri',
	102:'uri',
	103:'x',
	104:'x',
	105:'uri',
	106:'uri',
	107:'uri',
	108:'uri',
	109:'x',
	111:'x',
	115:'uri',
	116:'uri',
}

@get('/static/<filename>')
def server_static(filename):
	print filename
	return static_file(filename, root='static')

@get('/')
def index():
#Displays a HTML page for the tempalte the user wants to work with.
#Submits to a webpage which will display the generated question.
    return ''' 
    		<form action="/question" method="post">
            TempalteId: <input name="template_id" type="text" />
            username: <input name="username" type="text" />
            <input value="Enter" type="submit" />
        	</form>
    	'''

@post('/question') # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    template_id = request.forms.get('template_id')
    if username and template_id:
    	#set cookies and other meta data.
    	response.set_cookie("username",username)
    	response.set_cookie("template_id",template_id)
    	#query for a question from the database. 
    	question = retriveQuestion(template_id)
    	if not question:
    		return "<p>All questions of template id is completed. Return to login page</p>"
    	#setting the question id as the cookie for state tracking
    	data = {"verbalized_question":question["verbalized_question"],"json_content":str(pformat(question)),"number":1,"verbalized_question_removed":question[u"verbalized_question"].replace("<","").replace(">","")}
    	response.set_cookie("question_id",question["_id"])
    	print question[u"verbalized_question"]
    	response.set_cookie("verbalized_question",question[u"verbalized_question"].encode('utf-8'))
    	response.set_cookie('number', str(0))
        return template('question.tpl',data)
    else:
        return "<p>Login failed. Please start from the index url</p>"

@get("/newquestion")
def new_question():
	if request.get_cookie('username') and request.get_cookie('template_id'):
		template_id = request.get_cookie('template_id')
		if request.get_cookie('number'):
			number = request.get_cookie('number')
			response.set_cookie('number', str(int(number) + 1))
			print number
		else:
			response.set_cookie('number', str(1))
			number = 1
		question = retriveQuestion(template_id)
		if not question:
			print "am I here? where gaurav pooped?"
			return "<p>All questions of template id is completed. Return to login page</p>"
    	#setting the question id as the cookie for state tracking
    	data = {"verbalized_question":question[u"verbalized_question"],"json_content":str(pformat(question)),"number":number,"verbalized_question_removed":question[u"verbalized_question"].replace("<","").replace(">","")}
    	response.set_cookie("question_id",question["_id"])
    	response.set_cookie("verbalized_question",question[u"verbalized_question"].encode('utf-8'))
        return template('question.tpl',data)		

@post('/submitQuestion')
def submit_question():
	if request.get_cookie('username') and request.get_cookie('template_id') and request.get_cookie('question_id'):
		#parse the form for answer
		corrected_answer = request.forms.get("corrected_answer")
		if corrected_answer:
			username = request.get_cookie('username')
			template_id = request.get_cookie('template_id')
			question_id = request.get_cookie('question_id')
			if corrected_answer == request.get_cookie('verbalized_question'):
				print "chutiya user"
				redirect("/newquestion")
			data = {u"username":username,u"corrected":"true",u"corrected_answer":corrected_answer }
			try:
				update_db(question_id,data)
				#rerout to the next url
				
			except:
				print traceback.print_exc()
				return "<p>Database error. Contact the admin.</p>"
			redirect("/newquestion")	
	else:
		return "<p>Login failed. Please start from the index url</p>"

@post('/deleteQuestion')		
def delete_question():
	if request.get_cookie('username') and request.get_cookie('template_id') and request.get_cookie('question_id'):
		#parse the form for answer
		corrected_answer = request.forms.get("corrected_answer")
		username = request.get_cookie('username')
		template_id = request.get_cookie('template_id')
		question_id = request.get_cookie('question_id')
		data = {u"username":username,u"corrected":"true",u"corrected_answer":corrected_answer,u"delete":"true" }
		try:
			update_db(question_id,data)
			#rerout to the next url
		except:
			print traceback.print_exc()
			return "<p>Database error. Contact the admin.</p>"
		redirect("/newquestion")

@get('/checkquestion')
def check_question():
	#retrive a pecific question from the database
	if request.get_cookie('username') and request.get_cookie('template_id'):
		template_id = request.get_cookie('template_id')
		if request.get_cookie('number'):
			number = request.get_cookie('number')
			response.set_cookie('number', str(int(number) + 1))
			print number
		else:
			response.set_cookie('number', str(1))
			number = 1
		question = retriveCorrectedQuestion(template_id)
		#now do all the formating to return the list of possible additions

		if not question:
			print "am I here? where gaurav pooped?"
			return "<p>All questions of template id is completed. Return to login page</p>"
		checklist = create_checklist(question)
		# print type(checklist)
    	if not checklist:
			checklist = ["things"]
    	data = {"verbalized_question":question[u"verbalized_question"],"json_content":str(pformat(question)),"number":number,"verbalized_question_removed":question[u"verbalized_question"].replace("<","").replace(">",""),"checklist":checklist,u"corrected_answer":question[u"corrected_answer"]}
    	response.set_cookie("question_id",question["_id"])
    	response.set_cookie("verbalized_question",question[u"verbalized_question"].encode('utf-8'))
        return template('question_correcter.tpl',data)
# 	#Correct its form 
# 	#and then add it back to the tempalkte 

@post('/checkquestion')
def post_check_question():
	if request.get_cookie('username') and request.get_cookie('template_id') and request.get_cookie('question_id'):
		print "here"
		reviewed_answer = request.forms.get("reviewed_answer")
		username = request.get_cookie('username')
		template_id = request.get_cookie('template_id')
		question_id = request.get_cookie('question_id')
		checked_list = request.forms.getlist('checked_list')
		new_corrected_question = request.forms.get('corrected_answer')
		# print checked_list
		#also add question

		#Now this has all the list which have been checked.
		#Update the sparql query accordingly 
		question = retriveQuestionById(question_id)
		updated_sparql = add_domain_restrictions(question["query"],checked_list,template_id)
		print "here"
		if not checked_list:
			data = {u'updated_query':updated_sparql,u"reviewed_question":new_corrected_question,u"reviewed":True}
			# print data
		else:
			data = {u'updated_query':updated_sparql,u"reviewed_question":new_corrected_question,u"reviewed":True,u"id":int(question[u"id"])+300}	
		# raw_input()
		pprint(data)
		try:
			update_db(question_id,data)
			#rerout to the next url
		except:
			print traceback.print_exc()
			return "<p>Database error. Contact the admin. Pull commit push run !!</p>"
		redirect("/checkquestion")

def retriveQuestion(template_id):
	'''connects to a database and retrives question based on template type'''
	question = posts.find_one({u"id":int(template_id),u"corrected" : u"false", u"verbalized":True})
	# print "***", question
	if question:
		return question
	else:
		return False

def retrive_question_id(_question_id):
	#retrives the question from database based on id
	question = posts.find_one({u"_id":int(_question_id)})

# def retriveCorrectedQuestion(template_id):

def update_db(_question_id,data):
	'''data must be a dictionary/json'''
	try:
		posts.update_one({u"_id":unicode(_question_id,"utf-8")},{"$set":data})
	except:
		print traceback.print_exc()


def retriveCorrectedQuestion(template_id):
	#reviewed:false has to be added to the database.
	question = posts.find_one({u"id":int(template_id),u"corrected" : u"true", u"verbalized":True,u"reviewed":False,u"delete":{"$exists":False}})
	# print "***", question
	if question:
		return question
	else:
		return False

def create_checklist(question):
	# pprint(question)
	tID = question[u"id"]
	querykeyWord = intermediate_dict[tID]
	# print querykeyWord
	# print question["mapping_type"][querykeyWord]
	# raw_input()
	return question["mapping_type"][querykeyWord]

def retriveQuestionById(_id):
	question = posts.find_one({u"_id":_id})
	# print "***", question
	if question:
		return question
	else:
		return False

def add_domain_restrictions(query,classes,tempalte_id):
	# print query
	# print classes
	# raw_input()
	var = '?' + intermediate_dict[int(tempalte_id)]	#If there is only one class
	if (classes.__class__ == [].__class__ and len(classes) == 1) or classes.__class__ == ''.__class__:

		if classes.__class__ == [].__class__:
			classes = classes[0]

		#Form the triple
		triple = ' . ' + var + ' rdf:type ' + "<"+classes + ">"

	else:

		#Form individual triples
		triples = []
		for cls in classes:
			triple = var + ' rdf:type ' + "<"+cls+">"
			triples.append(triple)

		triple = ' . '.join(triples)
		triple = ' . '+ triple

	#Appending this triple in the query
	if query.strip()[-1] == '}':

		query = query.strip()
		query = query[:-1] + triple + '}'
	# print query
	# raw_input()	
	return query			

run(host='0.0.0.0', port=8000)