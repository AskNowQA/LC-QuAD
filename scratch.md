# Overall Todos

## Major/BUGS:

- ~~Extend subgraph to return an iterator for mappings~~
- ~~Write generate query code~~
- ~~Update, and fix templates~~
- ~~Add uri type to subgraph~~
- ~~Test uri type in subgraph~~
- ~~Verbalize template 1, 2, 101, 102~~
- **CHECK WHY SOME TEMPALTES ARE NOT BEING GENERATED!!!**
- **Template 8/108 might not satisfy conditions. Check!**
- Enforce that things are unequal in template 305 (and others?)
- Don't pluralize entites in the count templates

## Minor:

- Rework dbpedia interface
- Rework nlutils, to internally call functions properly. No code duplication.
- ~~Write a warning system which neatly breaks lines~~
- [DOING] Clean up the repo, and file structure.
- Update nomenclature png with class_uri, class_x

## Feeling Lucky:

- ~~Extend generator_vanilla to generate all sorts of SPARQLs~~
- ~~Write code to gen SPARQL, which is agnostic to actual template str.~~
- **Improve mapping generation performance.**

## Discuss

- Template `107`, `108` have top class URI mentioned in the question, which can lead to RDF class being there. 
What should we do? Shall we replace them all with `things`?
Eg. `Count the <Works> whose <director> is <Orson  Welles> and <producer> is <Orson  Welles>?` (108)



-------------------------

# Reformatting for LCQuAD v2

## Major Todos

- Get entity in question and not in answer.
    - What algorithm?
    
       we can