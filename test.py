from main import savior
import time
from tqdm import tqdm


def translate(d):
    
    # if d is None or 0:
    #     raise ValueError

    time.sleep(.5)

    return '_%s_' % d


@savior('bouille.txt')
def batch_translate(ds):
    return map(translate, ds)


if __name__ == "__main__":
    
    items = [
        "This is astute%d" % i
        for i in range(10)
    ]
    items = (
        items 
        # + [ None ]
        + [i + 'x' for i in items]
    )

    # translations = map(translate, items)
    # print(*translations,)

    # translations = savior('touille.txt').map(translate, items)
    # translations = tqdm(translations, total=len(items), ncols=60)
    # print(*translations,)

    # translations = batch_translate(items)
    # print(*translations,)

    # translations = savior('bouille.txt').batchwrap(batch_translate)(items)
    translations = batch_translate(items)
    translations = tqdm(translations, total=len(items), ncols=60)
    print(*translations,)