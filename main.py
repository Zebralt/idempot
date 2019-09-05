
import os
import pickle
import hashlib
import inspect
import re
from itertools import tee

from yapf import yapf_api


def cleansource(source):
    """
    Auto-format w/ yapf and clean a Python function 's source code.
    """

    # Remove single line comments
    source, _ = yapf_api.FormatCode(source)

    # Remove # comments
    source = re.sub(r'\s*#.*\n', '\n', source)
    # Remove triple quotes comments
    source = re.sub(r'\n\s*"""(.|\n|(\n\r))*?"""', '\n', source)
    # Remove trailing whitespace
    source = re.sub(r'\s+$', '\n', source)
    # Remove empty lines
    source = re.sub(r'\n\s*\n', '\n', source)

    return source


def funcsum(f):
    """
    Compute a checksum of the source code of a function.
    """

    h = hashlib.sha384()

    try:
        h.update(
            cleansource(inspect.getsource(f)).encode('utf-8')
        )
    except TypeError as te:
        print(te)
        h.update(f.__name__.encode('utf-8'))

    return h.hexdigest()


class savior:

    """
    An interface object used to make a batch process idempotent.
    This will save the output elements and keep track of those who
    have been already processed, skipping them at next runtime.
    """

    def __init__(
        self,
        at: str,  # The saving point (a filepath)
        idkey: callable = hash,  # The function used to uniquely identify the input value
    ):
        self.filepath = at
        self.storage = {}
        self.idkey = idkey
        self.fuid = -1

    def question(self, f):
        checksum = funcsum(f)
        if checksum != self.fuid:
            print("Changes have been detected in the function. Wiping storage.")
            self.storage = {}
            self.fuid = checksum

    def map(
        self,
        f,
        iterable
    ):
        """
        Call a map object wrapped backed by the current object.
        """
        with self:
            self.question(f)
            for item in iterable:
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                yield result

    def __call__(self, f):
        """Wraps a function in idempotency."""
        return self.batchwrap(f)

    def batchwrap(self, f):
        """Wraps a function in idempotency."""
        def wrapper(items, **kw):

            sentinel = object()

            with self:

                self.question(f)

                mogadicio = (
                    (item, self.storage.get(item, sentinel))
                    for item in items
                )

                mogadicio, mogadicia = tee(mogadicio)

                parallel = f(
                    item[0]
                    for item in mogadicia
                    if item[1] is sentinel
                )

                for m in mogadicio:
                    item, result = m
                    if result is sentinel:
                        result = next(parallel)
                    # do it then
                    self.store(item, result)
                    yield result

        return wrapper

    def filter(
        self,
        f,
        iterable
    ):
        with self:
            self.question(f)
            for item in iterable:
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                if result:
                    yield item

    def load(self):
        self.storage = {}
        if os.path.exists(self.filepath):
            with open(self.filepath, 'rb') as f:
                self.fuid, self.storage = pickle.load(f)

    def save(self):
        self.storage = self.fuid, self.storage
        pickle.dump(self.storage, open(self.filepath, 'wb+'))

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, *a):
        self.save()

    def store(self, input, output):
        self.storage[input] = output
