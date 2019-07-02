import json


def load_json(path):
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def beautifier(data):
    for row in data:
        print "\t<div class=\"item\">"
        print "\t<div class=\"content\">"

        # Question
        question = row["question"]
        # if "?" not in question:
        #     question = question + "?"
        print "\t<div class=\"header\">%s</div>" % question

        if "sparql_wikidata" in row:
            # Wikidata
            print "\t<div class=\"description\">"
            print "\t<p>"
            print "\tSPARQL Wikidata : ", row["sparql_wikidata"]
            print "\t</p>"
            print "\t</div>"


        # DBPedia
        if "sparql_dbpedia18" in row:
            # Wikidata
            print "\t<div class=\"description\">"
            print "\t<p>"
            print "\tSPARQL DBpedia18: ", row["sparql_dbpedia18"]
            print "\t</p>"
            print "\t</div>"

        print "\t</div>"
        print "\t</div>"


if __name__ == '__main__':
    beautifier(load_json("static/lc-quad2.0_nitpicks.json"))
