"""
    Contains ways to verbalize sparqls.

    Usage: call verbalizer class over

    SPARQL looks like this:
        {
            "template": "SELECT DISTINCT COUNT(?uri) WHERE {
                    ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x .
                } ",
            "template_id": 106,
            "n_entities": 1,
            "type": "count",
            "max": 100,
            "query": "SELECT DISTINCT COUNT(?uri) WHERE {
                    ?x <http://dbpedia.org/property/governmentType> <http://dbpedia.org/resource/Suva_City_Council> .
                    ?uri <http://dbpedia.org/property/capital> ?x .
                } ",
            "_id": "cfb7a9fae1074751a52a6115038dc59d",
            "corrected": "false",
            "mapping": {
                    "e_to_e_out": "http://dbpedia.org/property/capital",
                    "class_uri": "http://dbpedia.org/ontology/MusicalArtist",
                    "e_out_to_e_out_out": "http://dbpedia.org/property/governmentType",
                    "e_out_out": "http://dbpedia.org/resource/Suva_City_Council"
                },
            "mapping_type": {
                    "e_to_e_out": "http://www.w3.org/2002/07/owl#Thing",
                    "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                    "e_out_to_e_out_out": "http://www.w3.org/2002/07/owl#Thing",
                    "e_out_out": "http://dbpedia.org/ontology/Organisation"
                },
            "answer_num": {"callret-0": 1}, "answer": {"callret-0": ["2"]}}

    ANOTHER
        {
            "template": " SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> . } ",
            "template_id": 1,
            "n_entities": 1,
            "type": "vanilla",
            "max": 100,
            "query": " SELECT DISTINCT ?uri WHERE {
                    ?uri <http://dbpedia.org/property/capital> <http://dbpedia.org/resource/Suva> .
                } ",
            "_id": "01f0be26f67c48028506e999d265d3e2",
            "corrected": "false",
            "mapping": {
                    "e_to_e_out": "http://dbpedia.org/property/capital",
                    "class_uri": "http://dbpedia.org/ontology/MusicalArtist",
                    "e_out": "http://dbpedia.org/resource/Suva"
                },
            "mapping_type": {
                    "e_to_e_out": "http://www.w3.org/2002/07/owl#Thing",
                    "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                    "e_out": "http://dbpedia.org/ontology/City"
                },
            "answer_num": {"uri": 2},
            "answer": {"uri": ["http://dbpedia.org/resource/Fiji", "http://dbpedia.org/resource/Colony_of_Fiji"]}
        }


    TEMPLATES covered: 1, 2, 3, 6, 7, 8, 11, 15, 16, 101, 102, 103, 106, 107, 108, 301, 302, 303, 305, 306,
    307, 308, 309, 311, 315, 316
    401, 402, 403, 406, 407, 408, 411
    TOTEST: 5, 9, 402
    LEFT: 105,405, 451, 452
"""
import json
import warnings
from pprint import pprint
import numpy.random as npr

warnings.filterwarnings("ignore")

from utils.goodies import *
from utils import dbpedia_interface as dbi
from utils import natural_language_utilities as nlutils

NUM_ANSWER_PLURAL = 3
NO_SURFACE_FORM = ['count_prefix_a', 'count_prefix_b', 'Who_What', 'who_which', 'and_aswellas', 'alsothe', 'both',
                   'arethere_exists', 'things_thething']
# npr.seed(42)


class Templates(object):
    """
        These are what makes the questions. Fill the dict in order you want the decision to be made (plural -> type) etc.
        Add an 's' after variable if you want it to be plural. e.g. e_to_e_out -> e_to_e_out_s

        Ideally, the templates should be automatically picked up by the verbalizing class.

        [DONE]? @TODO: add and incorporate count prefixes
    """
    COUNT_PREFIXES_A = ['Give me the total number of', 'Count the', 'Count the number of', 'What is the number of']
    COUNT_PREFIXES_B = ['How many']

    _1 = FancyDict(
        vanilla=["%(Who_What)s is the <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s>?",
                 "%(Who_What)s <%(e_to_e_out)s> is <%(e_out)s>?"],
        plural=["%(Who_What)s are the things whose <%(e_to_e_out)s> is <%(e_out)s>?",
                "%(Who_What)s <%(e_to_e_out)s> is <%(e_out)s>?"])
    _301 = FancyDict(
        vanilla = ["%(Who_What)s is the <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s>?"],
        plural = ["%(Who_What)s are the <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s>?",
                "%(Who_What)s <%(class_uri)s>'s <%(e_to_e_out)s> is <%(e_out)s>?"]
    )
    _2 = FancyDict(
        vanilla=["%(Who_What)s is the <%(e_in_to_e)s> of <%(e_in)s>?"],
        plural=["%(Who_What)s are the <%(e_in_to_e_s)s> of <%(e_in)s>?"])
    _302 = FancyDict(
        vanilla=["%(Who_What)s <%(class_uri)s> is the <%(e_in_to_e)s> of <%(e_in)s>?"],
        plural=["%(Who_What)s <%(class_uri)s> are the <%(e_in_to_e_s)s> of <%(e_in)s>?"])
    _3 = FancyDict(
        vanilla=["What is the <%(e_in_to_e)s> of %(things_thething)s %(who_which)s is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s>?"])
    _303 = FancyDict(
        vanilla=["What is the <%(e_in_to_e)s> of <%(class_x)s> %(who_which)s is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s>?"])
    _5 = FancyDict(
        vanilla=["%(Who_What)s is the <%(e_in_to_e)s> of %(things_thething)s whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?",
                 "Tell me the <%(e_in_to_e)s> of %(things_thething)s whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"],
        plural=["List the <%(e_in_to_e)s> of the things whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?",
                "%(Who_What)s the <%(e_in_to_e)s> of the things whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"])
    _305 = FancyDict(
        vanilla=["%(Who_What)s is the <%(e_in_to_e)s> of <%(class_uri)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?",
                 "Tell me the <%(e_in_to_e)s> of <%(class_uri)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"],
        plural=["List the <%(e_in_to_e)s> of the <%(class_uri)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?",
                "%(Who_What)s the <%(e_in_to_e)s> of the <%(class_uri)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"])
    _6 = FancyDict(
        vanilla=["%(Who_What)s is the <%(top_class_uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
                 "Name the <%(top_class_uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
                 "<%(e_out_out)s> is the <%(e_out_to_e_out_out)s> of the <%(e_to_e_out)s> of %(Who_What)s?"],
        plural=["%(Who_What)s are the <%(top_class_uri_s)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
                "List the <%(sp_class_uri_s)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>."])
    _306 = FancyDict(
        vanilla=[
            "%(Who_What)s is the <%(class_x)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
            "Name the <%(class_x)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
            "<%(e_out_out)s> is the <%(e_out_to_e_out_out)s> of the <%(e_to_e_out)s> of %(Who_What)s?",
            "<%(e_out_out)s> is the <%(e_out_to_e_out_out)s> of %(Who_What)s <%(class_x)s>'s <%(e_to_e_out)s>?"],
        plural=[
            "%(Who_What)s are the <%(class_x)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?",
            "List the <%(class_x)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>."])
    _7 = FancyDict(
        vanilla=FancyDict(
            vanilla=["Whose <%(e_to_e_out)s> includes both <%(e_out)s>, %(and_aswellas)s <%(e_out_2)s>?",
                     "%(Who_What)s is the <%(top_class_uri)s> whose <%(e_to_e_out)s> are <%(e_out)s> %(and_aswellas)s <%(e_out_2)s>?"],
            plural=["<%(e_to_e_out_s)s> of %(Who_What)s are <%(e_out)s> %(and_aswellas)s <%(e_out_2)s>?",
                    "%(Who_What)s are the <%(top_class_uri_s)s> whose <%(e_to_e_out)s> are <%(e_out)s> and <%(e_out_2)s>?"]),
        preposition=["What is <%(e_to_e_out)s> <%(e_out)s> and <%(e_out_2)s>?"])
    _307 = FancyDict(
        vanilla=FancyDict(
            vanilla=["Which <%(class_uri)s>'s <%(e_to_e_out)s> includes both <%(e_out)s>, %(and_aswellas)s <%(e_out_2)s>?",
                     "%(Who_What)s is the <%(class_uri)s> whose <%(e_to_e_out)s> are <%(e_out)s> %(and_aswellas)s <%(e_out_2)s>?"],
            plural=["<%(e_to_e_out_s)s> of %(Who_What)s <%(class_uri)s>'s are <%(e_out)s> %(and_aswellas)s <%(e_out_2)s>?",
                    "%(Who_What)s are the <%(class_uri)s> whose <%(e_to_e_out)s> are <%(e_out)s> and <%(e_out_2)s>?"]),
        preposition=["Which <%(class_uri)s> is <%(e_to_e_out)s> <%(e_out)s> and <%(e_out_2)s>?"])
    _8 = FancyDict(
        vanilla=["%(Who_What)s is the <%(top_class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?"],
        plural=["%(Who_What)s are the <%(top_class_uri_s)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?"])
    _308 = FancyDict(
        vanilla=[
            "%(Who_What)s is the <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?"],
        plural=[
            "%(Who_What)s are the <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?"])
    _9 = FancyDict(
        vanilla=["%(Who_What)s is <%(e_in_to_e)s> of %(things_thething)s %(who_which) is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s>"])
    _309 = FancyDict(
        vanilla=[
            "%(Who_What)s is <%(e_in_to_e)s> of <%(class_x)s> %(who_which)s is the <%(e_in_in_to_e_in)s> of <%(e_in_in)s>"])
    _11 = FancyDict(
        vanilla=["List the other <%(e_in_to_e)s> of %(things_thething)s one of whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
                 "Name some other <%(e_in_to_e)s> of those things one of whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
                 "What are the other <%(e_in_to_e)s> of %(things_thething)s one of whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"])
    _311 = FancyDict(
        vanilla=[
            "List the other <%(e_in_to_e)s> of <%(class_x)s> one of whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
            "Name some other <%(e_in_to_e)s> of those <%(class_x)s> one of whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
            "What are the other <%(e_in_to_e)s> of <%(class_x)s> one of whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"])
    _15 = FancyDict(
        vanilla=["%(Who_What)s is the <%(e_in_to_e)s> of the <%(e_in)s> %(and_aswellas)s <%(e_in_2)s>?"],
        plural=["%(Who_What)s are the <%(e_in_to_e)s> of the <%(e_in)s> %(and_aswellas)s <%(e_in_2)s>?"])
    _315 = FancyDict(
        vanilla=["%(Who_What)s <%(class_uri)s> is the <%(e_in_to_e)s> of the <%(e_in)s> %(and_aswellas)s <%(e_in_2)s>?"],
        plural=["%(Who_What)s <%(class_uri)s> are the <%(e_in_to_e)s> of the <%(e_in)s> %(and_aswellas)s <%(e_in_2)s>?"])
    _16 = FancyDict(
        vanilla=["%(Who_What)s is the <%(e_in_to_e)s> of the <%(e_in)s> and %(alsothe)s<%(e_in_to_e_2)s> of the <%(e_in_2*)s>?"],
        plural=["%(Who_What)s are the <%(e_in_to_e)s> of the <%(e_in)s> and %(alsothe)s<%(e_in_to_e_2)s> of the <%(e_in_2*)s>?"])
    _316 = FancyDict(
        vanilla=[
            "%(Who_What)s <%(class_uri)s> is the <%(e_in_to_e)s> of the <%(e_in)s> and %(alsothe)s<%(e_in_to_e_2)s> of the <%(e_in_2*)s>?"],
        plural=[
            "%(Who_What)s <%(class_uri)s> are the <%(e_in_to_e)s> of the <%(e_in)s> and %(alsothe)s<%(e_in_to_e_2)s> of the <%(e_in_2*)s>?"])
    _101 = FancyDict(
        vanilla=["How many things are there whose <%(e_to_e_out)s> is <%(e_out_s)s>?",
                 "%(count_prefix_a)s things whose <%(e_to_e_out)s> is <%(e_out_s)s>?"])
    _401 = FancyDict(
        vanilla=["How many <%(class_uri)s> are there whose <%(e_to_e_out)s> is <%(e_out_s)s>?",
                 "%(count_prefix_a)s <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out_s)s>?"])
    _102 = FancyDict(
        vanilla=["%(count_prefix_a)s <%(e_in_to_e_s)s> in <%(e_in_s)s>?",
                 "%(count_prefix_a)s <%(e_in_to_e_s)s> in <%(e_in_s)s>?",
                 "%(count_prefix_b)s <%(e_in_to_e_s)s> are there in <%(e_in_s)s>?"])

    _402 = FancyDict(
        vanilla=["%(count_prefix_a)s <%(class_uri)s> <%(e_in_to_e_s)s> in <%(e_in_s)s>?",
                 "%(count_prefix_a)s <%(class_uri)s> <%(e_in_to_e_s)s> in <%(e_in_s)s>?",
                 "%(count_prefix_b)s <%(class_uri)s> <%(e_in_to_e_s)s> are there in <%(e_in_s)s>?"])

    _103 = FancyDict(
        vanilla=["%(count_prefix_b)s <%(e_in_to_e_s)s> are there of the thing %(who_which)s is the <%(e_in_in_to_e_in)s> of <%(e_in_in_s)s> ?"],
        continuous=["%(count_prefix_b)s <%(e_in_to_e_s)s> are there of the thing %(who_which)s is the <%(e_in_in_to_e_in)s> in <%(e_in_in_s)s> ?"])

    _403 = FancyDict(
        vanilla=["%(count_prefix_b)s <%(e_in_to_e_s)s> are there of the <%(class_x)s> %(who_which)s is the <%(e_in_in_to_e_in)s> of <%(e_in_in_s)s> ?"],
        continuous=["%(count_prefix_b)s <%(e_in_to_e_s)s> are there of the <%(class_x)s> %(who_which)s is the <%(e_in_in_to_e_in)s> in <%(e_in_in_s)s> ?"])


    _106 = FancyDict(
        vanilla=["%(count_prefix_a)s <%(top_class_uri_s)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?"])

    _406 = FancyDict(
        vanilla=[
            "%(count_prefix_a)s <%(class_uri)s> whose <%(e_to_e_out)s>'s <%(e_out_to_e_out_out)s> is <%(e_out_out)s>?"])

    _107 = FancyDict(
        vanilla=["%(count_prefix_b)s <%(top_class_uri_s)s> are there whose <%(e_to_e_out)s> are %(both)s<%(e_out)s> %(and_aswellas)s <%(e_out_2)s>?",
                 "%(count_prefix_a)s <%(top_class_uri_s)s> whose <%(e_to_e_out)s> are %(both)s<%(e_out)s> %(and_aswellas)s <%(e_out_2)s>."])

    _407 = FancyDict(
        vanilla=[
            "%(count_prefix_b)s <%(class_uri)s> are there whose <%(e_to_e_out)s> are %(both)s<%(e_out)s> %(and_aswellas)s <%(e_out_2)s>?",
            "%(count_prefix_a)s <%(class_uri)s> whose <%(e_to_e_out)s> are %(both)s<%(e_out)s> %(and_aswellas)s <%(e_out_2)s>."])
    _108 = FancyDict(
        vanilla=["%(count_prefix_b)s <%(top_class_uri_s)s> %(arethere_exists)s whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?",
                 "%(count_prefix_a)s <%(top_class_uri_s)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?",
                 "%(count_prefix_b)s things %(arethere_exists)s whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?",
                 "%(count_prefix_a)s things whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s"])

    _408 = FancyDict(
        vanilla=[
            "%(count_prefix_b)s <%(class_uri)s> %(arethere_exists)s whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?",
            "%(count_prefix_a)s <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?",
            "%(count_prefix_b)s <%(class_uri)s> %(arethere_exists)s whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s>?",
            "%(count_prefix_a)s <%(class_uri)s> whose <%(e_to_e_out)s> is <%(e_out)s> and <%(e_to_e_out_2)s> is <%(e_out_2*)s"])


    _111 = FancyDict(
        vanilla=["Give me the total number of <%(e_in_to_e_s)s> of the %(things_thething)s whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
                 "Count the other <%(e_in_to_e_s)s> of the %(things_thething)s whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
                 "Count the number of other <%(e_in_to_e_s)s> of the %(things_thething)s whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
                 "How many other <%(e_in_to_e_s)s> %(arethere_exists)s of the %(things_thething)s whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"])

    _411 = FancyDict(
        vanilla=[
            "Give me the total number of <%(e_in_to_e_s)s> of the <%(class_x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
            "Count the other <%(e_in_to_e_s)s> of the <%(class_x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
            "Count the number of other <%(e_in_to_e_s)s> of the <%(class_x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>.",
            "How many other <%(e_in_to_e_s)s> %(arethere_exists)s of the <%(class_x)s> whose <%(e_in_to_e_in_out)s> is <%(e_in_out)s>?"])


def _answer_is_person_(datum):
    return 'http://dbpedia.org/ontology/Agent' in datum['answer_type'] \
           and "http://dbpedia.org/ontology/Organisation" not in datum['answer_type']


def _get_plural_maps_(datum: dict):
    """
        Appends plural version of mapping
    :param datum:
    :return:
    """
    datum.update({k + '_s': nlutils.get_plural(v) for k, v in datum.items()})
    return datum


class Verbalizer:
    """
        Instantiate for each different template you want to verbalize.
        Not for each different question.

        Usage:
            Init with template ID
            Verbalize by giving it the dict (stored as ./sparql/template_*)

        Logic:
            Instantiate with a given template id, it pulls nl templates.
            Then navigates based on the keys mentioned in the templates.
            Once decided on a *list* of templates (devoid of rules), it selects randomly b/w them.
            Different things such as "Who/What", "Person/Thing" are decided on the fly (within verbalize)

            This is done for all diff sparqls, individually.

        @TODO: can we make this filtering perform on the entire group?
        @TODO: figure out all the data we need to make this decision.

    """

    def __init__(self, _id: int):
        self.templates = getattr(Templates, '_' + str(_id))
        self.dbp = dbi.DBPedia(_verbose=False, _caching=False)

        # If in count range, put plural in flags by default
        if 100 < _id < 120 or 400 < _id < 420:
            self.default_flags = ['plural']
        else:
            self.default_flags = []

        # List containing sp. conditions for filling this template
        self.flags = self.default_flags.copy()

    def _get_template_(self, templates, sparql):
        """
            Recursive fn which finally will home down on a concrete list of templates.

            Logic:
                there will be two keys. One will be named vanilla. One something else.
                E.g. vanilla, plural -> if less than some, choose vanilla. else choose plural
                @TODO: other such constraints

        :param sparql: the data based on which our decisions are made
        :return: list of str/dict based on recursive or not
        """
        if type(templates) is list:
            return templates

        keys = list(templates.keys()).copy()
        keys.pop(keys.index('vanilla'))

        # If no other key left, return vanilla
        if len(keys) == 0:
            return self._get_template_(templates.vanilla, sparql)

        # Some other key is left
        keys = keys[0]

        if keys == 'plural':
            num_ans = sparql['answer_num']
            self.flags.append('plural')
            return self._get_template_(templates.plural if num_ans >= NUM_ANSWER_PLURAL else templates.vanilla, sparql)

        if keys == 'preposition':
            by = sparql['mapping']['e_to_e_out'].split()[-1].lower() == 'by'
            return self._get_template_(templates.preposition if by else templates.vanilla, sparql)

        if keys == 'continuous':
            continuous_pred = 'ing' in sparql['mapping']['e_in_in_to_e_in']
            return self._get_template_(templates.continuous if continuous_pred else templates.vanilla, sparql)

    def _get_sf_(self, mapping):
        """
            Replace url with its surface form
        :param mapping: dict
        :return: dict (same keys)
        """
        return {k: self.dbp.get_label(v) if k not in NO_SURFACE_FORM else v
                for k, v in mapping.items()}

    def _reset_(self):
        """
            Will reset flags.
        :return: None
        """
        self.flags = self.default_flags.copy()

    def verbalize(self, datum):
        """
            Navigate based on particulars of this sparql, and decide what conditions to follow.

        :param datum: dict (mentioned @ start of script)
        :return: dict (mentioned @ start of script) + new fields
        """
        self._reset_()

        # Select the correct template.
        candidate_templates = self._get_template_(self.templates, datum)
        template = npr.choice(candidate_templates)

        # Update mapping with prefix
        datum['mapping']['top_class_uri'] = self.dbp.get_most_generic_class(datum['mapping']['class_uri'], _is_class=True)
        datum['mapping']['count_prefix_a'] = npr.choice(Templates.COUNT_PREFIXES_A)
        datum['mapping']['count_prefix_b'] = npr.choice(Templates.COUNT_PREFIXES_B)
        datum['mapping']['who_which'] = 'who' if _answer_is_person_(datum) else 'which'
        datum['mapping']['Who_What'] = 'Who' if _answer_is_person_(datum) else npr.choice(['What', 'Which'], p=[0.3, 0.7])
        datum['mapping']['and_aswellas'] = npr.choice(['and', 'as well as'])
        datum['mapping']['alsothe'] = npr.choice(['also the ', ''])
        datum['mapping']['things_thething'] = npr.choice(['things', 'the thing'], p=[0.8, 0.2])
        datum['mapping']['arethere_exists'] = npr.choice(['are there', 'exists'], p=[0.1, 0.9])
        datum['mapping']['both'] = npr.choice(['both ', ''])

        # Get surface form of mappings
        datum['mapping_sf'] = self._get_sf_(datum['mapping'])
        if 'plural' in self.flags:
            datum['mapping_sf'] = _get_plural_maps_(datum['mapping_sf'])
        datum['question_verbalized'] = template % datum['mapping_sf']
        datum['question_template'] = template

        return datum


def test_template(id:int, skip:int = 0, show:bool = False) -> None:
    f = open(f'resources/sparqls/template{id}.txt', 'r')
    counter = 0
    for line in f.readlines():
        data = json.loads(line)
        if counter >= skip:
            break
        counter += 1
    if show:
        pprint(data['query'])
    verb = Verbalizer(id)
    data = verb.verbalize(data)
    print(data['question_verbalized'])




if __name__ == "__main__":
    data_1 = {"template": " SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> . } ", "template_id": 1, "n_entities": 1,
              "type": "vanilla", "max": 100,
              "query": " SELECT DISTINCT ?uri WHERE {?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Abstract_strategy_game> . } ",
              "_id": "75a170adb55245cdb0d63e8fa70cf3bc", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
              "mapping": {"e_to_e_out": "http://dbpedia.org/property/genre", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                          "e_out": "http://dbpedia.org/resource/Abstract_strategy_game"},
              "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                               "e_out": "http://dbpedia.org/ontology/MusicGenre"},
              "answer_type": ["http://dbpedia.org/ontology/VideoGame", "http://dbpedia.org/ontology/Activity",
                              "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/Sport"], "answer_num": 50, "answer": {
            "uri": ["http://dbpedia.org/resource/Chess", "http://dbpedia.org/resource/Chinese_checkers",
                    "http://dbpedia.org/resource/Reversi", "http://dbpedia.org/resource/Shogi",
                    "http://dbpedia.org/resource/Abalone_(board_game)", "http://dbpedia.org/resource/Fanorona",
                    "http://dbpedia.org/resource/Hex_(board_game)", "http://dbpedia.org/resource/Nine_Men's_Morris",
                    "http://dbpedia.org/resource/Xiangqi", "http://dbpedia.org/resource/Epaminondas_(game)",
                    "http://dbpedia.org/resource/Renju", "http://dbpedia.org/resource/Arimaa",
                    "http://dbpedia.org/resource/GIPF_(game)", "http://dbpedia.org/resource/YINSH",
                    "http://dbpedia.org/resource/Tori_shogi", "http://dbpedia.org/resource/Terakh",
                    "http://dbpedia.org/resource/Tafl_games", "http://dbpedia.org/resource/Connect_Four",
                    "http://dbpedia.org/resource/DVONN", "http://dbpedia.org/resource/Janggi",
                    "http://dbpedia.org/resource/Dablot_Prejjesne", "http://dbpedia.org/resource/Connect_4x4",
                    "http://dbpedia.org/resource/Chu_shogi", "http://dbpedia.org/resource/Ludus_latrunculorum",
                    "http://dbpedia.org/resource/Circular_chess", "http://dbpedia.org/resource/Terrace_(board_game)",
                    "http://dbpedia.org/resource/Breakthru_(board_game)", "http://dbpedia.org/resource/Alquerque",
                    "http://dbpedia.org/resource/Draughts", "http://dbpedia.org/resource/Go_(game)",
                    "http://dbpedia.org/resource/International_draughts", "http://dbpedia.org/resource/Yot\u00e9",
                    "http://dbpedia.org/resource/Halma", "http://dbpedia.org/resource/Four-player_chess",
                    "http://dbpedia.org/resource/Lasca", "http://dbpedia.org/resource/Russian_draughts",
                    "http://dbpedia.org/resource/Fangqi", "http://dbpedia.org/resource/Spot:_The_Video_Game",
                    "http://dbpedia.org/resource/EuroShogi", "http://dbpedia.org/resource/Four_Fronts",
                    "http://dbpedia.org/resource/Jungle_(board_game)", "http://dbpedia.org/resource/English_draughts",
                    "http://dbpedia.org/resource/Morabaraba", "http://dbpedia.org/resource/Conspirateurs",
                    "http://dbpedia.org/resource/Camelot_(board_game)", "http://dbpedia.org/resource/Cubic_chess",
                    "http://dbpedia.org/resource/Choko_(game)", "http://dbpedia.org/resource/Lines_of_Action",
                    "http://dbpedia.org/resource/Game_of_the_Seven_Kingdoms", "http://dbpedia.org/resource/The_Duke_(board_game)"]}}
    data_2 = {"template": " SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri . } ", "template_id": 2, "n_entities": 1,
              "type": "vanilla", "max": 100,
              "query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines> <http://dbpedia.org/ontology/sport> ?uri . } ",
              "_id": "af4eef5b7e4d47a99457fd6c8736b0da", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
              "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/sport", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                          "e_in": "http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines"},
              "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                               "e_in": "http://dbpedia.org/ontology/School"},
              "answer_type": ["http://dbpedia.org/ontology/Activity", "http://dbpedia.org/ontology/Sport",
                              "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/VideoGame"], "answer_num": 13,
              "answer": {"uri": ["http://dbpedia.org/resource/Archery", "http://dbpedia.org/resource/Badminton",
                                 "http://dbpedia.org/resource/Basketball", "http://dbpedia.org/resource/Chess",
                                 "http://dbpedia.org/resource/Tennis", "http://dbpedia.org/resource/Ultimate_(sport)",
                                 "http://dbpedia.org/resource/Volleyball", "http://dbpedia.org/resource/Water_polo",
                                 "http://dbpedia.org/resource/Football", "http://dbpedia.org/resource/Track_and_field",
                                 "http://dbpedia.org/resource/Flying_disc_games", "http://dbpedia.org/resource/Swimming_(sport)",
                                 "http://dbpedia.org/resource/Combat_sport"]}}
    data_3 = {"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri . } ",
              "template_id": 3, "n_entities": 1, "type": "vanilla", "max": 100,
              "query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/The_Bad_and_the_Beautiful> <http://dbpedia.org/property/basedOn> ?x . ?x <http://dbpedia.org/ontology/deathCause> ?uri . } ",
              "_id": "075c95528e8746d0856c3b42e97a23d2", "corrected": "false",
              "entity": "http://dbpedia.org/resource/Cholera",
              "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/deathCause", "class_uri": "http://dbpedia.org/ontology/Disease",
                          "e_in_in_to_e_in": "http://dbpedia.org/property/basedOn", "e_in_in": "http://dbpedia.org/resource/The_Bad_and_the_Beautiful"},
              "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                               "e_in_in_to_e_in": "http://www.w3.org/2002/07/owl#Thing", "e_in_in": "http://dbpedia.org/ontology/Archive"},
              "answer_type": ["http://dbpedia.org/ontology/Disease"], "answer_num": 1,
              "answer": {"uri": ["http://dbpedia.org/resource/Cholera"]}}
    data_3 = {"template": " SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri . } ",
              "template_id": 3, "n_entities": 1, "type": "vanilla", "max": 100,
              "query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/List_of_Band_of_Brothers_episodes> <http://dbpedia.org/property/writtenby> ?x . ?x <http://dbpedia.org/ontology/notableWork> ?uri . } ",
              "_id": "58ddb98ab93349d6990e5fce124217e0", "corrected": "false",
              "entity": "http://dbpedia.org/resource/Band_of_Brothers_(miniseries)",
              "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/notableWork", "class_uri": "http://dbpedia.org/ontology/Drama",
                          "e_in_in_to_e_in": "http://dbpedia.org/property/writtenby",
                          "e_in_in": "http://dbpedia.org/resource/List_of_Band_of_Brothers_episodes"},
              "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing",
                               "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                               "e_in_in_to_e_in": "http://www.w3.org/2002/07/owl#Thing",
                               "e_in_in": "http://dbpedia.org/ontology/Person"},
              "answer_type": ["http://dbpedia.org/ontology/TelevisionShow", "http://dbpedia.org/ontology/Drama", "http://dbpedia.org/ontology/Work", "http://dbpedia.org/ontology/Film"],
              "answer_num": 3,
              "answer": {"uri": ["http://dbpedia.org/resource/Band_of_Brothers_(miniseries)", "http://dbpedia.org/resource/Legend_of_the_Guardians:_The_Owls_of_Ga'Hoole", "http://dbpedia.org/resource/A_Mighty_Heart_(film)"]}}
    data_6 = {"template": "SELECT DISTINCT ?uri WHERE { ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x . } ",
              "template_id": 6, "n_entities": 1, "type": "vanilla", "max": 100,
              "query": "SELECT DISTINCT ?uri WHERE { ?x <http://dbpedia.org/property/headquarters> <http://dbpedia.org/resource/Stockholm> . ?uri <http://dbpedia.org/property/presenter> ?x . } ",
              "_id": "a7e1a8b7a8894d69b82654990ab1a904", "corrected": "false", "entity": "http://dbpedia.org/resource/Nobel_Prize",
              "mapping": {"e_to_e_out": "http://dbpedia.org/property/presenter",
                          "class_uri": "http://dbpedia.org/ontology/TelevisionShow",
                          "e_out_to_e_out_out": "http://dbpedia.org/property/headquarters",
                          "e_out_out": "http://dbpedia.org/resource/Stockholm"},
              "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                               "e_out_to_e_out_out": "http://www.w3.org/2002/07/owl#Thing",
                               "e_out_out": "http://dbpedia.org/ontology/City"},
              "answer_type": ["http://dbpedia.org/ontology/TelevisionShow", "http://dbpedia.org/ontology/Organization",
                              "http://dbpedia.org/ontology/Award"], "answer_num": 9, "answer": {
            "uri": ["http://dbpedia.org/resource/Svenska_Dagbladet_Gold_Medal", "http://dbpedia.org/resource/Nobel_Prize",
                    "http://dbpedia.org/resource/Nobel_Prize_controversies", "http://dbpedia.org/resource/Nobel_Prize_in_Literature",
                    "http://dbpedia.org/resource/Guldbollen", "http://dbpedia.org/resource/Nobel_Prize_in_Physics",
                    "http://dbpedia.org/resource/Crafoord_Prize",
                    "http://dbpedia.org/resource/Nobel_Memorial_Prize_in_Economic_Sciences",
                    "http://dbpedia.org/resource/Nobel_Prize_in_Chemistry"]}}
    data_7 = {"template": " SELECT DISTINCT ?uri WHERE { ?uri <%(e_to_e_out)s> <%(e_out)s> . ?uri <%(e_to_e_out)s> <%(e_out_2)s> . } ",
              "template_id": 7, "n_entities": 2, "type": "vanilla", "max": 100,
              "query": " SELECT DISTINCT ?uri WHERE { ?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Board_game> . ?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Abstract_strategy_game> . } ",
              "_id": "236e78c0aae542a59688f76c7d3a8c69", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
              "mapping": {"e_to_e_out": "http://dbpedia.org/property/genre", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                          "e_out": "http://dbpedia.org/resource/Board_game",
                          "e_out_2": "http://dbpedia.org/resource/Abstract_strategy_game"},
              "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                               "e_out": "http://dbpedia.org/ontology/MusicGenre", "e_out_2": "http://dbpedia.org/ontology/MusicGenre"},
              "answer_type": ["http://dbpedia.org/ontology/Activity", "http://dbpedia.org/ontology/Sport",
                              "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/VideoGame"], "answer_num": 41,
              "answer": {"uri": ["http://dbpedia.org/resource/Chess", "http://dbpedia.org/resource/Chinese_checkers",
                                 "http://dbpedia.org/resource/Reversi", "http://dbpedia.org/resource/Shogi",
                                 "http://dbpedia.org/resource/Abalone_(board_game)", "http://dbpedia.org/resource/Fanorona",
                                 "http://dbpedia.org/resource/Hex_(board_game)", "http://dbpedia.org/resource/Nine_Men's_Morris",
                                 "http://dbpedia.org/resource/Xiangqi", "http://dbpedia.org/resource/Epaminondas_(game)",
                                 "http://dbpedia.org/resource/Renju", "http://dbpedia.org/resource/Arimaa",
                                 "http://dbpedia.org/resource/GIPF_(game)", "http://dbpedia.org/resource/YINSH",
                                 "http://dbpedia.org/resource/Tori_shogi", "http://dbpedia.org/resource/Tafl_games",
                                 "http://dbpedia.org/resource/DVONN", "http://dbpedia.org/resource/Janggi",
                                 "http://dbpedia.org/resource/Dablot_Prejjesne", "http://dbpedia.org/resource/Chu_shogi",
                                 "http://dbpedia.org/resource/Ludus_latrunculorum", "http://dbpedia.org/resource/Terrace_(board_game)",
                                 "http://dbpedia.org/resource/Breakthru_(board_game)", "http://dbpedia.org/resource/Alquerque",
                                 "http://dbpedia.org/resource/Draughts", "http://dbpedia.org/resource/Go_(game)",
                                 "http://dbpedia.org/resource/International_draughts", "http://dbpedia.org/resource/Yot\u00e9",
                                 "http://dbpedia.org/resource/Halma", "http://dbpedia.org/resource/Lasca",
                                 "http://dbpedia.org/resource/Russian_draughts", "http://dbpedia.org/resource/Fangqi",
                                 "http://dbpedia.org/resource/Four_Fronts", "http://dbpedia.org/resource/Jungle_(board_game)",
                                 "http://dbpedia.org/resource/English_draughts", "http://dbpedia.org/resource/Morabaraba",
                                 "http://dbpedia.org/resource/Conspirateurs", "http://dbpedia.org/resource/Camelot_(board_game)",
                                 "http://dbpedia.org/resource/Choko_(game)", "http://dbpedia.org/resource/Lines_of_Action",
                                 "http://dbpedia.org/resource/The_Duke_(board_game)"]}}
    data_8 = {
        "template": " SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> . ?uri <%(e_to_e_out_2)s> <%(e_out_2*)s> . } ",
        "template_id": 8, "n_entities": 2, "type": "vanilla", "max": 100,
        "query": " SELECT DISTINCT ?uri WHERE {?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Board_game> . ?uri <http://dbpedia.org/ontology/genre> <http://dbpedia.org/resource/Abstract_strategy_game> . } ",
        "_id": "2d438a28f9e34958846545252a721fad", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
        "mapping": {"e_to_e_out": "http://dbpedia.org/property/genre", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                    "e_out": "http://dbpedia.org/resource/Board_game", "e_to_e_out_2": "http://dbpedia.org/ontology/genre",
                    "e_out_2*": "http://dbpedia.org/resource/Abstract_strategy_game"},
        "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out": "http://dbpedia.org/ontology/MusicGenre", "e_to_e_out_2": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out_2*": "http://dbpedia.org/ontology/MusicGenre"},
        "answer_type": ["http://dbpedia.org/ontology/Activity", "http://dbpedia.org/ontology/Sport",
                        "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/VideoGame"], "answer_num": 41, "answer": {
            "uri": ["http://dbpedia.org/resource/Chess", "http://dbpedia.org/resource/Chinese_checkers",
                    "http://dbpedia.org/resource/Reversi", "http://dbpedia.org/resource/Shogi",
                    "http://dbpedia.org/resource/Abalone_(board_game)", "http://dbpedia.org/resource/Fanorona",
                    "http://dbpedia.org/resource/Hex_(board_game)", "http://dbpedia.org/resource/Nine_Men's_Morris",
                    "http://dbpedia.org/resource/Xiangqi", "http://dbpedia.org/resource/Epaminondas_(game)",
                    "http://dbpedia.org/resource/Renju", "http://dbpedia.org/resource/Arimaa",
                    "http://dbpedia.org/resource/GIPF_(game)", "http://dbpedia.org/resource/YINSH",
                    "http://dbpedia.org/resource/Tori_shogi", "http://dbpedia.org/resource/Tafl_games",
                    "http://dbpedia.org/resource/DVONN", "http://dbpedia.org/resource/Janggi",
                    "http://dbpedia.org/resource/Dablot_Prejjesne", "http://dbpedia.org/resource/Chu_shogi",
                    "http://dbpedia.org/resource/Ludus_latrunculorum", "http://dbpedia.org/resource/Terrace_(board_game)",
                    "http://dbpedia.org/resource/Breakthru_(board_game)", "http://dbpedia.org/resource/Alquerque",
                    "http://dbpedia.org/resource/Draughts", "http://dbpedia.org/resource/Go_(game)",
                    "http://dbpedia.org/resource/International_draughts", "http://dbpedia.org/resource/Yot\u00e9",
                    "http://dbpedia.org/resource/Halma", "http://dbpedia.org/resource/Lasca",
                    "http://dbpedia.org/resource/Russian_draughts", "http://dbpedia.org/resource/Fangqi",
                    "http://dbpedia.org/resource/Four_Fronts", "http://dbpedia.org/resource/Jungle_(board_game)",
                    "http://dbpedia.org/resource/English_draughts", "http://dbpedia.org/resource/Morabaraba",
                    "http://dbpedia.org/resource/Conspirateurs", "http://dbpedia.org/resource/Camelot_(board_game)",
                    "http://dbpedia.org/resource/Choko_(game)", "http://dbpedia.org/resource/Lines_of_Action",
                    "http://dbpedia.org/resource/The_Duke_(board_game)"]}}
    data_11 = {
        "template": " SELECT DISTINCT ?uri WHERE { ?x <%(e_in_to_e_in_out)s> <%(e_in_out)s> . ?x <%(e_in_to_e)s> ?uri  }",
        "template_id": 11, "n_entities": 1, "type": "vanilla",
        "equal": ["e_in_to_e_in_out", "e_in_to_e"], "max": 100,
        "query": " SELECT DISTINCT ?uri WHERE { ?x <http://dbpedia.org/ontology/location> <http://dbpedia.org/resource/North_America> . ?x <http://dbpedia.org/ontology/location> ?uri  }",
        "_id": "58de057f78954500bab909cf52ef0dfc", "corrected": "false",
        "entity": "http://dbpedia.org/resource/North_America",
        "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/location", "class_uri": "http://dbpedia.org/ontology/Continent", "e_in_to_e_in_out": "http://dbpedia.org/ontology/location", "e_in_out": "http://dbpedia.org/resource/North_America"},
        "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing", "e_in_to_e_in_out": "http://www.w3.org/2002/07/owl#Thing", "e_in_out": "http://dbpedia.org/ontology/Continent"},
        "answer_type": ["http://dbpedia.org/ontology/Country", "http://dbpedia.org/ontology/Place", "http://dbpedia.org/ontology/PopulatedPlace", "http://dbpedia.org/ontology/Location", "http://dbpedia.org/ontology/Continent"],
         "answer_num": 11,
         "answer": {"uri": ["http://dbpedia.org/resource/North_America", "http://dbpedia.org/resource/California", "http://dbpedia.org/resource/San_Francisco", "http://dbpedia.org/resource/United_States", "http://dbpedia.org/resource/Mexico", "http://dbpedia.org/resource/London", "http://dbpedia.org/resource/United_Kingdom", "http://dbpedia.org/resource/Europe", "http://dbpedia.org/resource/Florida", "http://dbpedia.org/resource/Sanford,_Florida", "http://dbpedia.org/resource/Minnesota"]}}
    data_15 = {"template": " SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri . <%(e_in_2)s> <%(e_in_to_e)s> ?uri . } ",
               "template_id": 15, "n_entities": 2, "type": "vanilla", "max": 100,
               "query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines> <http://dbpedia.org/ontology/sport> ?uri . <http://dbpedia.org/resource/Harvest_Christian_Academy_(Honduras)> <http://dbpedia.org/ontology/sport> ?uri . } ",
               "_id": "00b00d5cab884a92a65b88b60c365c12", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
               "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/sport", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                           "e_in": "http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines",
                           "e_in_2": "http://dbpedia.org/resource/Harvest_Christian_Academy_(Honduras)"},
               "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                                "e_in": "http://dbpedia.org/ontology/School", "e_in_2": "http://dbpedia.org/ontology/School"},
               "answer_type": ["http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/VideoGame",
                               "http://dbpedia.org/ontology/Sport", "http://dbpedia.org/ontology/Activity"], "answer_num": 5,
               "answer": {"uri": ["http://dbpedia.org/resource/Badminton", "http://dbpedia.org/resource/Basketball",
                                  "http://dbpedia.org/resource/Chess", "http://dbpedia.org/resource/Tennis",
                                  "http://dbpedia.org/resource/Volleyball"]}}
    data_16 = {"template": " SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri . <%(e_in_2*)s> <%(e_in_to_e_2)s> ?uri . } ",
               "template_id": 16, "n_entities": 2, "type": "vanilla", "max": 100,
               "query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines> <http://dbpedia.org/ontology/sport> ?uri . <http://dbpedia.org/resource/All_Assam_Chess_Association> <http://dbpedia.org/property/purpose> ?uri . } ",
               "_id": "382226066a334d76b0f34744cd8b00a7", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
               "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/sport", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                           "e_in": "http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines",
                           "e_in_to_e_2": "http://dbpedia.org/property/purpose",
                           "e_in_2*": "http://dbpedia.org/resource/All_Assam_Chess_Association"},
               "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                                "e_in": "http://dbpedia.org/ontology/School", "e_in_to_e_2": "http://www.w3.org/2002/07/owl#Thing",
                                "e_in_2*": "http://dbpedia.org/ontology/Organisation"},
               "answer_type": ["http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/Sport",
                               "http://dbpedia.org/ontology/VideoGame", "http://dbpedia.org/ontology/Activity"], "answer_num": 1,
               "answer": {"uri": ["http://dbpedia.org/resource/Chess"]}}
    data_101 = {"template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { ?uri <%(e_to_e_out)s> <%(e_out)s> . } ",
                "template_id": 101, "n_entities": 1, "type": "count", "max": 100,
                "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { ?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Board_game> . } ",
                "_id": "ef78c4baa0e645149ffb64a00a1f325b", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
                "mapping": {"e_to_e_out": "http://dbpedia.org/property/genre", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                            "e_out": "http://dbpedia.org/resource/Board_game"},
                "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing",
                                 "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                                 "e_out": "http://dbpedia.org/ontology/MusicGenre"},
                "answer_type": ["http://dbpedia.org/ontology/Activity", "http://dbpedia.org/ontology/Sport",
                                "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/VideoGame"], "answer_num": -1,
                "answer": {"uri": ["137"]}}
    data_102 = {"template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri . } ", "template_id": 102,
                "n_entities": 1, "type": "count", "max": 100,
                "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { <http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines> <http://dbpedia.org/ontology/sport> ?uri . } ",
                "_id": "5c16833273134cc684d22d4779094f6f", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
                "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/sport", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                            "e_in": "http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines"},
                "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing",
                                 "class_uri": "http://www.w3.org/2002/07/owl#Thing", "e_in": "http://dbpedia.org/ontology/School"},
                "answer_type": ["http://dbpedia.org/ontology/Activity", "http://dbpedia.org/ontology/Sport",
                                "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/VideoGame"], "answer_num": -1,
                "answer": {"uri": ["13"]}}
    data_103 = npr.choice([{
        "template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri . } ", "template_id": 103, "n_entities": 1, "type": "count", "max": 100, "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { <http://dbpedia.org/resource/Qazi_Touqeer> <http://dbpedia.org/property/origin> ?x . ?x <http://dbpedia.org/property/label> ?uri . } ", "_id": "c580fb02cfe64144a7f480a252769fed", "corrected": "false", "entity": "http://dbpedia.org/resource/Buddhism", "mapping": {"e_in_to_e": "http://dbpedia.org/property/label", "class_uri": "http://dbpedia.org/ontology/Country", "e_in_in_to_e_in": "http://dbpedia.org/property/origin", "e_in_in": "http://dbpedia.org/resource/Qazi_Touqeer"}, "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing", "e_in_in_to_e_in": "http://www.w3.org/2002/07/owl#Thing", "e_in_in": "http://dbpedia.org/ontology/Singer"}, "answer_type": ["http://dbpedia.org/ontology/Country", "http://dbpedia.org/ontology/EthnicGroup"], "answer_num": -1, "answer": {"uri": ["8"]}}, {
            "template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri . } ", "template_id": 103, "n_entities": 1, "type": "count", "max": 100, "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { <http://dbpedia.org/resource/Shingo_La> <http://dbpedia.org/ontology/location> ?x . ?x <http://dbpedia.org/property/label> ?uri . } ", "_id": "00a05db68b8f407ea5bbe654f478328e", "corrected": "false", "entity": "http://dbpedia.org/resource/Buddhism", "mapping": {"e_in_to_e": "http://dbpedia.org/property/label", "class_uri": "http://dbpedia.org/ontology/Country", "e_in_in_to_e_in": "http://dbpedia.org/ontology/location", "e_in_in": "http://dbpedia.org/resource/Shingo_La"}, "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing", "e_in_in_to_e_in": "http://www.w3.org/2002/07/owl#Thing", "e_in_in": "http://dbpedia.org/ontology/MountainPass"}, "answer_type": ["http://dbpedia.org/ontology/Country", "http://dbpedia.org/ontology/EthnicGroup"], "answer_num": -1, "answer": {"uri": ["8"]}}])
    data_106 = {
        "template": "SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { ?x <%(e_out_to_e_out_out)s> <%(e_out_out)s> . ?uri <%(e_to_e_out)s> ?x . } ",
        "template_id": 106, "n_entities": 1, "type": "count", "max": 100,
        "query": "SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { ?x <http://dbpedia.org/property/sovereigntyType> <http://dbpedia.org/resource/History_of_Norway> . ?uri <http://dbpedia.org/property/country> ?x . } ",
        "_id": "9af4c44f353a4b27afd86a8d2c78082f", "corrected": "false", "entity": "http://dbpedia.org/resource/Nobel_Prize",
        "mapping": {"e_to_e_out": "http://dbpedia.org/property/country",
                    "class_uri": "http://dbpedia.org/ontology/TelevisionShow",
                    "e_out_to_e_out_out": "http://dbpedia.org/property/sovereigntyType",
                    "e_out_out": "http://dbpedia.org/resource/History_of_Norway"},
        "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing",
                         "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out_to_e_out_out": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out_out": "http://www.w3.org/2002/07/owl#Thing"},
        "answer_type": ["http://dbpedia.org/ontology/Award", "http://dbpedia.org/ontology/Organization",
                        "http://dbpedia.org/ontology/TelevisionShow"], "answer_num": -1,
        "answer": {"uri": ["2298"]}}
    data_107 = {
        "template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { ?uri <%(e_to_e_out)s> <%(e_out)s> . ?uri <%(e_to_e_out)s> <%(e_out_2)s> . } ",
        "template_id": 107, "n_entities": 2, "type": "count", "max": 100,
        "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE { ?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Board_game> . ?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Abstract_strategy_game> . } ",
        "_id": "cf487f51f89842d4abeeaa808396d5e5", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess",
        "mapping": {"e_to_e_out": "http://dbpedia.org/property/genre", "class_uri": "http://dbpedia.org/ontology/VideoGame",
                    "e_out": "http://dbpedia.org/resource/Board_game",
                    "e_out_2": "http://dbpedia.org/resource/Abstract_strategy_game"},
        "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out": "http://dbpedia.org/ontology/MusicGenre", "e_out_2": "http://dbpedia.org/ontology/MusicGenre"},
        "answer_type": ["http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/Sport",
                        "http://dbpedia.org/ontology/VideoGame", "http://dbpedia.org/ontology/Activity"], "answer_num": -1,
        "answer": {"uri": ["41"]}}
    data_108 = {
        "template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> . ?uri <%(e_to_e_out_2)s> <%(e_out_2*)s> . } ",
        "template_id": 108, "n_entities": 2, "type": "count", "max": 100,
        "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE {?uri <http://dbpedia.org/property/director> <http://dbpedia.org/resource/Orson_Welles> . ?uri <http://dbpedia.org/ontology/producer> <http://dbpedia.org/resource/Orson_Welles> . } ",
        "_id": "f275d3c2b28f44f397ed52c892139617", "corrected": "false", "entity": "http://dbpedia.org/resource/Citizen_Kane",
        "mapping": {"e_to_e_out": "http://dbpedia.org/property/director", "class_uri": "http://dbpedia.org/ontology/Archive",
                    "e_out": "http://dbpedia.org/resource/Orson_Welles", "e_to_e_out_2": "http://dbpedia.org/ontology/producer",
                    "e_out_2*": "http://dbpedia.org/resource/Orson_Welles"},
        "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out": "http://dbpedia.org/ontology/Actor", "e_to_e_out_2": "http://www.w3.org/2002/07/owl#Thing",
                         "e_out_2*": "http://dbpedia.org/ontology/Actor"},
        "answer_type": ["http://dbpedia.org/ontology/Film", "http://dbpedia.org/ontology/Wikidata:Q11424",
                        "http://dbpedia.org/ontology/Work", "http://dbpedia.org/ontology/Archive"],
        "answer_num": -1, "answer": {"uri": ["15"]}}
    data_108 = {
        "template": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> . ?uri <%(e_to_e_out_2)s> <%(e_out_2*)s> . } ",
        "template_id": 108, "n_entities": 2, "type": "count", "max": 100,
        "query": " SELECT (COUNT(DISTINCT ?uri) as ?uri) WHERE {?uri <http://dbpedia.org/property/distributor> <http://dbpedia.org/resource/RKO_Pictures> . ?uri <http://dbpedia.org/property/cinematography> <http://dbpedia.org/resource/Gregg_Toland> . } ",
        "_id": "fb2ffa4189e348e990d5247f840366b8", "corrected": "false", "entity": "http://dbpedia.org/resource/Citizen_Kane",
        "mapping": {"e_to_e_out": "http://dbpedia.org/property/distributor",
                    "class_uri": "http://dbpedia.org/ontology/Archive", "e_out": "http://dbpedia.org/resource/RKO_Pictures",
                    "e_to_e_out_2": "http://dbpedia.org/property/cinematography",
                    "e_out_2*": "http://dbpedia.org/resource/Gregg_Toland"},
        "mapping_type": {"e_to_e_out": "http://www.w3.org/2002/07/owl#Thing",
                         "class_uri": "http://www.w3.org/2002/07/owl#Thing", "e_out": "http://dbpedia.org/ontology/Company",
                         "e_to_e_out_2": "http://www.w3.org/2002/07/owl#Thing", "e_out_2*": "http://dbpedia.org/ontology/Person"},
        "answer_type": ["http://dbpedia.org/ontology/Film", "http://dbpedia.org/ontology/Wikidata:Q11424", "http://dbpedia.org/ontology/Work", "http://dbpedia.org/ontology/Archive"],
        "answer_num": -1, "answer": {"uri": ["9"]}}

    '''
        Start of 300 series. None of them have been implemented till now
    '''
    data_301 = {'template': ' SELECT DISTINCT ?uri WHERE {?uri <%(e_to_e_out)s> <%(e_out)s> . ?uri rdf:type <%(class_uri)s> . } ',
         'template_id': 301,
         'n_entities': 1,
         'type': 'vanilla',
         'max': 100,
         'query': ' SELECT DISTINCT ?uri WHERE {?uri <http://dbpedia.org/property/genre> <http://dbpedia.org/resource/Abstract_strategy_game> . ?uri rdf:type <http://dbpedia.org/ontology/VideoGame> . } ',
         '_id': '30321ccbd1544930bc1bce2fdc734ba8',
         'corrected': 'false',
         'entity': 'http://dbpedia.org/resource/Chess',
         'mapping': {'e_to_e_out': 'http://dbpedia.org/property/genre',
          'class_uri': 'http://dbpedia.org/ontology/VideoGame',
          'e_out': 'http://dbpedia.org/resource/Abstract_strategy_game'},
         'mapping_type': {'e_to_e_out': 'http://www.w3.org/2002/07/owl#Thing',
          'class_uri': 'http://www.w3.org/2002/07/owl#Thing',
          'e_out': 'http://dbpedia.org/ontology/MusicGenre'},
         'answer_type': ['http://dbpedia.org/ontology/Sport',
          'http://dbpedia.org/ontology/VideoGame',
          'http://dbpedia.org/ontology/Game',
          'http://dbpedia.org/ontology/Activity'],
         'answer_num': 36,
         'answer': {'uri': ['http://dbpedia.org/resource/Chess',
           'http://dbpedia.org/resource/Chinese_checkers',
           'http://dbpedia.org/resource/Reversi',
           'http://dbpedia.org/resource/Shogi',
           'http://dbpedia.org/resource/Fanorona',
           'http://dbpedia.org/resource/Hex_(board_game)',
           "http://dbpedia.org/resource/Nine_Men's_Morris",
           'http://dbpedia.org/resource/Xiangqi',
           'http://dbpedia.org/resource/Epaminondas_(game)',
           'http://dbpedia.org/resource/Arimaa',
           'http://dbpedia.org/resource/GIPF_(game)',
           'http://dbpedia.org/resource/YINSH',
           'http://dbpedia.org/resource/Terakh',
           'http://dbpedia.org/resource/Connect_Four',
           'http://dbpedia.org/resource/DVONN',
           'http://dbpedia.org/resource/Janggi',
           'http://dbpedia.org/resource/Dablot_Prejjesne',
           'http://dbpedia.org/resource/Connect_4x4',
           'http://dbpedia.org/resource/Chu_shogi',
           'http://dbpedia.org/resource/Ludus_latrunculorum',
           'http://dbpedia.org/resource/Terrace_(board_game)',
           'http://dbpedia.org/resource/Breakthru_(board_game)',
           'http://dbpedia.org/resource/Alquerque',
           'http://dbpedia.org/resource/Go_(game)',
           'http://dbpedia.org/resource/International_draughts',
           'http://dbpedia.org/resource/Yoté',
           'http://dbpedia.org/resource/Halma',
           'http://dbpedia.org/resource/Fangqi',
           'http://dbpedia.org/resource/Spot:_The_Video_Game',
           'http://dbpedia.org/resource/Four_Fronts',
           'http://dbpedia.org/resource/Jungle_(board_game)',
           'http://dbpedia.org/resource/Morabaraba',
           'http://dbpedia.org/resource/Camelot_(board_game)',
           'http://dbpedia.org/resource/Choko_(game)',
           'http://dbpedia.org/resource/Lines_of_Action',
           'http://dbpedia.org/resource/The_Duke_(board_game)']}}
    data_302 = {'template': ' SELECT DISTINCT ?uri WHERE { <%(e_in)s> <%(e_in_to_e)s> ?uri  . ?uri rdf:type <%(class_uri)s> . } ',
 'template_id': 302,
 'n_entities': 1,
 'type': 'vanilla',
 'max': 100,
 'query': ' SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines> <http://dbpedia.org/ontology/sport> ?uri  . ?uri rdf:type <http://dbpedia.org/ontology/VideoGame> . } ',
 '_id': '77cdc46939c549b2a1b0d547837911f5',
 'corrected': 'false',
 'entity': 'http://dbpedia.org/resource/Chess',
 'mapping': {'e_in_to_e': 'http://dbpedia.org/ontology/sport',
  'class_uri': 'http://dbpedia.org/ontology/VideoGame',
  'e_in': 'http://dbpedia.org/resource/Polytechnic_University_of_the_Philippines'},
 'mapping_type': {'e_in_to_e': 'http://www.w3.org/2002/07/owl#Thing',
  'class_uri': 'http://www.w3.org/2002/07/owl#Thing',
  'e_in': 'http://dbpedia.org/ontology/School'},
 'answer_type': ['http://dbpedia.org/ontology/Sport',
  'http://dbpedia.org/ontology/VideoGame',
  'http://dbpedia.org/ontology/Game',
  'http://dbpedia.org/ontology/Activity'],
 'answer_num': 2,
 'answer': {'uri': ['http://dbpedia.org/resource/Chess',
   'http://dbpedia.org/resource/Flying_disc_games']}}
    data_303 = {
        "template": " SELECT DISTINCT ?uri WHERE { <%(e_in_in)s> <%(e_in_in_to_e_in)s> ?x . ?x <%(e_in_to_e)s> ?uri . ?x rdf:type <%(class_x)s> } ", "template_id": 303, "n_entities": 1, "type": "vanilla", "max": 100, "query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/1999_Formula_Shell_Zoom_Masters_season> <http://dbpedia.org/property/school> ?x . ?x <http://dbpedia.org/ontology/sport> ?uri . ?x rdf:type <http://dbpedia.org/ontology/School> } ", "_id": "5c0e70a2299f4a51ae56b1ec52d7d595", "corrected": "false", "entity": "http://dbpedia.org/resource/Chess", "mapping": {"e_in_to_e": "http://dbpedia.org/ontology/sport", "class_uri": "http://dbpedia.org/ontology/VideoGame", "e_in_in_to_e_in": "http://dbpedia.org/property/school", "class_x": "http://dbpedia.org/ontology/School", "e_in_in": "http://dbpedia.org/resource/1999_Formula_Shell_Zoom_Masters_season"}, "mapping_type": {"e_in_to_e": "http://www.w3.org/2002/07/owl#Thing", "class_uri": "http://www.w3.org/2002/07/owl#Thing", "e_in_in_to_e_in": "http://www.w3.org/2002/07/owl#Thing", "class_x": "http://www.w3.org/2002/07/owl#Thing", "e_in_in": "http://dbpedia.org/ontology/FootballLeagueSeason"}, "answer_type": ["http://dbpedia.org/ontology/Sport", "http://dbpedia.org/ontology/VideoGame", "http://dbpedia.org/ontology/Game", "http://dbpedia.org/ontology/Activity"], "answer_num": 13, "answer": {"uri": ["http://dbpedia.org/resource/Archery", "http://dbpedia.org/resource/Badminton", "http://dbpedia.org/resource/Basketball", "http://dbpedia.org/resource/Chess", "http://dbpedia.org/resource/Tennis", "http://dbpedia.org/resource/Ultimate_(sport)", "http://dbpedia.org/resource/Volleyball", "http://dbpedia.org/resource/Water_polo", "http://dbpedia.org/resource/Football", "http://dbpedia.org/resource/Track_and_field", "http://dbpedia.org/resource/Flying_disc_games", "http://dbpedia.org/resource/Swimming_(sport)", "http://dbpedia.org/resource/Combat_sport"]}}




    # verb = Verbalizer(303)
    # data = verb.verbalize(data_303)
    #
    # print(data['question_verbalized'])

    test_template(id=411, skip=98, show=True)
