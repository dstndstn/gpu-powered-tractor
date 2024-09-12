# generic version of tractor_math_worker.py

import multiprocessing as mp
import time
import os

from mathpipe.pool import TimingDuplexPipe
from astrometry.util.timingpool import TimingConnection

# This is the top-level function called in the new worker process
def worker_target(clz, pipes):
    print('Starting worker class in pid', os.getpid())
    #print('worker pipes:', pipes)
    #from astrometry.util import timingpool
    #import pickle
    #pipes = pickle.loads(pipes)
    #print('unpickled pipes:', pipes)
    w = clz(pipes)
    w.run()

class MathPipeWorker(object):
    def __init__(self, pipes):
        self.pipes = pipes
        self.free_functions = dict(
            stats = get_stats)
        self.member_functions = dict()

    def register_free_function(self, name, f):
        self.free_functions[name] = f

    def register_member_function(self, name, f):
        self.member_functions[name] = f

    # def __call__(self):
    #     print('MathPipeWorker.__call__... pipes=', self.pipes)
    #     self.run()

    # If you wanted to batch up requests before running them, could do something like:
    # batch = []
    # while True:
    #     for r in mp.connection.wait(pipes):
    #         try:
    #             msg = r.recv()
    #             print('Received from pipe', pipes.index(r), ':', msg)
    #             batch.append((msg, r))
    #             if len(batch) >= 10:
    #                 break
    #         except EOFError:
    #             pipes.remove(r)
    # 
    #     if len(batch) >= 10:
    #         print('Doing a batch of work')
    #         for msg,r in batch:
    #             r.send(('gpu', msg))
    #         batch = []
        
    def run(self):
        cputimes = {}
        ncalls = {}
        while True:
            for r in mp.connection.wait(self.pipes):
                try:
                    R = None
                    msg = r.recv()
                    #print('Received from pipe', pipes.index(r), ':', msg)
                    funcname,args,kwargs = msg
                    print('Worker: funcname', funcname)
                    func = self.free_functions.get(funcname, None)
                    if func is None:
                        func = self.member_functions.get(funcname, None)
                        if func is None:
                            R = 'unknown func'
                        else:
                            args = (self,) + args

                    if func is not None:
                        print('Got function', func)
                        # Special cases...
                        if funcname == 'stats':
                            args = (self.pipes, ncalls, cputimes)

                        t0 = time.time()
                        R = func(*args, **kwargs)
                        t1 = time.time()
    
                        ncalls[funcname] = ncalls.get(funcname, 0) + 1
                        cputimes[funcname] = cputimes.get(funcname, 0.) + (t1-t0)
    
                    r.send(R)
    
                except EOFError:
                    self.pipes.remove(r)

def get_stats(pipes, ncalls, cputimes):
    sum_stats = {}
    for p in pipes:
        s = p.stats()
        #print('pipe stats:', s)
        for k,v in s.items():
            if k in sum_stats:
                sum_stats[k] = sum_stats[k] + v
            else:
                sum_stats[k] = v
    for k,v in ncalls.items():
        sum_stats['ncalls_'+k] = v
    for k,v in cputimes.items():
        sum_stats['cputime_'+k] = v
    return sum_stats
