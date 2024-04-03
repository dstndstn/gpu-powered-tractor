# GPU offload experiments

# This will be set up for worker processes by tractor_pool.py
tractor_math_pipe = None

def get_pipe_stats():
    tractor_math_pipe.send(('stats', None))
    r = tractor_math_pipe.recv()
    return r
    
# fftmix, v, w, P, mux, muy
def fft_mix_inv_shift(*args):
    tractor_math_pipe.send(('fft_mix_inv_shift', args))
    r = tractor_math_pipe.recv()
    return r
