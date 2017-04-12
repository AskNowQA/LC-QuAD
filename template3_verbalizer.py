# parsing code

import json
from pprint import pprint
import utils.natural_language_utilities as nlutils


data = []
#read from the file
with open('output/json_template3.txt') as data_file:
    for line in data_file:
        data.append(json.loads(line.rstrip('\n')))

question_format = "What is the <%(e_in_to_e)s> of the <%(x)s> who is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"
question_format2 = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"

e_in_to_e = {}

for counter in range(len(data)):
    data[counter]['verbalized'] = False

    datum = data[counter]

    x = datum["answer_type"]['x']
    maps = datum['mapping']
    maps['x'] = x

    try:
        if e_in_to_e[maps['e_in_to_e']] > 0:
            continue
        e_in_to_e[maps['e_in_to_e']] = e_in_to_e[maps['e_in_to_e']] + 1
    except:
        e_in_to_e[maps['e_in_to_e']] = 1
    
    # replace each path by label
    for element in maps:
        maps[element] = nlutils.get_label_via_parsing(maps[element])  # obtain just elements.
    if "http://dbpedia.org/ontology/Agent" in datum['mapping_type']["x"] and "http://dbpedia.org/ontology/Organisation" not in datum['mapping_type']["x"]:
        data[counter]['verbalized_question'] = question_format % maps
        data[counter]['verbalized'] = True
    else:
        data[counter]['verbalized_question'] = question_format2 % maps
        data[counter]['verbalized'] = True

#Writing them to a file
fo = open('output/verbalized_template3.txt', 'w+')
for key in data:
    fo.writelines(json.dumps(key) + "\n")
fo.close()

questions = 0
with open('output/verbalized_template3_readable.txt','w+') as output_file:
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
print "Total data items: ", counter
