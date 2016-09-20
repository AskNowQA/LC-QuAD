# Generating Natural Language Questions from valid SPARQL Queries
## Introduction
This code aims to convert a valid SPARQL query into a (or many) natural language questions. The incentive is to create a good dataset for QA system training, and achieve a scale which helps Neural Network based QA Systems too. We do this mostly by converting the query into a pseudo natural language question based on some rules we basically derive by hand, and come up with some sort of an algorithm which does this. Thereafter we will use some heurestic based features to figure out appropriate prepositions and Wh-types (What, when, who, which, where...). 

Refer to this document for a list of templates we have or will be focusing on - https://docs.google.com/document/d/1N4KRy_xMD7B5cAnQWMiytRrPkZ-HwIEiZj4PbI-xROM/edit
`Note: If you don't have access to the doc, please drop me a mail at pc.priyansh@gmail.com`

## Branches
#### master
Will have the code for converting SPARQL templates to valid SPARQL Queries which retrieve something from DBPedia, and then to convert them to pseudo-nl query.

#### relation-curation
Code and files which are collected from varied sources, of good relations in DBPedia, making our job easier. This is mostly taken from other research projects. The commit messages will contain information of the sources, for future crediting. 

##Deployment
@todo