mathpipe -- an experimental way for multiprocessing tasks to offload their work to a
shared process (that could, eg, be managing a GPU).

You need the "tractor" repository's branch called "gpu-powered".

The run-gpu.py script runs a demo.

What it does:

- mathpipe.tractor_pool.create_pool
   creates a multiprocessing.Pool whose workers all have pipes that let them talk to the
   worker process.  Also starts up the worker process (in mathpipe.tractor_pool_worker)

- the main process uses the multiprocessing pool as usual

- in the Tractor code, deep in the galaxy.py code, instead of doing math at one point, it
  calls a function in mathpipe.tractor_math (fft_mix_inv_shift).  That function just sends a
  message over its pipe, waits to receive an answer, and returns the answer.

- the real action happens in mathpipe.tractor_math_worker.  The main loop there is gpu_manager(),
  and it calls work functions such as fft_mix_inv_shift() to actually do the math.

- it also records how much CPU time is used, how many times functions are called, and (via some
  code reused from astrometry.util.timingpool), how much time is spent pickling/unpickling and how
  many bytes are sent.

