[{
	"template": " SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> } ",
	"id": 1,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri } ",
	"id": 2,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri, ?x WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri } ",
	"id": 3,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_out_in)s> <%(e_out_in_to_e_out)s> ?x . ?uri <%(e_to_e_out)s> ?x } ",
	"id": 4,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri, ?x WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri } ",
	"id": 5,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": "SELECT DISTINCT ?uri WHERE { ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x } ",
	"id": 6,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?uri <%(e_to_e_out)s> <%(e_out_1)s> . ?uri <%(e_to_e_out)s> <%(e_out_2)s>} ",
	"id": 7,
	"n_entities": 2,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out_1)s> <%(e_out_1)s> . ?uri <%(e_to_e_out_2)s> <%(e_out_2)s> } ",
	"id": 8,
	"n_entities": 2,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_in)s>  <%(e_in_in_to_e_in)s> ?x .  ?x <%(e_in_to_e)s> ?uri}",
	"id": 9,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(ent_a)s> <%(rel_from_a)s> ?x . ?uri <%(rel_from_a)s> ?x",
	"id": 10,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(rel_to_a)s> <%(ent_a)s> . ?x <%(rel_to_a)s> ?uri",
	"id": 11,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(rel_to_a)s> <%(ent_a)s> . ?x <%(rel_to_a)s> ?uri",
	"id": 12,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e_1)s> ?uri. <%(e_in)s> <%(e_in_to_e_2)s> ?uri}.",
	"id": 14,
	"n_entities": 2,
	"type": "vanilla"
}, {
	"template": "SELECT DISTINCT count(?uri) WHERE { <%(e_in)s> <%(e_in_to_e)s> <%(e)s> . <%(e)s> <%(e_to_e_out)s> ?uri }",
	"id": 20,
	"n_entities": 1,
	"type": "count"
}
]