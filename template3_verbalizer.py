# parsing code

import json
from pprint import pprint
import utils.natural_language_utilities as nlutils

import csv
def generate_CSV(questions):
    with open('mturk_upload.csv', 'w') as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=['question'])
        writer.writeheader()
        for question in questions:
            writer.writerow({
                'question': question.replace(">", "").replace("<","")})

with open('output/template3.json') as data_file:
    data = json.load(data_file)

questions = []
question_format = "What is the <%(e_in_to_e)s> of the <%(x)s> who is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"
question_format2 = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"


e_in_to_e = {}
counter = 0
for filler in data:
    counter = counter + 1
    x = filler["answer_type"]['x']
    maps = filler['mapping']
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
    if "http://dbpedia.org/ontology/Agent" in filler['mapping_type']["x"] and "http://dbpedia.org/ontology/Organisation" not in filler['mapping_type']["x"]:
        questions.append(question_format % maps)
    else:
        questions.append(question_format2 % maps)

for question in questions:
    print question

print "*******************"
print len(questions)
print counter