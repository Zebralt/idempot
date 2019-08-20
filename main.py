"""
Make a batch process idempotent.

 keys => values (bijective)

 f ( *values )  

"""

import yaml


class savior:

    def __init__(
        self, 
        at: str, 
        idkey: callable = hash,
        hkey:callable = None, 
    ):
        self.filepath = at
        self.idkey = idkey
        self.hkey = hkey

    def map(
        self,
        f,
        iterable
    ):
        with self:
            for item in iterable:
                print(self.storage)
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                yield result

    def filter(
        self,
        f,
        iterable
    ):
        with self:
            for item in iterable:
                result = self.storage.get(item) or f(item)
                self.store(item, result)
                if result:
                    yield item

    # def batchwrap(
    #     self,
    #     f
    # ):

    def __enter__(self):
        self.storage = yaml.safe_load(open(self.filepath))
        print(self.storage)
        return self

    def __exit__(self, *a):
        yaml.dump(self.storage, open(self.filepath, 'w+'))


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