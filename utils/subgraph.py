from collections import namedtuple
from pprint import pprint

from utils.goodies import *


PredEntTuple = namedtuple('PredEntTuple', 'pred ent type')
PredEntTuple.__new__.__defaults__ = (None, None, '')


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
    def entities_(self):
        try:
            assert self.__verify__()
        except AssertionError:
            raise InvalidSubgraphPreds
        return [subgraph for _, subgraphs in self.items() for subgraph in subgraphs]

    @property
    def predicates(self):
        try:
            assert self.__verify__()
        except AssertionError:
            raise InvalidSubgraphPreds

        return [pred for pred, _ in self.items()]


class Subgraph(dict):

    def __init__(self, _uri=None, _type=None):
        super(Subgraph, self).__init__()
        self['uri'] = _uri if _uri else ''
        self['type'] = _type if _type else ''
        self['left'], self['right'] = SubgraphPreds(), SubgraphPreds()

    def find(self, _uri, _caller, _type=None, _new=True):
        """


            Expected to find and return corresponding object of this uri.

            First checks if the caller has the given uri.
                If so, returns caller.
                Else: check in self.

            If not found, creates a new one.


            @TODO: Implement logic to find from depth 2 (or rather, recursively)
            :param _uri: str
            :returns Subgraph object
        """
        if _uri == _caller:
            return _caller

        for subg in self.entities_ + [self]:
            if _uri == subg:
                return subg
        else:
            if not _new:
                raise NoSubgraphFoundError("%s doesn't exist for this subgraph")
            else:
                return Subgraph(_uri, _type if not _type == None else '')

    def __eq__(self, other):
        """
            Overloading internal a == b op
        """
        if isinstance(other, str):
            return other == self.uri
        elif isinstance(other, Subgraph):
            return other.uri == self.uri
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.uri)

    # @staticmethod
    # def uniques(subgraphs):
    #     uniques = []
    #     for subg in subgraphs:
    #         if subg not in uniques: uniques.append(subg)
    #     return uniques

    @property
    def uri(self):
        return self['uri']

    @property
    def type(self):
        return self['type']

    @property
    def left(self):
        return self['left']

    @property
    def right(self):
        return self['right']

    # @TODO: the below presumes 1hop. not 2.
    @property
    def entities(self):
        return list(set(self.left.entities + self.right.entities))

    @property
    def entities_(self):
        return list(set(self.left.entities_ + self.right.entities_))

    @property
    def predicates(self):
        return list(set(self.left.predicates + self.right.predicates))

    def insert(self, _data, _origin=None, _outgoing=True):
        """
            Will put the data properly in left/right based on direction

            :param _data: list of PredEntTuple
            :param _origin: where in the graph should these be put in.
            :param _outgoing: bool (True -> Right; False -> Left)
        """

        # If no origin specified, assume self.
        if not _origin:
            _origin = self
        elif type(_origin) == str:
            _origin = self.find(_origin, _caller=self, _new=False)

        # Select which SubgraphPreds to choose from (left/right)
        src = _origin.right if _outgoing else _origin.left

        for datum in _data:
            # Find the predicate in src, ent in self.
            pred = src.setdefault(datum.pred, [])
            ent = _origin.find(datum.ent, _caller=self, _new=True, _type=datum.type)

            # Check if the entity doesn't already exist for this list
            if not datum.ent in pred:
                src[datum.pred].append(ent)


if __name__ == "__main__":
    a = Subgraph('dbo:Obama')

    data_out = [PredEntTuple(pred='dbp:prez', ent='dbr:US', type="country"),
                PredEntTuple(pred='dbp:bornin', ent='dbr:Chicago', type="city"),
                PredEntTuple(pred='dbp:left', ent='2014', type="year"),
                PredEntTuple(pred='dbp:spouse', ent='dbr:Michelle', type="person"),
                PredEntTuple(pred='dbp:left', ent='2010', type="year")]

    data_in = [PredEntTuple(pred='dbp:son', ent='dbr:BiggerObama', type="person"),
               PredEntTuple(pred='dbp:spouse', ent='dbr:Michelle', type="person"),
               PredEntTuple(pred='dbp:father', ent='dbr:Wut', type="nothing"),
               PredEntTuple(pred='dbp:hasResident', ent='dbo:Obama', type="person")]

    a.insert(data_out, _outgoing=True)
    a.insert(data_in, _outgoing=False)

    pprint(a)
    print("Entities: ", a.entities)
    print("Predicates: ", a.predicates)
    print("Entities: ")
    pprint(a.entities_)

    input("Press enter to try putting in a two triple thing")
    hop2_data = [PredEntTuple(pred='dbp:continent', ent='dbr:NorthAmerica')]
    a.insert(hop2_data, _origin='dbr:US', _outgoing=True)

    pprint(a)
