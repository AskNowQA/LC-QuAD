# parsing code

import json
from pprint import pprint
import utils.natural_language_utilities as nlutils

import csv
def generate_CSV(questions):
    with open('mturk_upload_template_20.csv', 'w') as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=['question'])
        writer.writeheader()
        for question in questions:
            writer.writerow({
                'question': question.replace(">", "").replace("<","")})
data = []
with open('output/json_template20.txt') as data_file:
    for line in data_file:
        data.append(json.loads(line.rstrip('\n')))

questions = []
question_format = "How many <%(e_to_e_out)s> has the <%(e_in_to_e)s> of <%(e_in)s> ?"
# question_format2 = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"


e_in_to_e = {}
counter = 0
for filler in data:
    counter = counter + 1
    maps = filler['mapping']
    # print maps
    questions.append(question_format % maps)
for question in questions:
    print question

print "*******************"
print len(questions)
print counter
#
# with open('json_template3.txt') as file_handler:
# ...     for line in file_handler:
# ...             print line.rstrip('\n')
# ...             raw_input()
