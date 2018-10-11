from collections import namedtuple
from pprint import pprint

from utils.goodies import *

VAR_HOP1_RIGHT = ['e_out', 'e_to_e_out']
VAR_HOP1_RIGHT_DUP = ['e_out_2*', 'e_to_e_out_2']
VAR_HOP1_RIGHT_DOUBLE = ['e_out_2']
VAR_HOP1_LEFT = ['e_in', 'e_in_to_e']
VAR_HOP1_LEFT_DUP = ['e_in_2*', 'e_in_to_e_2']
VAR_HOP1_LEFT_DOUBLE = ['e_in_2']
VAR_OTHERS = ['e', 'class_uri', 'class_x']
VAR_HOP2_RIGHT = ['e_out_out', 'e_out_in', 'e_out_to_e_out_out', 'e_out_in_to_e_out']
VAR_HOP2_LEFT = ['e_in_in', 'e_in_out', 'e_in_in_to_e_in', 'e_in_to_e_in_out']
VAR_HOP1 = VAR_HOP1_LEFT + VAR_HOP1_RIGHT + VAR_HOP1_LEFT_DUP + VAR_HOP1_RIGHT_DUP + \
           VAR_HOP1_LEFT_DOUBLE + VAR_HOP1_RIGHT_DOUBLE
VAR_HOP2 = VAR_HOP2_LEFT + VAR_HOP2_RIGHT
VARS = VAR_HOP1 + VAR_HOP2 + VAR_OTHERS
REC_RIGHT_VARS = {'e_out_out': 'e_out', 'e_out_to_e_out_out': 'e_to_e_out', 'e_out': 'e',
                  'e_out_in': 'e_in', 'e_out_in_to_e_out': 'e_in_to_e'}
REC_LEFT_VARS = {'e_in_in': 'e_in', 'e_in': 'e', 'e_in_in_to_e_in': 'e_in_to_e',
                 'e_in_to_e_in_out': 'e_to_e_out', 'e_in_out': 'e_out'}

PredEntTuple = namedtuple('PredEntTuple', 'pred ent type')
PredEntTuple.__new__.__defaults__ = (None, None, '')


def take_one(_map, _data, _key):
    """
        Make copies of _map with given _data, taking elements from _data **two** at a time.
    :param _map: dict
    :param _data: list of str/Subgraph objs
    :param _key: str
    :return: list of dict
    """
    _maps = []

    for ent in _data:
        _map = _map.copy()
        _map[_key] = ent.uri if isinstance(ent, Subgraph) else ent
        _maps.append(_map)

    return _maps


def take_two(_map, _data, _key_one, _key_two):
    """
        Make copies of _map with given _data, taking elements from _data **two** at a time.
    :param _map: dict
    :param _data: list of str/Subgraph objs
    :param _key_one: str
    :param _key_two: str
    :return: list of dict
    """
    _maps = []

    for i in range(len(_data)):
        for j in range(len(_data))[i:]:
            ent_a, ent_b = _data[i], _data[j]
            _map = _map.copy()
            _map[_key_one] = ent_a.uri if isinstance(ent_a, Subgraph) else ent_a
            _map[_key_two] = ent_b.uri if isinstance(ent_b, Subgraph) else ent_b
            _maps.append(_map)

    return _maps


def permute_dicts(_d1, _d2, _optional=True):
    """
        Given two list of dicts, it creates a list of dicts having a combination of both values.

        Assumption:
            - a list's dicts will have same keys
            - if two dict have common keys, only permute elements whose values for common keys are same.

        @TODO: also input maps to use this func to merge recursively generated dicts

    :param _d1: list of dicts
    :param _d2: list of dicts
    :param _optional: bool: flag which if False, will return nothing if one of _d* is empty.
    :return: list of dicts
    """
    if not _optional and (len(_d1) == 0 or len(_d2) == 0):
        return []
    if len(_d1) == 0:
        return _d2
    elif len(_d2) == 0:
        return _d1

    # ALSO PUT MAP HERE
    keys1 = set(_d1[-1].keys())
    keys2 = set(_d2[-1].keys())
    common_keys = keys1 & keys2

    data = []

    for dict1 in _d1:
        for dict2 in _d2:
            if common_keys:  # If there are common keys, accept elements only if their values are same.
                disjoint = False
                for key in common_keys:
                    if dict1[key] != dict2[key]:
                        disjoint = True
                if disjoint:
                    continue

            new_dict = dict1.copy()
            new_dict.update(dict2)
            data.append(new_dict)

    return data


rev = lambda mapping: {v: k for k, v in mapping.items()}
change_keys_list = lambda data, mapping: [mapping[v] for v in data if v in mapping]
change_keys_dict = lambda data, mapping: {mapping[k]: v for k, v in data.items() if k in mapping}


class VarList(list):
    """
        Extends list to easy peasy compute a bunch of flags for a list of variables.
        To be used within Subgraph.get_mapping_for fn, generally.
    """

    def __init__(self, _vars, _constraints, _valcheck=True):
        super(VarList, self).__init__(_vars)

        self.constraints = _constraints

        if _valcheck:
            for var in self:  # Check if all vars make sense
                if var not in VARS:
                    raise UnknownVarFoundError("Var %s not known." % var)

    def filtered(self, src):
        return VarList([v for v in self if v in src], False)

    # def mapped(self, mapping):
    #     return VarList([mapping[v] for v in self if v in mapping], False)
    #
    # def map_to_skip_hop_right(self):
    #     return self.mapped(REC_RIGHT_VARS)
    #
    # def map_to_skip_hop_left(self):
    #     return self.mapped(REC_LEFT_VARS)
    #
    # def map_from_skip_hop_left(self):
    #     return self.mapped(rev(REC_RIGHT_VARS))
    #
    # def map_from_skip_hop_right(self):
    #     return self.mapped(rev(REC_LEFT_VARS))

    @lazy_property
    def one(self):
        return self.filtered(VAR_HOP1)

    @lazy_property
    def two(self):
        return self.filtered(VAR_HOP2)

    @lazy_property
    def right(self):
        return self.filtered(VAR_HOP2_RIGHT + VAR_HOP1_RIGHT + VAR_HOP1_RIGHT_DUP + VAR_HOP1_RIGHT_DOUBLE)

    @lazy_property
    def left(self):
        return self.filtered(VAR_HOP2_LEFT + VAR_HOP1_LEFT + VAR_HOP1_LEFT_DUP + VAR_HOP1_LEFT_DOUBLE)

    @lazy_property
    def dup(self):
        return self.filtered(VAR_HOP1_RIGHT_DUP + VAR_HOP1_LEFT_DUP)

    @lazy_property
    def double(self):
        return self.filtered(VAR_HOP1_RIGHT_DOUBLE + VAR_HOP1_LEFT_DOUBLE)

    @lazy_property
    def one_(self):
        return bool(self.one) > 0

    @lazy_property
    def two_(self):
        return bool(self.two)

    @lazy_property
    def right_(self):
        return bool(self.right)

    @lazy_property
    def left_(self):
        return bool(self.left)

    @lazy_property
    def dup_(self):
        return bool(self.dup)

    @lazy_property
    def double_(self):
        return bool(self.double)

    @lazy_property
    def hash(self):
        # @TODO: handle constraints while computing hash too!
        if len(self) == 0:
            return 0
        h = hash(self[0])
        for v in self[1:]:
            h ^= hash(v)
        return h


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
        self.mappings = {}

    def find(self, _uri, _caller, _type=None, _new=True):
        """
            Expected to find and return corresponding object of this uri.

            First checks if the caller has the given uri.
                If so, returns caller.
                Else: check in self.

            If not found, creates a new one.

            :param _uri: str
            :param _caller: subgraph obj which calls this fn. (Used to return _caller if it matches _uri)
            :param _type: str: class to which this uri belongs. Needed if we create a new obj and return
            :param _new: flag: if we want to return a new obj in case no older one is found.
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
                return Subgraph(_uri, _type if _type is not None else '')

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
            if datum.ent not in pred:
                src[datum.pred].append(ent)

    def _get_mapping_for_(self, _vars, _equal=None):
        """
            Returns a list of mapping fitting these vars, satisfying the equal condition.

            Logic: check which side of self should we start at (may be both).
            Function is recursive in nature!

            @TODO: fix equal constraints parsing
            @TODO: remove unnecessary variables upon exit

            Assumptions:
                - won't ask for _2 and _2* for any var in one call
                - won't ask for _2 of something without its original var.

        :param _vars: list of str: indicate variables that you want the mapping to consist of.
        :param _equal: only get mapping satisfying this constraint.
        :return: list of dicts.
        """

        _vars = VarList(_vars, _equal)

        right_maps = []
        left_maps = []

        if (_vars.right.dup_ and len(self.right.predicates) < 2) or (
                _vars.left.dup_ and len(self.left.predicates) < 2):
            return []

        """
            Logic for right side
        """
        if _vars.one.right_:

            for pred, ents in self.right.items():
                if _vars.right.double_ and len(ents) < 2:
                    continue

                _map = {'e_to_e_out': pred, 'e': self.uri}
                _maps = take_one(_map, ents, _key='e_out') if not _vars.right.double_ \
                    else take_two(_map, ents, _key_one='e_out', _key_two='e_out_2')

                if _vars.right.two_:
                    rec_right_maps = []
                    for ent in ents:
                        rec_right_maps += [change_keys_dict(x, rev(REC_RIGHT_VARS))
                                           for x in
                                           ent._get_mapping_for_(change_keys_list(_vars.right, REC_RIGHT_VARS))]

                    _maps = permute_dicts(_maps, rec_right_maps, _optional=False)

                right_maps += _maps

            if _vars.right.dup_:
                dup_right_maps = []

                for _map in right_maps:
                    for pred, ents in self.right.items():

                        if _map['e_to_e_out'] == pred:
                            continue

                        _map['e_to_e_out_2'] = pred
                        dup_right_maps += take_one(_map, ents, _key='e_out_2*')

                right_maps = dup_right_maps

        """
            Logic for left
        """
        if _vars.one.left_:

            for pred, ents in self.left.items():

                if _vars.left.double_ and len(ents) < 2:
                    continue

                _map = {'e_in_to_e': pred, 'e': self.uri}
                _maps = take_one(_map, ents, _key='e_in') if not _vars.left.double_ \
                    else take_two(_map, ents, _key_one='e_in', _key_two='e_in_2')

                if _vars.left.two_:
                    rec_left_maps = []
                    for ent in ents:
                        rec_left_maps += [change_keys_dict(x, rev(REC_LEFT_VARS)) for x
                                          in ent._get_mapping_for_(change_keys_list(_vars.right, REC_LEFT_VARS))]

                    _maps = permute_dicts(_maps, rec_left_maps, _optional=False)

                left_maps += _maps

            if _vars.left.dup_:
                dup_left_maps = []

                for _map in left_maps:
                    for pred, ents in self.left.items():

                        if _map['e_in_to_e'] == pred:
                            continue

                        _map['e_in_to_e_2'] = pred
                        dup_left_maps += take_one(_map, ents, _key='e_in_2*')

                left_maps = dup_left_maps

        mappings = permute_dicts(left_maps, right_maps)
        self.mappings[_vars.hash] = mappings
        return mappings

    def gen_maps(self, _vars, _equal=None):
        """
            Returns a list of mapping fitting these vars, satisfying the equal condition.

            Hash the params and see if we have it precomputed. If not, call _get_mapping_for_ fn and return op.

        :param _vars: list of str: indicate variables that you want the mapping to consist of.
        :param _equal: only get mapping satisfying this constraint.
        :return: list of dicts.
        """

        _var_obj = VarList(_vars, _equal)

        return self.mappings.get(_var_obj.hash, self._get_mapping_for_(_vars, _equal))


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
               PredEntTuple(pred='dbp:hasResident', ent='dbr:US', type="person")]

    a.insert(data_out, _outgoing=True)
    a.insert(data_in, _outgoing=False)

    hop2_data = [PredEntTuple(pred='dbp:continent', ent='dbr:NorthAmerica')]
    a.insert(hop2_data, _origin='dbr:US', _outgoing=True)
    #
    # print("Entities: ", a.entities)
    # print("Predicates: ", a.predicates)
    # print("Entities: ")
    #
    # pprint(a)

    maps = a.gen_maps(['e_out', 'e_out_out'])
    maps = a.gen_maps(['e_in', 'e_in_out'])
    pprint(maps)
