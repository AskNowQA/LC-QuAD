import csv
import json
import numpy as np
from pprint import pprint
from pattern.en import pluralize
import utils.natural_language_utilities as nlutils

def generate_CSV(questions):
    with open('mturk_upload.csv', 'w') as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=['question'])
        writer.writeheader()
        for question in questions:
            writer.writerow({
                'question': question.replace(">", "").replace("<","")})

data = []           #Variable to keep all the unverbalized queries

#Read from the file and fill the data variable
with open('output/json_template6.txt') as data_file:
    for line in data_file:
        data.append(json.loads(line.rstrip('\n')))

questions = []      #Variable to keep all the verbalized questions
vanilla_template_singular = "What is the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?"
vanilla_template_plural = [ "What are the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
                            "List the <%(uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>."]
type_template_singular = [ "What is the <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?",
                           "What is the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?" ]
type_template_plural = [ "What are the <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?", 
                         "What are the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?",
                         "List the <%(uri)s> whose <%(e_to_e_out)s> is a <%(e_out_out)s>?",
                         "List the <%(uri)s> whose <%(e_to_e_out)s> is a kind of a <%(e_out_out)s>?", ]
e_to_e_out = {}
counter = 0

#The process of verbalizing starts here
for filler in data:
    counter = counter + 1

    #Get type of answer
    try:
        uri = filler["answer_type"]['uri']
    except:
        continue

    #Get the entire mapping dict
    maps = filler['mapping']
    maps['uri'] = uri

    #What does this block do?
        #Its a limitation on the generation where we only generate one question per relation. 
        #Not sure why this filters out the bad questions but god it does!
    try:
        if e_to_e_out[maps['e_to_e_out']] > 0:
            continue
        e_to_e_out[maps['e_to_e_out']] = e_to_e_out[maps['e_to_e_out']] + 1
    except:
        e_to_e_out[maps['e_to_e_out']] = 1

    #@TODO: Instead of parsing them, have a hashmap to retrieve all labels from DBPedia
    for element in maps:
        maps[element] = nlutils.get_label_via_parsing(maps[element], lower = True)  #Get their labels

    '''
        ### RULES ###
        1. Plural Rule:
            If there are multiple answers to the question (say more than 4), then use plural form of the question.
        2. Type Rule

        In 3 of these four cases, we select a template stochiastically. Details must be inferred from the code below
    '''


    if len(filler['answer']['uri']) > 3:
        #Plural
        maps['uri'] = pluralize(maps['uri'])

        #Type rule check
        if maps['e_out_to_e_out_out'] == 'type':
            question_format = np.random.choice(type_template_plural, p = [0.4,0.4, 0.1,0.1])
        else: 
            question_format = np.random.choice(vanilla_template_plural, p = [0.8, 0.2])

    else:
        #Singular

        #Type rule check
        if maps['e_out_to_e_out_out'] == 'type':
            question_format = np.random.choice(type_template_singular)
        else:
            question_format = vanilla_template_singular

    #All barriers in place, and all variables collected. Now let's verbalize (put the mapping in the tempates)
    questions.append(( filler[u'query'], question_format % maps ))

for question in questions:
    print question

print "*******************"
print "Generated Questions: ", len(questions)
print "Total data items: ", counter

#Writing them to a file

with open('output/verbalized_template6.txt','w+') as output_file:
    for question in questions:
        output_file.write(question[0].encode('utf-8')+'\n')
        output_file.write(question[1].encode('utf-8')+'\n\n')


