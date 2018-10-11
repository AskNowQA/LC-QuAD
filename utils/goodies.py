import time
from collections import namedtuple

Log = namedtuple('Log', 'uri traceback')


def lazy_property(fn):
    """
        Got the following decorator from https://stevenloria.com/lazy-properties/
        It makes the property lazy load, not precompute, and once loaded, always return the same thing.

        DO NOT USE THIS FOR CLASSES WHO'S SELF KEEPS CHANGING!
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazy_property


class InvalidTemplateError(Exception):
    pass


class InvalidTemplateMappingError(Exception):
    pass


class InvalidSubgraphPreds(Exception):
    pass


class InvalidSubgraph(Exception):
    pass


class NoSubgraphFoundError(Exception):
    pass


class UnknownVarFoundError(Exception):
    pass


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.interval = self.end - self.start
