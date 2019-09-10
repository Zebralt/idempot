
import os
import pickle
import hashlib
import inspect
import re
from typing import Iterator
from functools import wraps, partial
from itertools import tee

from yapf import yapf_api


def cleansource(source: str) -> str:
    """
    Auto-format w/ yapf and clean a Python function 's source code.
    Do away with whitespace, empty lines and comments. (docstrings + single-line)
    """

    first = source.split('\n')[0]
    m = re.match('^\s+', first)
    if m is not None:
        x = m.group()
        if len(x):
            source = '\n'.join(
                re.sub(r'^\s{%s}' % len(x), '', line)
                for line in source.split('\n')
            )

    print(source)

    # Format code with yapf
    source, _ = yapf_api.FormatCode(source)

    # Remove # comments
    source = re.sub(r'\s*#.*\n', '\n', source)

    # Remove triple quotes comments
    source = re.sub(r'\n\s*"""(.|\n|(\n\r))*?"""', '\n', source)
    source = re.sub(r"\n\s*'''(.|\n|(\n\r))*?'''", '\n', source)

    # Remove trailing whitespace
    source = re.sub(r'\s+$', '\n', source)

    # Remove empty lines
    source = re.sub(r'\n\s*\n', '\n', source)

    return source


def funcsum(f: callable) -> str:
    """
    Compute a checksum of the source code of a function.
    The source code also includes both the function's prototype and decorators declarations.
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
        at: str = None,  # The saving point (a filepath)
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
        f: callable,
        iterable: Iterator
    ) -> Iterator:
        """
        Call a map object wrapped backed by the current object.
        """
        with self:
            self.question(f)
            for item in iterable:
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                yield result

    def __call__(self, f: callable) -> callable:
        """Wraps a function in idempotency."""
        return self.batchwrap(f)

    def batchwrap(self, f: callable) -> callable:
        """Wraps a function in idempotency."""

        @wraps(f)
        def wrapper(items, **kw):

            sentinel = object()

            with self:

                self.question(f)

                mogadicio = (
                    (
                        item,
                        self.storage.get(item, sentinel)
                    )
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
        f: callable,
        iterable: Iterator
    ) -> Iterator:
        with self:
            self.question(f)
            for item in iterable:
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                if result:
                    yield item

    def load(self):
        self.storage = {}
        if self.filepath and os.path.exists(self.filepath):
            with open(self.filepath, 'rb') as f:
                self.fuid, self.storage = pickle.load(f)

    def save(self):
        if self.filepath:
            self.storage = self.fuid, self.storage
            pickle.dump(self.storage, open(self.filepath, 'wb+'))

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, *a):
        self.save()

    def store(self, input, output):
        self.storage[input] = output
