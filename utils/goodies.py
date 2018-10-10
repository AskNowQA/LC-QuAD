import time


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

