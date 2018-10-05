import numpy as np
from collections import namedtuple
from pprint import pprint

from utils.exceptions import *


PredEntTuple = namedtuple('PredEntTuple', 'pred ent')


class SubgraphPreds(dict):
    """
        Supposed to look like this:
            {'dbp:prez': [{'uri': 'dbr:US', 'left': {}, 'right': {}}],
             'dbp:bornin': [{'uri': 'dbr:Chicago', 'left': {}, 'right': {}}],
             'dbp:left': [{'uri': '2014', 'left': {}, 'right': {}},
              {'uri': '2010', 'left': {}, 'right': {}}]}

    """

    def __verify__(self):
        for key, value in self.items():
            if not type(value) == list:
                return False
        return True

    @property
    def entities(self):
        try:
            assert self.__verify__()
        except AssertionError:
            raise InvalidSubgraphPreds
        return [subgraph.uri for _, subgraphs in self.items() for subgraph in subgraphs]

    @property
    def predicates(self):
        try:
            assert self.__verify__()
        except AssertionError:
            raise InvalidSubgraphPreds

        return [pred for pred, _ in self.items()]


class Subgraph(dict):

    def __init__(self, _uri=None):
        super(Subgraph, self).__init__()
        self['uri'] = _uri if _uri else ''
        self['left'], self['right'] = SubgraphPreds(), SubgraphPreds()

    def echo(self, _echo='red'):
        print(_echo)

    def __eq__(self, other):
        """
            Overloading internal a == b op
        """
        print("eq")
        if isinstance(other, str):
            return other == self.uri
        elif isinstance(other, Subgraph):
            return other.uri == self.uri
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def uri(self):
        return self['uri']

    @property
    def left(self):
        return self['left']

    @property
    def right(self):
        return self['right']

    @property
    def entities(self):
        return self.left.entities + self.right.entities

    @property
    def predicates(self):
        return self.left.predicates + self.right.predicates

    def insert(self, _data, _outgoing=True):
        """
            Will put the data properly in left/right based on direction

            :param _data: list of PredEntTuple
            :param _outgoing: bool (True -> Right; False -> Left)
        """
        src = self.right if _outgoing else self.left

        for datum in _data:
            pred = src.setdefault(datum.pred, [])
            print("pred: ", pred)
            if not datum.ent in pred:
                src[datum.pred].append(Subgraph(datum.ent))


if __name__ == "__main__":
    # Make a 1 level subgraph out of it
    a = Subgraph('dbo:Obama')

    data_out = [PredEntTuple(pred='dbp:prez', ent='dbr:US'),
                PredEntTuple(pred='dbp:bornin', ent='dbr:Chicago'),
                PredEntTuple(pred='dbp:left', ent='2014'),
                PredEntTuple(pred='dbp:left', ent='2010')]

    data_in = [PredEntTuple(pred='dbp:son', ent='dbr:BiggerObama'),
               PredEntTuple(pred='dbp:spouse', ent='dbr:Michelle'),
               PredEntTuple(pred='dbp:father', ent='dbr:Wut')]

    a.insert(data_out, _outgoing=True)
    a.insert(data_in, _outgoing=False)

    pprint(a)
    print("Entities: ", a.entities)
    print("Predicates: ", a.predicates)