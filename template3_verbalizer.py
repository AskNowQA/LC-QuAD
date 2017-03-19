# parsing code

import json
from pprint import pprint
import utils.natural_language_utilities as nlutils

with open('output/template3.json') as data_file:
    data = json.load(data_file)
questions = []
question_format = "What is the <%(e_in_to_e)s> of the <%(x)s> who is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"
question_format2 = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"
for filler in data:
    x = filler["answer_type"]['x']
    maps = filler['mapping']
    maps['x'] = x
    # replace each path by label
    for element in maps:
        maps[element] = nlutils.get_label_via_parsing(maps[element])  # obtain just elements.
    questions.append(question_format % maps)

for question in questions:
    print question

print "*******************"
print len(questions)
