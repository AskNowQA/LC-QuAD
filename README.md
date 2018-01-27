# LC-QuAD
## Largescale Complex Question Answering Dataset

### Introduction


This framework aims to  create a large QA pairs, with their equivalent logical form. The primary objective while designing the framework for question generation was to generate a high quality large dataset with low domain expert intervention. In most of the datset, which has a logical form of the Question were generated manually. This process of writing formal expressions needs domain experts with a deep understanding of the underlying KB schema, and syntaxes of the logical form. 

The dataset generated from the framework using DBpedia as the knowledge base is available at <https://figshare.com/projects/LC-QuAD/21812>.  

Refer to this document for a list of templates we have or will be focusing on - <https://docs.google.com/document/d/1N4KRy_xMD7B5cAnQWMiytRrPkZ-HwIEiZj4PbI-xROM/edit?usp=sharing>

`Note: If you don't have access to the doc, please drop me a mail at pc.priyansh@gmail.com`


The dataset generated has the following JSON structure. 

```
{
 	u'_id': u'32 charachter long alpha-numeric ID',
  	u'corrected_answer': u'Verbalized form by the First reviewer',
	u'id': "template id in integer",
	u'query': u' The actual SPARQL queries',
	u'template': u'The tempalte of the SPARQL Query ',
	u'verbalized_question': u'Semi verbalized query'
}

```



### Branches
#### develop
Current default branch. Latest version of framework would be here.

#### relation-curation
Code and files which are collected from varied sources, of good relations in DBPedia, making our job easier. This is mostly taken from other research projects. The commit messages will contain information of the sources, for future crediting. 


### Changelog

#### 0.1.2 - 28-01-2018
- Updated public website
- Dataset now available in QALD format
- Published train, test splits
- Leaderboard underway

#### 0.1.1 -  27-10-2017
- Fixed a bug with rdf:type filter in SPARQL
- data_set.json updated
- updated templates.py

#### 0.1.0 - 01-05-2017
- First version released
- [lc-quad.sda.tech](http://lc-quad.sda.tech) published
