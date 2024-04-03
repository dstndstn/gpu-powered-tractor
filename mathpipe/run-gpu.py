from mathpipe.tractor_pool import create_pool
from legacypipe.oneblob import one_blob
import multiprocessing
import pickle
from time import time

def main():
    # Set up a magic multiprocessing.Pool that has mathpipes set up.
    pool = create_pool(4)
    print('Created pool', pool)

    # All standard code in here...
    infn = 'oneblob-inputs-custom-185981p19474-10'
    xstr = open(infn, 'rb').read()
    X = pickle.loads(xstr)

    (nblob, iblob, Isrcs, brickwcs, bx0, by0, blobw, blobh, blobmask, timargs,
     srcs, bands, plots, ps, reoptimize, iterative, use_ceres, refmap,
     large_galaxies_force_pointsource, less_masking, frozen_galaxies) = X

    print('%i sources, %i images, blob size %i x %i' % (len(Isrcs), len(timargs), blobw, blobh))
    print(len(xstr), 'bytes of input')

    t0 = time()
    Riter = pool.imap_unordered(one_blob, [X])
    res = []
    while True:
        try:
            r = Riter.next()
            res.append(r)
        except StopIteration:
            break
        except multiprocessing.TimeoutError:
            continue
    print('Got', len(res), 'results')
    assert(len(res) == 1)
    print('Took', time()-t0, 'sec')
    R = res[0]
    print('Measured %i sources, types %s' % (len(R), [str(type(s)) for s in R.sources]))

    # End of standard code -- print mathpipe stats!
    
    from mathpipe import tractor_math
    print('GPU work pipe stats:')
    stats = tractor_math.get_pipe_stats()
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
    
