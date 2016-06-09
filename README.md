# QueryDataSet
A data set of natural language query with corresponding SPARQL query

###Approaches
Approach 1: SPARQL to Natural Language Query.

Approach 2: Crowdsourcing the coverstion of stanford query dataset to SPARQL.

Approach 3: Check Webquestion query (over freebase) whether they could be answered by DBpedia

###Query Dataset Design & Curation
1. Statistically designing the queryset (dataset) covering questions from all the major sections/topics of interests 
2. Strategic designing the complexity of each query to ensure a good quality of versatile benchmarks: e.g lets say we have 20 queries in politics section, so now we should alternate the complexity (no of triples covered, no. of joins, type of query [snowflake, star, path, keyword]). Thus, 5 keyword queries, 5 linear queries, 5 star shaped, and last 5 with high number of joins or even snowflake queries. 
3. Take a research/empirical study based approach by examining how a variety of query datasets such as QALD, CLEF ehealth queries and others have been curated by the moderators.
4. Provide a GUIDELINE for the end users(crowdsource) for query generation
