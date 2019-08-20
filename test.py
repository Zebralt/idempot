from main import savior
import time
from tqdm import tqdm


def translate(d):

    if d is None:
        raise ValueError

    time.sleep(.5)

    return '_%s_' % d


def batch_translate(ds):
    return map(translate, ds)


if __name__ == "__main__":
    
    items = [
        "This is astute"
    ] * 10
    items = (
        items 
        # + [ None ]
        + items
    )

    # translations = map(translate, items)
    # print(*translations,)

    translations = savior('touille.txt').map(translate, items)
    translations = tqdm(translations, total=len(items), ncols=60)
    print(*translations,)

    # translations = batch_translate(items)
    # print(*translations,)

    # translations = savior('bouille.txt').batchwrap(batch_translate)(items)
    # translations = tqdm(translations, total=21)
    # print(*translations,)