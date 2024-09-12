# Generic version of tractor_pool.py

import sys
import time
import multiprocessing as mp
#import threading
import pickle
import astrometry.util.timingpool

# This replaces multiprocessing.Pipe, adding tracking of pickle cpu time & bytes sent/received
def TimingDuplexPipe():
    from astrometry.util.timingpool import TimingConnection
    import socket
    s1, s2 = socket.socketpair()
    s1.setblocking(True)
    s2.setblocking(True)
    c1 = TimingConnection(s1.detach())
    c2 = TimingConnection(s2.detach())
    return c1,c2

# This is the "target" function for the multiprocessing Pool worker processes.
# These are the mathpipe client processes.
# We just wrap the real thing, setting the mathpipe for this pool process.
def my_target(ctx, realtarget, r, *args):
    from mathpipe.client import mathpipe_client
    mathpipe_client().set_pipe(r)
    return realtarget(*args)

class ProcessContext(object):
    def __init__(self):
        self.pipes = []

    def add_pipes(self, r, w):
        #print('ProcessContext: remembering pipe', w)
        self.pipes.append(w)

    SimpleQueue = mp.SimpleQueue

    def Process(ctx, target=None, args=None, **kwargs):
        #print('ProcessContext.Process...')
        r,w = TimingDuplexPipe()
        #print('pipes:', r,w)
        ctx.add_pipes(r, w)
        my_args = (ctx, target, r) + args
        p = mp.Process(args=my_args, target=my_target, **kwargs)
        return p

    def main_process_pipe(self):
        # Allow the main process to also be a mathpipe client
        from mathpipe.client import mathpipe_client
        r,w = TimingDuplexPipe()
        self.add_pipes(r, w)
        mathpipe_client().set_pipe(r)

worker_processes = []
#gpu_context = None

def create_pool(worker_class, nproc):
    # global gpu_context
    # if gpu_context is None:
    #     gpu_context = ProcessContext()
    from multiprocessing.pool import Pool
    context = ProcessContext()
    pool = Pool(nproc, context=context)

    pipes = context.pipes
    #print('context Pipes:', context.pipes)

    from multiprocessing.reduction import ForkingPickler as fp
    
    #pic = fp.dumps(pipes)
    #picpipes = fp.loads(pic)
    #print('ForkingPickler roundtrip pipes:', picpipes)

    # Also connect up the math pipe for the main process...
    context.main_process_pipe()

    # Create the Process for the worker end of the mathpipes

    from mathpipe.worker import worker_target
    workerproc = mp.Process(target=worker_target,
                            args=(worker_class, pipes,),
                            daemon=True)

    #worker = worker_class(pipes)
    #workerproc = mp.Process(target=worker, args=(), daemon=True)

    workerproc.start()
    # save the process - having it go out of scope is maybe bad?
    global worker_processes
    worker_processes.append(workerproc)

    return pool
