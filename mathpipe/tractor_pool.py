import sys
import time
import multiprocessing as mp
import threading

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
# We just wrap the real thing, setting the mathpipe for this pool process.
def my_target(ctx, realtarget, r, *args):
    from mathpipe import tractor_math
    tractor_math.tractor_math_pipe = r
    return realtarget(*args)

class ProcessContext(object):
    def __init__(self):
        self.pipes = []

    def add_pipes(self, r, w):
        self.pipes.append(w)

    SimpleQueue = mp.SimpleQueue

    def Process(ctx, target=None, args=None, **kwargs):
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
    pool = Pool(nproc, context=gpu_context)

    pipes = gpu_context.pipes

    # Also connect up the math pipe for the main process...
    gpu_context.main_process_pipe()

    # Create the Process for the worker end of the mathpipes
    from mathpipe.tractor_math_worker import gpu_manager
    gpuproc = mp.Process(target=gpu_manager,
                          args=(pipes,),
                          daemon=True)
    gpuproc.start()
    # save the process - having it go out of scope is maybe bad?
    global gpu_processes
    gpu_processes.append(gpuproc)

    return pool
