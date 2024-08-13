#from legacypipe.oneblob import one_blob
from legacypipe.oneblob import OneBlob
from astrometry.util.fits import fits_table

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
    #R = one_blob(X)
    #print('Measured %i sources, types %s' % (len(R), [str(type(s)) for s in R.sources]))

    blobwcs = brickwcs.get_subimage(bx0, by0, blobw, blobh)

    ob = OneBlob(nblob, blobwcs, blobmask, timargs, srcs, bands,
                 plots, ps, use_ceres, refmap,
                 large_galaxies_force_pointsource,
                 less_masking, frozen_galaxies)
    B = ob.init_table(Isrcs)
    B = ob.run(B, reoptimize=reoptimize, iterative_detection=iterative)
    ob.finalize_table(B, bx0, by0)

    print('Took', time()-t0, 'sec')

    print('Measured %i sources, types %s' % (len(B), [str(type(s)) for s in B.sources]))
