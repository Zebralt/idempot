from main import savior
import time
import random
from tqdm import tqdm


def translate(d):

    print(1)

    # if d is None or 0:
    #     raise ValueError

    time.sleep(.5)

    return '_%s_' % d


@savior('bouille.pkl')
def batch_translate(ds):
    return map(translate, ds)


if __name__ == "__main__":

    items = [
        "This is astute%d" % i
        for i in random.choices(range(10), k=10)
    ]
    items = (
        items
        # + [ None ]
        + [i + 'x' for i in items]
    )

    # translations = map(translate, items)
    # print(*translations,)

    translations = savior('touille.pkl').map(translate, items)
    translations = tqdm(translations, total=len(items), ncols=60)
    print(*translations,)

    translations = savior('bouille.txt').batchwrap(batch_translate)(items)
    # translations = batch_translate(items)
    translations = tqdm(translations, total=len(items), ncols=60)
    print(*translations, sep='\n')
