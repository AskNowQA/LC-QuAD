import csv
import json
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
with open('output/json_template5.txt') as data_file:
    for line in data_file:
        data.append(json.loads(line.rstrip('\n')))

questions = []      #Variable to keep all the verbalized questions
vanilla_template_singular = "What is the <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> ?"
vanilla_template_plural = "List the <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>."
type_template_singular = "What is the <%(e_in_to_e)s> of the <%(x)s> which is a <%(e_in_out)s> ?"
type_template_plural = "List the <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>."
# question_format2 = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"

e_in_to_e = {}
counter = 0

#The process of verbalizing starts here
for filler in data:
    counter = counter + 1

    #Get intermediate var
    try:
        x = filler["answer_type"]['x']
    except:
        continue

    #Get the entire mapping dict
    maps = filler['mapping']
    maps['x'] = x

    #What does this block do?
        #Its a limitation on the generation where we only generate one question per relation. 
        #Not sure why this filters out the bad questions but god it does!
    try:
        if e_in_to_e[maps['e_in_to_e']] > 0:
            continue
        e_in_to_e[maps['e_in_to_e']] = e_in_to_e[maps['e_in_to_e']] + 1
    except:
        e_in_to_e[maps['e_in_to_e']] = 1



    #@TODO: Instead of parsing them, have a hashmap to retrieve all labels from DBPedia
    for element in maps:
        maps[element] = nlutils.get_label_via_parsing(maps[element])  #Get their labels

    ''' 
        ### RULES ###
        1. List Rule:
            if there are more than one ?x, then use a list template. Also pluralize ?x's token
        2. Type Rule:
            if e_in_to_e_in_out is 'type', use a type template (singular or plural)
    '''    
    
    #Check if singular or plural
    if len(filler['answer']['x']) > 2:
        #Plural
        maps['x'] = pluralize(maps['x'])

        #Check for the type rule
        if maps['e_in_to_e_in_out'] == 'type':
            question_format = type_template_plural

        else:
            question_format = vanilla_template_plural
    else:
        #Singular

        #Check for the type rule
        if maps['e_in_to_e_in_out'] == 'type':
            question_format = type_template_singular

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

with open('output/verbalized_template5.txt','w+') as output_file:
    for question in questions:
        output_file.write(question[0].encode('utf-8')+'\n')
        output_file.write(question[1].encode('utf-8')+'\n\n')


