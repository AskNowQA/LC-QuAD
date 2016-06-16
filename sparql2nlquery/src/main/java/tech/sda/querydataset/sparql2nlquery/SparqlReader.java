package tech.sda.querydataset.sparql2nlquery;

//for fetching SPARQL from QALD6 and others
public class SparqlReader {

	static String getSparql(){
		return "SELECT DISTINCT ?uri WHERE "
				+ "{  <http://dbpedia.org/resource/Ganges> <http://dbpedia.org/property/sourceCountry> ?l . "
				+ "?uri <http://www.w3.org/2000/01/rdf-schema#label> ?l . "
				+ "?uri rdf:type <http://dbpedia.org/ontology/Country>";
		
	}
}

