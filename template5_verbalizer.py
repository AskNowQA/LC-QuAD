import csv
import json
from pprint import pprint
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
question_format = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_to_e_in_out)s> of <%(e_in_out)s> ?"
# question_format2 = "What is the <%(e_in_to_e)s> of the <%(x)s> which is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s> ?"

e_in_to_e = {}
counter = 0

#The process of verbalizing starts here
for filler in data:
    counter = counter + 1

    #Get intermediate var
    #DEBUG
    try:
        x = filler["answer_type"]['x']
    except:
        continue
    #Get the entire mapping dict
    maps = filler['mapping']
    #Push the intermediate var in the dict
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

    for element in maps:
        #@TODO: Instead of parsing them, have a hashmap to retrieve all labels from DBPedia
        maps[element] = nlutils.get_label_via_parsing(maps[element])  #Get their labels
        
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


