import time
import sys
import os
from main import savior

# Test map

def inform(around=2):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, exc_obj, fname, exc_tb.tb_lineno)
    ll = open(fname).readlines()
    print('---' * 20)
    for l in ll[exc_tb.tb_lineno-around + 1:exc_tb.tb_lineno + 1]:
        print(l.strip('\n'))
    print('\033[93;1m' + ll[exc_tb.tb_lineno+1].strip('\n') + '\033[m')
    for l in ll[exc_tb.tb_lineno+1+1:exc_tb.tb_lineno+around+1+1]:
        print(l.strip('\n'))
    print('---' * 20)

def test_savior_map():

    items = range(10)

    def f(item):
        time.sleep(.1)
        return item / 2

    s = savior()

    obtained_results = s.map(f, items)

    t = time.time()

    obtained_results = list(obtained_results)

    if time.time() - t < 1:
        assert False
    
    obtained_results = s.map(f, items)

    print(s.storage)

    t = time.time()

    obtained_results = list(obtained_results)

    if time.time() - t >= 1:
        assert False


if __name__ == "__main__":
    
    score = 0
    total = 0

    for k, v in list(globals().items()):
        if callable(v) and k.startswith('test_'):
            total += 1
            print(k)
            try:
                v()
                score += 1
                print('\033[92m[OK]\033[m', k)
            except AssertionError:
                inform()
                print('\033[91m[KO]\033[m', k)
        
    print('%s/%s' % (score, total))
    
    
    