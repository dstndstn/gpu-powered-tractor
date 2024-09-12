from mathpipe.pool import create_pool
import multiprocessing
import pickle
from time import time
import os

from mathpipe.worker import MathPipeWorker
from mathpipe.client import mathpipe_client

def my_math_func(a, b, c=None, d=None):
    print('my_math_func: a=', a, 'b=', b, 'c=', c, 'd=', d)
    return a+b

class MyWorker(MathPipeWorker):
    def __init__(self, pipes):
        super().__init__(pipes)
        print('Creating MyWorker() in pid', os.getpid())
        #print('MyWorker: pipes', pipes)
        self.register_free_function('freefunc', my_math_func)
        self.register_member_function('memfunc', MyWorker.memfunc)

    def memfunc(self, a, c=None):
        print('memfunc: a=', a, 'c=', c)
        return a


def mp_func(*args):
    print('mp_func in pid', os.getpid(), 'with args', args)
    print('mp_func calling free func...')
    r1 = mathpipe_client().freefunc(100, *args)
    print('mp_func got', r1)
    print('mp_func calling mem func...')
    r2 = mathpipe_client().memfunc(*args)
    print('mp_func got', r2)
    return r1,r2
    
def main():
    # Set up a magic multiprocessing.Pool that has mathpipes set up.
    pool = create_pool(MyWorker, 4)
    print('Created pool', pool)

    args = list(range(10))

    #R = list(pool.imap_unordered(mp_func, args))
    R = list(pool.map(mp_func, args))

    print('Results:', R)
    
    # Riter = pool.imap_unordered(mp_func, args)
    # res = []
    # while True:
    #     try:
    #         r = Riter.next()
    #         res.append(r)
    #     except StopIteration:
    #         break
    #     except multiprocessing.TimeoutError:
    #         continue
    # print('Got', len(res), 'results')

    # End of standard code -- print mathpipe stats!

    from mathpipe import tractor_math
    print('GPU work pipe stats:')
    stats = mathpipe_client().stats()
    for k in ['pickle_objs', 'pickle_megabytes', 'pickle_cputime',
              'unpickle_objs', 'unpickle_megabytes', 'unpickle_cputime']:
        v = stats[k]
        if type(v) is int:
            print('  ', k, v)
        else:
            print('  ', k, '%.3g' % stats[k])
    for k,v in stats.items():
        if k.startswith('ncalls_'):
            print('  ', k, v)
        elif k.startswith('cputime_'):
            print('  ', k, '%.3f' % v)

    print(stats)

if __name__ == '__main__':
    main()
    
