import time


class InvalidTemplateError(Exception): pass


class InvalidTemplateMappingError(Exception): pass


class InvalidSubgraphPreds(Exception):
    pass


class InvalidSubgraph(Exception):
    pass


class NoSubgraphFoundError(Exception):
    pass


class Timer:
    def __enter__(self):
        self.start = time.process_time()
        return self

    def __exit__(self, *args):
        self.end = time.process_time()
        self.interval = self.end - self.start

