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
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri } ",
	"id": 3,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri } ",
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
	"template": " SELECT DISTINCT ?uri WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri }",
	"id": 11,
	"n_entities": 1,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_1)s> <%(e_in_to_e)s> ?uri. <%(e_in_2)s> <%(e_in_to_e)s> ?uri} ",
	"id": 15,
	"n_entities": 2,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_1)s> <%(e_in_to_e_1)s> ?uri. <%(e_in_2)s> <%(e_in_to_e_2)s> ?uri} ",
	"id": 16,
	"n_entities": 2,
	"type": "vanilla"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> } ",
	"id": 101,
	"n_entities": 1,
	"type": "count"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri } ",
	"id": 102,
	"n_entities": 1,
	"type": "count"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri } ",
	"id": 103,
	"n_entities": 1,
	"type": "count"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri } ",
	"id": 105,
	"n_entities": 1,
	"type": "count"
}, {
	"template": "SELECT DISTINCT COUNT(?uri) WHERE { ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x } ",
	"id": 106,
	"n_entities": 1,
	"type": "count"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE { ?uri <%(e_to_e_out)s> <%(e_out_1)s> . ?uri <%(e_to_e_out)s> <%(e_out_2)s>} ",
	"id": 107,
	"n_entities": 2,
	"type": "count"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE {?uri <%(e_to_e_out_1)s> <%(e_out_1)s> . ?uri <%(e_to_e_out_2)s> <%(e_out_2)s> } ",
	"id": 108,
	"n_entities": 2,
	"type": "count"
}, {
	"template": " SELECT DISTINCT COUNT(?uri) WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri }",
	"id": 111,
	"n_entities": 1,
	"type": "count"
}, {
	"template": "ASK WHERE { <%(uri)s> <%(e_to_e_out)s> <%(e_out)s> }",
	"id": 151,
	"n_entities": 1,
	"type": "ask"
}, {
	"template": "ASK WHERE { <%(e_in)s> <%(e_in_to_e)s> <%(uri)s> }",
	"id": 152,
	"n_entities": 1,
	"type": "ask"
}
]