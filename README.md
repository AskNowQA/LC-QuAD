 # LC-QuAD
## Largescale Complex Question Answering Dataset

### Download 
 :hatching_chick: [Train](train-data.json), [Test](test-data.json) Data 
 
### Links
:earth_africa: [Webpage](http://lc-quad.sda.tech/) | :page_facing_up: [Paper](http://lc-quad.sda.tech/static/ISWC2017_paper_152.pdf) | :office: [Lab](http://sda.cs.uni-bonn.de/)

### Introduction

We release, and maintain a _gold standard_ KBQA (Question Answering over Knowledge Base) dataset 
containing 5000 Question and SPARQL queries.
LC-QuAD uses [DBpedia v04.16](https://wiki.dbpedia.org/dbpedia-version-2016-04) as the target KB.

### Usage

**License**: You can download the dataset (released with a [GPL 3.0 License](LICENSE.txt)), or read below to know more.

**Versioning**: We use [DBpedia version 04-2016](https://wiki.dbpedia.org/dbpedia-version-2016-04) as our target KB. The public DBpedia endpoint (http://dbpedia.org/sparql) no longer uses this version, which might cause many SPARQL queries to not retrieve any answer.
We _strongly_ recommend hosting this version locally. To do so, see [this guide](https://github.com/harsh9t/Dockerised-DBpedia-Virtuoso-Endpoint-Setup-Guide)

**Splits**: We release the dataset split into _training_, and _test_ in a 80:20 fashion.

**Format**: The dataset is released in JSON dumps, where the key 
`corrected_question` contains the question, and `query` contains the corresponding SPARQL query. 

The dataset generated has the following JSON structure, kept intact for . 
```
{
 	'_id': 'Unique ID of this datapoint',
  	'corrected_question': 'Corrected, Final Question',
	'id': 'Template ID',
	'query': 'SPARQL Query',
	'template': 'Template used to create SPARQL Query',
	'intermediary_question': 'Automatically generated, grammatically incorrect question'
}
```

### Cite
```
@inproceedings{trivedi2017lc,
  title={Lc-quad: A corpus for complex question answering over knowledge graphs},
  author={Trivedi, Priyansh and Maheshwari, Gaurav and Dubey, Mohnish and Lehmann, Jens},
  booktitle={International Semantic Web Conference},
  pages={210--218},
  year={2017},
  organization={Springer}
}
```

### Benchmarking/Leaderboard

We're in the process of automating the benchmarking process (and updating results on our [webpage](http://lc-quad.sda.tech)).
In the meantime, please get in touch with us at priyansh.trivedi@uni-bonn.de, and we'll do it manually.
Apologies for this inconvinience.

### Methodology 

**Overview**
- Automatically create **SPARQL** queries.
- Convert SPARQL queries to _intermediary NLQs._
- Manually correct intermediary NLQs to create **Questions**

We start with a set of [Seed Entities](resources/entities.txt), and [Predicate Whitelist](resources/predicates.txt).
Using the whitelist, we generate 2-hop subgraphs around seed entities.
With a seed entity as _supposed_ answer, we juxtapose [SPARQL Templates](resources/templates.json) onto the subgraph, and generate SPARQL queries.

Corresponding to SPARQL template, and based on certain conditions, we assign hand-made NL question templates to the SPARQLs.
_Refer to [this diagram](resources/nomenclature.png) to understand the nomenclature used in templates._

Finally, we follow a two-step (Correct, Review) system to generate a grammatically correct question for every template-generated one.

### Changelog

#### 0.1.3 - 19-06-2018
- Published train-test splits
- Website Updated

#### 0.1.2 - 28-01-2018
- Updated public website
- Dataset now available in QALD format
- Leaderboard underway

#### 0.1.1 -  27-10-2017
- Fixed a bug with rdf:type filter in SPARQL
- data_set.json updated
- updated templates.py

#### 0.1.0 - 01-05-2017
- First version released
- [lc-quad.sda.tech](http://lc-quad.sda.tech) published
