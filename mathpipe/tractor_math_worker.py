import multiprocessing as mp
import time

def gpu_manager(pipes):

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

    functions = dict(
        fft_mix_inv_shift = fft_mix_inv_shift,
        stats = get_stats,
    )
    
    cputimes = {}
    ncalls = {}
    while True:
        for r in mp.connection.wait(pipes):
            try:
                msg = r.recv()
                #print('Received from pipe', pipes.index(r), ':', msg)

                funcname,args = msg
                func = functions.get(funcname, None)
                if func is None:
                    R = 'unknown func'
                else:
                    # Special cases...
                    if funcname == 'stats':
                        args = (pipes, ncalls, cputimes)

                    t0 = time.time()
                    R = func(*args)
                    t1 = time.time()

                    ncalls[funcname] = ncalls.get(funcname, 0) + 1
                    cputimes[funcname] = cputimes.get(funcname, 0.) + (t1-t0)

                r.send(R)

            except EOFError:
                pipes.remove(r)

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

import numpy as np
from tractor.psf import lanczos_shift_image

def fft_mix_inv_shift(fftmix, v, w, P, mux, muy):
    Fsum = fftmix.getFourierTransform(v, w, zero_mean=True)
    G = np.fft.irfftn(Fsum * P)
    # float64.... should we be doing float32 FFTs??!
    #print('irfftn type:', G.dtype)
    G = G.astype(np.float32)
    if mux != 0.0 or muy != 0.0:
        lanczos_shift_image(G, mux, muy, inplace=True)
    return G
