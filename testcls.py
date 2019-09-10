from main import cleansource
import inspect, time


def translate(d):                 
    #
    """Comment"""   
    if d is None:
        raise ValueError

    time.sleep(.5)  # wait
    """
    Comment
    """
    a = """var"""
    b = """
    var  
    """
    return '_%s_' % d  
    # a


if __name__ == "__main__":
    
    src = inspect.getsource(translate)
    print(len(src.split('\n')), len(src))
    print('\033[4m' + src + '\033[m')
    print('---')
    print('\033[4m' + cleansource(src) + '\033[m')
    print('---')