import sys
import time
import multiprocessing as mp
import threading

def TimingDuplexPipe():
    from astrometry.util.timingpool import TimingConnection
    import socket
    s1, s2 = socket.socketpair()
    s1.setblocking(True)
    s2.setblocking(True)
    c1 = TimingConnection(s1.detach())
    c2 = TimingConnection(s2.detach())
    return c1,c2

def my_target(ctx, realtarget, r, *args):
    from mathpipe import tractor_math
    #print('tractor_math pipe was:', tractor_math.tractor_math_pipe)
    tractor_math.tractor_math_pipe = r
    #print('tractor_math pipe now:', tractor_math.tractor_math_pipe)
    return realtarget(*args)

class ProcessContext(object):
    def __init__(self):
        self.pipes = []
        #self.rpipes = []

    def add_pipes(self, r, w):
        #print('adding pipe', p)
        self.pipes.append(w)
        #self.rpipes.append(r)

    SimpleQueue = mp.SimpleQueue

    def Process(ctx, target=None, args=None, **kwargs):
        #print('Process: ctx=', ctx, 'args=', args, 'target=', target, 'kwargs=', kwargs)
        #r,w = mp.Pipe(duplex=True)
        #from astrometry.util.timingpool import TimingPipe
        #r,w = TimingPipe(duplex=True)
        r,w = TimingDuplexPipe()
        ctx.add_pipes(r, w)
        my_args = (ctx, target, r) + args
        p = mp.Process(args=my_args, target=my_target, **kwargs)
        return p

    def main_process_pipe(self):
        from mathpipe import tractor_math
        r,w = TimingDuplexPipe()
        self.add_pipes(r, w)
        tractor_math.tractor_math_pipe = r

gpu_processes = []
gpu_context = None

def create_pool(nproc):
    global gpu_context
    if gpu_context is None:
        gpu_context = ProcessContext()
    from multiprocessing.pool import Pool
    #print('Creating pool')
    pool = Pool(nproc, context=gpu_context)
    print('Created pool', pool)

    pipes = gpu_context.pipes
    #print('Creating worker...')

    # Also connect up the math pipe for the main process...
    gpu_context.main_process_pipe()

    from mathpipe.tractor_math_worker import gpu_manager
    gpuproc = mp.Process(target=gpu_manager,
                          args=(pipes,),
                          daemon=True)
    gpuproc.start()
    # stop the process from going out of scope...
    global gpu_processes
    gpu_processes.append(gpuproc)

    return pool

# def get_stats():
#     # This doesn't work, these are the copies before the copy-on-write
#     # for the Pool workers and GPU manager.
#     
#     # global gpu_context
#     # if gpu_context is None:
#     #     return None
#     # sum_stats = {}
#     # for p in gpu_context.pipes + gpu_context.rpipes:
#     #     s = p.stats()
#     #     print('pipe stats:', s)
#     #     for k,v in s.items():
#     #         if k in sum_stats:
#     #             sum_stats[k] = sum_stats[k] + v
#     #         else:
#     #             sum_stats[k] = v
#     # return sum_stats
#     from tractor_math import get_pipe_stats
#     return get_pipe_stats()
