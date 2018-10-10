# Logic for Templates

## ID Nomenclature:
- **1-16**: Normal SPARQL templates. Use old-school string formatting to sub uris in there. (NO SHORTHAND) 
No count/rdf-type constraint. See [this google doc](https://docs.google.com/document/d/1N4KRy_xMD7B5cAnQWMiytRrPkZ-HwIEiZj4PbI-xROM/edit?usp=sharing) to understand each of them.
- **+50**: A boolean (`ASK`) counterpart of the query instead of `SELECT`.
- **+100**: Additional count aggregate on the answer
- **+300**: Additional rdf:type constraint on either answer or intermediate entities.

## Term Nomenclature:

![Nomenclature of terms in the SPARQL][logo]

[logo]: resources/nomenclature.png "Nomenclature.png"

## Mapping Logic

Explanation for terms not in the image.

- **?uri**: The answer of any SPARQL query (`e` in image above).
- **?x**: The entities which satisfy the intermediate triple in our SPARQLs (typically `e_in` or `e_out`).
- **class_x/class_uri**: The DBpedia class that the ?uri or ?x variable must belong to.
- **equal** key: If a template has this key, and a corresponding list, the elements of that list should have the same value.

    E.g. if `"equal": ["e_in_to_e_in_out", "e_in_to_e"]`, then both of the predicates must be the same. For instance, `dbo:Father`.
- \<predicate\>**_2**: Another **predicate** which sits at the same position.

    E.g. if `e=dbo:Germany` and `e_to_e_out=dbp:population`, a possible `e_to_e_out_2` can be `dbo:language`. 
- \<entity\>**_2**: Another **entity** which sits at the same position, connected by the **same** predicate.

    E.g. if `e=dbo:Germany` and `e_to_e_out=dbo:leader`, then `e_out=dbr:Angela_Merkel` and `e_out_2=dbr:Joachim_Gauck`.

Note: However, if we want second `e_out` to be connected with **different** predicate, we'd call it `e_out_2*`. 