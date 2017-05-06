import utils.dbpedia_interface as db_interface
import utils.natural_language_utilities as nlutils

# ent_parent = 
dbp = db_interface.DBPedia(_verbose=True)
entity = open('resources/entity_classes.txt').read().split('\n') #Contains whitelisted entities classes


for x in entity:
	entity_set.append(dbp.get_most_specific_class(x))
