'''The central server and orchestrator for the turk job.'''

from bottle import route, run, template, get, post, request, response, static_file
import pymongo
from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.question_test_database
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
        return template('question.tpl')
    else:
        return "<p>Login failed. Please start from the index url</p>"

def retriveQuestion(template_id):
	'''connects to a database and retrives question based on template type'''
	question = posts.find_one({"template_id": template_id,"corrected" : "false"})
	return question

run(host='localhost', port=8080)