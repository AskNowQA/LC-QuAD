import csv
import json
import numpy as np
from pprint import pprint
from pattern.en import pluralize
import utils.natural_language_utilities as nlutils

data = []           #Variable to keep all the unverbalized queries

#Read from the file and fill the data variable
with open('output/json_template7.txt') as data_file:
    for line in data_file:
        data.append(json.loads(line.rstrip('\n')))

vanilla_template = "Whose <%(e_to_e_out)s> are <%(e_out_1)s> and <%(e_out_2)s>?"
preposition_template = "What is <%(e_to_e_out)s> <%(e_out_1)s> and <%(e_out_2)s>?"

e_to_e_out = {}
counter = 0

#The process of verbalizing starts here
for counter in range(len(data)):
    #Declaring verbalization flag
    data[counter]['verbalized'] = False

    datum = data[counter]

    #Get type of answer
    try:
        uri = datum["answer_type"]['uri']
    except:
        continue

    #Get the entire mapping dict
    maps = datum['mapping']
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
        1. Preposition Rule
            If the e_to_e_out ends in a by, use a different template
    '''

    #Check for the preposition rule
    if maps['e_to_e_out'].split()[-1] == 'by':
        question_format = preposition_template
    else:
        question_format = vanilla_template

    #All barriers in place, and all variables collected. Now let's verbalize (put the mapping in the tempates)
    data[counter]['verbalized_question'] = question_format % maps
    data[counter]['verbalized'] = True             #Since the question is now verbalized, we can set the flag to true.

#Writing them to a file
fo = open('output/verbalized_template7.txt', 'w+')
for key in data:
    fo.writelines(json.dumps(key) + "\n")
fo.close()

questions = 0
with open('output/verbalized_template7_readable.txt','w+') as output_file:
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

