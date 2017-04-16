import csv
import json
import numpy as np
from pprint import pprint
from pattern.en import pluralize
import utils.natural_language_utilities as nlutils

data = []           #Variable to keep all the unverbalized queries

#Read from the file and fill the data variable
with open('output/json_template5.txt') as data_file:
    for line in data_file:
        data.append(json.loads(line.rstrip('\n')))

vanilla_template_singular = "What is the total number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s> ?"
vanilla_template_plural = ["List the total number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.","What is the total number of <%(e_in_to_e)s> of the <%(x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>."]
type_template_singular = "What is the total number of <%(e_in_to_e)s> of the <%(x)s> which is a <%(e_in_out)s> ?"
type_template_plural = ["List the total number of <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>.","What is the total number of <%(e_in_to_e)s> of the <%(x)s> which are <%(e_in_out)s>."]

e_in_to_e = {}

#The process of verbalizing starts here
for counter in range(len(data)):
    #Declare verbalization flag
    data[counter]['verbalized'] = False

    filler = data[counter]

    #Get intermediate var
    try:
        x = filler["answer_type"]['x']
    except:
        continue

    #Get the entire mapping dict
    maps = filler['mapping']
    maps['x'] = x

    '''
        !!!! FILTERS !!!!
        -> The typical more than a rel filter
        -> If the count variable is true
    '''
    
    if data[counter]["countable"] != "true":
        continue

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
        maps[element] = nlutils.get_label_via_parsing(maps[element],lower = True)  #Get their labels

    ''' 
        ### RULES ###
        1. List Rule:
            if there are more than one ?x, then use a list template. Also pluralize ?x's token
             -> use list template only 20% of the time. use 'what is the' rest of the times.
        2. Type Rule:
            if e_in_to_e_in_out is 'type', use a type template (singular or plural)
    '''    
    #Check if singular or plural
    if len(filler['answer']['x']) > 2:
        #Plural
        maps['x'] = pluralize(maps['x'])

        #Check for the type rule
        if maps['e_in_to_e_in_out'] == 'type':
            question_format = np.random.choice(type_template_plural, p = [0.2,0.8])

        else:
            question_format = np.random.choice(vanilla_template_plural, p = [0.2,0.8])
    else:
        #Singular

        #Check for the type rule
        if maps['e_in_to_e_in_out'] == 'type':
            question_format = type_template_singular

        else:
            question_format = vanilla_template_singular

    #All barriers in place, and all variables collected. Now let's verbalize (put the mapping in the tempates), and put it back in the data variable
    data[counter]['verbalized_question'] =  question_format % maps
    data[counter]['verbalized'] = True             #Since the question is now verbalized, we can set the flag to true.

#Writing them to a file
fo = open('output/verbalized_template5_count.txt', 'w+')
for key in data:
    fo.writelines(json.dumps(key) + "\n")
fo.close()

questions = 0
with open('output/verbalized_template5_count_readable.txt','w+') as output_file:
    for datum in data:
        try:
            output_file.write(datum['verbalized_question'].encode('utf-8')+'\n')
            output_file.write(datum['query'].encode('utf-8')+'\n\n')
            questions += 1
        except:
            continue

        #Count the number of verbalized questions

# for question in questions:
#     print question

print "Generated Questions: ", questions
print "Total data items: ", len(data)
