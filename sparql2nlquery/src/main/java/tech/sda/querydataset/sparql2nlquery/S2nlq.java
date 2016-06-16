package tech.sda.querydataset.sparql2nlquery;

public class S2nlq {
   /*
    * 1.read the Sparql query
    * 2.pre-process
    * 3.query translation
    */
	static String sparql;
	static String labelSparql;
	static String nlQuery;
	public static void main(String[] args) {
		 sparql = SparqlReader.getSparql();
		 
	}
}
