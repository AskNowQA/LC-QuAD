[{
	"template": " SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> } ",
	"id": 1,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri } ",
	"id": 2,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri } ",
	"id": 3,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_out_in)s> <%(e_out_in_to_e_out)s> ?x . ?uri <%(e_to_e_out)s> ?x } ",
	"id": 4,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(rel_to_a)s> <%(ent_a)s> . ?x <%(rel_from_x)s> ?uri } ",
	"id": 5,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(rel_to_a)s> <%(ent_a)s> . ?uri <%(rel_to_x)s> ?x } ",
	"id": 6,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?uri <%(rel_to_a)s> <%(ent_a)s> . ?uri <%(rel_to_a_and_b)s> <%(ent_b)s> } ",
	"id": 7,
	"n_entities": 2
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?uri <%(rel_to_a)s> <%(ent_a)s> . ?uri <%(rel_to_b)s> <%(ent_b)s> } ",
	"id": 8,
	"n_entities": 2
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(ent_a)s> <%(rel_from_a)s> ?x . ?x <%(rel_from_a)s> ?uri",
	"id": 9,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(ent_a)s> <%(rel_from_a)s> ?x . ?uri <%(rel_from_a)s> ?x",
	"id": 10,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(rel_to_a)s> <%(ent_a)s> . ?x <%(rel_to_a)s> ?uri",
	"id": 11,
	"n_entities": 1
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(rel_to_a)s> <%(ent_a)s> . ?x <%(rel_to_a)s> ?uri",
	"id": 12,
	"n_entities": 1
}]