"""
Make a batch process idempotent.

 keys => values (bijective)

 f ( *values )  

"""

import os
import pickle
import hashlib
import inspect
import re
from yapf import yapf_api

def cleansource(source):

    # Remove single line comments
    # right-
    source,_ = yapf_api.FormatCode(source)
    
    # Remove # comments
    source = re.sub(r'\s*#.*\n', '\n', source)
    # Remove triple quotes comments
    source = re.sub(r'\n\s*"""(.|\n|(\n\r))*?"""', '\n', source)
    # Remove trailing whitespace
    source = re.sub(r'\s+$', '\n', source)
    # Remove empty lines
    source = re.sub('\n\s*\n', '\n', source)


    print(len(source.split('\n')), len(source))
    return source


def funcsum(f):
    h = hashlib.sha384()
    
    try:
        h.update(
            cleansource(inspect.getsource(f)).encode('utf-8')
        )
    except TypeError as te:
        print(te)
        h.update(f.__name__.encode('utf-8'))
    
    v = h.hexdigest()
    print(v)
    return v


class savior:

    def __init__(
        self, 
        at: str, 
        idkey: callable = hash,
        hkey:callable = None, 
    ):
        self.filepath = at
        self.storage = {}
        self.idkey = idkey
        self.hkey = hkey
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
        with self:
            self.question(f)
            for item in iterable:
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                yield result

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

    # def batchwrap(
    #     self,
    #     f
    # ):

    def load(self):
        self.storage = {}
        if os.path.exists(self.filepath):
            with open(self.filepath, 'rb') as f:
                self.fuid, self.storage = pickle.load(f)

    def save(self):
        # yaml.dump(self.storage, open(self.filepath, 'w+'))
        self.storage = self.fuid, self.storage
        pickle.dump(self.storage, open(self.filepath, 'wb+'))

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, *a):
        self.save()


    def store(self, input, output):
        # print(input, '=>', output)
        self.storage[input] = output


def test_idempotency():

    # Let's say I want to translate 1k elements;

    texts = ["I"] * 20 + ["A"] + ["I"] * 20

    # I want to make the process idempotent, that is,
    # 

    def translate(d):
        if d == "A":
            raise Exception
        return "E"
    
    translations = map(translate, texts)

    # Oups! One the items wasn't translated properly and raised an exception.
    # Where have the successful translations up to exception time found ?

    # automatically hash out and checksum the function
    translations = savior(at='backup.pkg').map(translate, texts)
    translations = savior(at='backup.pkg')(batch_translate)(texts)  # align
    # defaults:
    # name => numerated default (backup1, backup2, backup3, etc. created  as temp files)
    # idkey => hash
    
    translations = map(translate, texts)
    translations = savior('name').iter(translations)  # +^ this is nonsensical; the operation still need to be done and we can't access the input of each transaction

    *translations,