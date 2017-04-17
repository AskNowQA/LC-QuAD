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
    	data = {"verbalized_question":question["verbalized_question"],"json_content":str(pformat(question))}
    	response.set_cookie("question_id",question["_id"])
    	response.set_cookie("verbalized_question",question[u"verbalized_question"])
        return template('question.tpl',data)
    else:
        return "<p>Login failed. Please start from the index url</p>"

@get("/newquestion")
def new_question():
	print "here"
	if request.get_cookie('username') and request.get_cookie('template_id'):
		template_id = request.get_cookie('template_id')
		if request.get_cookie('number'):
			number = request.get_cookie('number')
			response.set_cookie('number', str(int(number) + 1))
		else:
			response.set_cookie('number', str(1))
		question = retriveQuestion(template_id)
    	if not question:
    		return "<p>All questions of template id is completed. Return to login page</p>"
    	#setting the question id as the cookie for state tracking
    	data = {"verbalized_question":question[u"verbalized_question"],"json_content":str(pformat(question))}
    	response.set_cookie("question_id",question["_id"])
    	response.set_cookie("verbalized_question",question[u"verbalized_question"])
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
				redirect("http://localhost:8080/newquestion")
			data = {u"username":username,u"corrected":"true",u"corrected_answer":corrected_answer }
			try:
				update_db(question_id,data)
				#rerout to the next url
				
			except:
				print traceback.print_exc()
				return "<p>Database error. Contact the admin.</p>"
			redirect("http://localhost:8080/newquestion")	
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

def retriveQuestion(template_id):
	'''connects to a database and retrives question based on template type'''
	question = posts.find_one({u"id":int(template_id),u"corrected" : u"false", u"verbalized":True})
	if question:
		return question
	else:
		return False

def retrive_question_id(_question_id):
	#retrives the question from database based on id
	question = posts.find_one({u"_id":int(_question_id)})

def update_db(_question_id,data):
	'''data must be a dictionary/json'''
	try:
		posts.update_one({u"_id":unicode(_question_id,"utf-8")},{"$set":data})
	except:
		print traceback.print_exc()
run(host='0.0.0.0', port=8080)