from legacypipe.oneblob import one_blob

import pickle
from time import time

if __name__ == '__main__':
    #infn = '/pscratch/sd/d/dstn/legacypipe-demo/oneblob-inputs-custom-185981p19474-10'
    infn = 'oneblob-inputs-custom-185981p19474-10'
    xstr = open(infn, 'rb').read()
    X = pickle.loads(xstr)

    (nblob, iblob, Isrcs, brickwcs, bx0, by0, blobw, blobh, blobmask, timargs,
     srcs, bands, plots, ps, reoptimize, iterative, use_ceres, refmap,
     large_galaxies_force_pointsource, less_masking, frozen_galaxies) = X

    print('%i sources, %i images, blob size %i x %i' % (len(Isrcs), len(timargs), blobw, blobh))
    print(len(xstr), 'bytes of input')

    t0 = time()
    R = one_blob(X)
    print('Took', time()-t0, 'sec')

    print('Measured %i sources, types %s' % (len(R), [str(type(s)) for s in R.sources]))
