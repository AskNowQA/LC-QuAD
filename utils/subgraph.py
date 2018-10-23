from pprint import pprint
from utils.goodies import *

# @TODO: remove lazy properties, implement manual caching.

TYPE_BLACKLIST = ['owl:Thing', 'http://www.w3.org/2002/07/owl#Thing']

VAR_HOP1_RIGHT = ['e_out', 'e_to_e_out']
VAR_HOP1_RIGHT_DUP = ['e_out_2*', 'e_to_e_out_2']
VAR_HOP1_RIGHT_DOUBLE = ['e_out_2']
VAR_HOP1_LEFT = ['e_in', 'e_in_to_e']
VAR_HOP1_LEFT_DUP = ['e_in_2*', 'e_in_to_e_2']
VAR_HOP1_LEFT_DOUBLE = ['e_in_2']
VAR_CLASS = ['class_uri', 'class_x']
VAR_HOP2_RIGHT = ['e_out_out', 'e_out_in', 'e_out_to_e_out_out', 'e_out_in_to_e_out']
VAR_HOP2_LEFT = ['e_in_in', 'e_in_out', 'e_in_in_to_e_in', 'e_in_to_e_in_out']
VAR_OTHERS = ['uri'] + VAR_CLASS
VAR_HOP1 = VAR_HOP1_LEFT + VAR_HOP1_RIGHT + VAR_HOP1_LEFT_DUP + VAR_HOP1_RIGHT_DUP + \
           VAR_HOP1_LEFT_DOUBLE + VAR_HOP1_RIGHT_DOUBLE
VAR_HOP2 = VAR_HOP2_LEFT + VAR_HOP2_RIGHT
VARS = VAR_HOP1 + VAR_HOP2 + VAR_OTHERS
REC_RIGHT_VARS = {'e_out_out': 'e_out', 'e_out_to_e_out_out': 'e_to_e_out', 'e_out': 'uri',
                  'e_out_in': 'e_in', 'e_out_in_to_e_out': 'e_in_to_e', 'class_x': 'class_uri'}
REC_LEFT_VARS = {'e_in_in': 'e_in', 'e_in': 'uri', 'e_in_in_to_e_in': 'e_in_to_e',
                 'e_in_to_e_in_out': 'e_to_e_out', 'e_in_out': 'e_out', 'class_x': 'class_uri'}

PredEntTuple = namedtuple('PredEntTuple', 'pred ent type')
PredEntTuple.__new__.__defaults__ = (None, None, '')

# Some lambda functions
rev = lambda mapping: {v: k for k, v in mapping.items()}
change_keys_list = lambda data, mapping: [mapping[v] for v in data if v in mapping]
change_keys_dict = lambda data, mapping: {mapping[k]: v for k, v in data.items() if k in mapping}
hashable = lambda data, keys: "+++".join(str(data[key]) for key in keys)


def _take_one_(_map, _data, _key):
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


def _take_two_(_map, _data, _key_one, _key_two):
    """
        Make copies of _map with given _data, taking elements from _data **two** at a time.
    :param _map: dict
    :param _data: list of str/Subgraph objs
    :param _key_one: str
    :param _key_two: str
    :return: list of dict
    """
    _maps = []

    if len(_data) <= 1:
        return []

    for i in range(len(_data)):
        for j in range(len(_data))[i+1:]:
            ent_a, ent_b = _data[i], _data[j]
            _map = _map.copy()
            _map[_key_one] = ent_a.uri if isinstance(ent_a, Subgraph) else ent_a
            _map[_key_two] = ent_b.uri if isinstance(ent_b, Subgraph) else ent_b
            _maps.append(_map)

    return _maps


def _enforce_equal_constraints_(_dicts, _keys):
    """
        Remove the dicts whose values aren't equal in these positions as specified by keys.
        For instance if
        _dict = [{'a':1, 'b':2, 'c':3}, {'a':1, 'b':2, 'c':1}, {'a':1, 'b':1, 'c':1}]
        _keys = [''a','c']
        returns [{'a':1, 'b':2, 'c':1}, {'a':1, 'b':1, 'c':1}]

        Assumption: the _keys are present in _dict as keys

    :param _dicts: list of dicts
    :param _keys: list of str (keys of dict above)
    :return: filtered list of dicts
    """
    if len(_keys) < 2:
        return list(_dicts)

    equal_dicts = []

    for _dict in _dicts:

        val_one = _dict[_keys[0]]
        equal_flag = True
        for val_i in _keys[1:]:
            if _dict[val_i] != val_one:
                equal_flag = False
                break
        if equal_flag:
            equal_dicts.append(_dict)

    return equal_dicts


def trim_dicts(_dicts, _keys, _equal):
    """
        Remove the keys which aren't provided in _keys arg.

        - Assumes all the elements of the dict have the same keyv
        - Also remove duplicates (if any) after some keys have been removed.

    :param _dicts: list of dictionaries (with the same set of keys)
    :param _keys: list of keys that we should keep in there.
    :param _equal: list of keys whose values should be equal in every list
    :return: list of dicts
    """
    for _dict in _dicts:
        for _key in list(_dict.keys()):
            if _key not in _keys:
                _dict.pop(_key)

    # Now to take care of uniques.
    return _enforce_equal_constraints_(dict((hashable(v, _keys), v) for v in _dicts).values(), _equal)


def permute_dicts(_d1, _d2, _optional=True):
    """
        Given two list of dicts, it creates a list of dicts having a combination of both values.

        Assumption:
            - a list's dicts will have same keys
            - if two dict have common keys, only permute elements whose values for common keys are same.

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


class VarList(list):
    """
        Extends list to easy peasy compute a bunch of flags for a list of variables.
        To be used within Subgraph.get_mapping_for fn, generally.
    """

    def __init__(self, _vars, _valcheck=True):
        super(VarList, self).__init__(_vars)

        if _valcheck:
            for var in self:  # Check if all vars make sense
                if var not in VARS:
                    raise UnknownVarFoundError("Var %s not known." % var)

    def filtered(self, src):
        return VarList([v for v in self if v in src], False)

    @lazy_property
    def one(self):
        return self.filtered(VAR_HOP1)

    @lazy_property
    def two(self):
        return self.filtered(VAR_HOP2)

    @lazy_property
    def right(self):
        return self.filtered(VAR_HOP2_RIGHT + VAR_HOP1_RIGHT + VAR_HOP1_RIGHT_DUP + VAR_HOP1_RIGHT_DOUBLE + VAR_CLASS)

    @lazy_property
    def left(self):
        return self.filtered(VAR_HOP2_LEFT + VAR_HOP1_LEFT + VAR_HOP1_LEFT_DUP + VAR_HOP1_LEFT_DOUBLE + VAR_CLASS)

    @lazy_property
    def dup(self):
        return self.filtered(VAR_HOP1_RIGHT_DUP + VAR_HOP1_LEFT_DUP)

    @lazy_property
    def double(self):
        return self.filtered(VAR_HOP1_RIGHT_DOUBLE + VAR_HOP1_LEFT_DOUBLE)

    @lazy_property
    def type(self):
        return self.filtered(VAR_CLASS)

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
    def type_(self):
        return bool(self.type)

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
        self.time_maps = 0

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

    def _get_mapping_for_(self, _vars, _equal):
        """
            Returns a list of mapping fitting these vars, satisfying the equal condition.

            Logic: check which side of self should we start at (may be both).
            Function is recursive in nature!

            @TODO: fix equal constraints parsing

            Assumptions:
                - won't ask for _2 and _2* for any var in one call
                - won't ask for _2 of something without its original var.

        :param _vars: list of str: indicate variables that you want the mapping to consist of.
        :param _equal: only get mapping satisfying this constraint.
        :return: list of dicts.
        """

        _vars = VarList(_vars)

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

                _map = {'e_to_e_out': pred, 'uri': self.uri}
                if 'class_uri' in _vars:
                    _map.update({'class_uri': self.type})

                _maps = _take_one_(_map, ents, _key='e_out') if not _vars.right.double_ \
                    else _take_two_(_map, ents, _key_one='e_out', _key_two='e_out_2')

                if len(_maps) == 0:
                    return []

                if _vars.right.two_:
                    rec_right_maps = []
                    for ent in ents:
                        rec_right_maps += [change_keys_dict(x, rev(REC_RIGHT_VARS))
                                           for x in ent._get_mapping_for_(change_keys_list(_vars.right, REC_RIGHT_VARS), [])]

                    _maps = permute_dicts(_maps, rec_right_maps, _optional=False)

                right_maps += _maps

            if _vars.right.dup_:
                dup_right_maps = []

                for _map in right_maps:
                    for pred, ents in self.right.items():

                        if _map['e_to_e_out'] == pred or pred.split('/')[-1] == _map['e_to_e_out'].split('/')[-1]:
                            continue

                        _map['e_to_e_out_2'] = pred
                        dup_right_maps += _take_one_(_map, ents, _key='e_out_2*')

                right_maps = dup_right_maps

        """
            Logic for left
        """
        if _vars.one.left_:

            for pred, ents in self.left.items():

                if _vars.left.double_ and len(ents) < 2:
                    continue

                _map = {'e_in_to_e': pred, 'uri': self.uri}
                if 'class_uri' in _vars:
                    _map.update({'class_uri': self.type})

                _maps = _take_one_(_map, ents, _key='e_in') if not _vars.left.double_ \
                    else _take_two_(_map, ents, _key_one='e_in', _key_two='e_in_2')

                if len(_maps) == 0:
                    return []

                if _vars.left.two_:
                    rec_left_maps = []
                    for ent in ents:
                        rec_left_maps += [change_keys_dict(x, rev(REC_LEFT_VARS)) for x
                                          in ent._get_mapping_for_(change_keys_list(_vars.right, REC_LEFT_VARS), [])]

                    _maps = permute_dicts(_maps, rec_left_maps, _optional=False)

                left_maps += _maps

            if _vars.left.dup_:
                dup_left_maps = []

                for _map in left_maps:
                    for pred, ents in self.left.items():

                        if _map['e_in_to_e'] == pred or pred.split('/')[-1] == _map['e_in_to_e'].split('/')[-1]:
                            continue

                        _map['e_in_to_e_2'] = pred
                        dup_left_maps += _take_one_(_map, ents, _key='e_in_2*')

                left_maps = dup_left_maps

        mappings = trim_dicts(permute_dicts(left_maps, right_maps), _keys=_vars, _equal=_equal)
        self.mappings[_vars.hash] = mappings
        return mappings

    def gen_maps(self, _vars, _equal=[]):
        """
            Returns a list of mapping fitting these vars, satisfying the equal condition.

            Hash the params and see if we have it precomputed. If not, call _get_mapping_for_ fn and return op.

        :param _vars: list of str: indicate variables that you want the mapping to consist of.
        :param _equal: only get mapping satisfying this constraint.
        :return: list of dicts.
        """

        _var_obj = VarList(_vars)

        with Timer() as timer:
            mappings = self.mappings.get(_var_obj.hash, [x for x in self._get_mapping_for_(_vars, _equal) if len(x) != 0])

        self.time_maps += timer.interval
        print("%(uri)s | %(time).03f : %(len)03d : %(var)s :" %
              {'uri': self.uri, 'time': timer.interval, 'var': str(_var_obj), 'len': len(mappings)})

        return mappings

if __name__ == "__main__":
    a = Subgraph('dbr:Obama', 'dbo:Person')

    # Add 1 hop stuff
    data_out = [PredEntTuple(pred='dbp:prez', ent='dbr:US', type="dbo:Country"),
                PredEntTuple(pred='dbp:bornin', ent='dbr:Chicago', type="dbo:City"),
                PredEntTuple(pred='dbp:left', ent='2014', type="dbo:Year"),
                PredEntTuple(pred='dbp:spouse', ent='dbr:Michelle', type="dbo:Person"),
                PredEntTuple(pred='dbp:left', ent='2010', type="dbo:Year")]

    data_in = [PredEntTuple(pred='dbp:son', ent='dbr:BiggerObama', type="dbo:Person"),
               PredEntTuple(pred='dbp:spouse', ent='dbr:Michelle', type="dbo:Person"),
               PredEntTuple(pred='dbp:father', ent='dbr:Wut', type="dbo:Nothing"),
               PredEntTuple(pred='dbp:hasResident', ent='dbr:US', type="dbo:Person")]

    a.insert(data_out, _outgoing=True)
    a.insert(data_in, _outgoing=False)

    us = a.find('dbr:US', a)
    a.insert([
        PredEntTuple(pred='dbp:hasResident', ent='dbr:Obama', type='dbo:Person'),
        PredEntTuple(pred='dbp:capital', ent='dbr:WashingtonDC', type='dbo:City'),
        PredEntTuple(pred='dbp:continent', ent='dbr:NorthAmerica', type='dbo:Continent')
        ], _outgoing=True, _origin=us)
    a.insert([
        PredEntTuple(pred='dbp:bornin', ent='dbr:Trump', type='dbo:Person'),
        PredEntTuple(pred='dbp:location', ent='dbr:Stanford', type='dbo:Uni'),
    ], _outgoing=False, _origin=us)

    maps = a.gen_maps(['e_to_e_out', 'e_out_to_e_out_out', 'e_out_out', 'class_x'])
    maps_2 = a.gen_maps(['e_to_e_out', 'e_out_to_e_out_out', 'e_out_out', 'class_x'])
    maps_1 = a.gen_maps(['e_in', 'e_in_to_e', 'class_uri'])

    # pprint(maps)
    print(a.time_maps)
    # map = {'e_in_to_e':'color'}
    # data = ['blue', 'red','yellow','green', 'white', 'black']
    # key1, key2 = 'e', 'ee'
    # a = _take_two_(map, data, key1, key2)
    # print(a)