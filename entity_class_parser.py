''' A script for parsing the entity_classes.txt and returning a list of classes '''
import random
import utils.dbpedia_interface as db_interface
import traceback
from pprint import pprint

dbp = db_interface.DBPedia(_verbose=True)

with open("resources/classes.txt") as f:
    contents = f.readlines()

clean_contents = []

for content in contents:
    cont = content.strip().replace("\n","")
    if cont:
        clean_contents.append(cont)
# print clean_contents
entity_list = []
for con in clean_contents:
    try:
        if con:
            uri = "http://dbpedia.org/ontology/" + con
            entites = dbp.get_entities_of_class(uri)
            if entites:
                entity = random.sample(entites,1)
                print entity
                entity_list.append(entity[0])
    except:
        print traceback.print_exc()

file = open('entity.txt', 'a+')
for entity in entity_list:
    temp = entity + "\n"
    file.write(temp)
pprint(entity_list)
file.close()