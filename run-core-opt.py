import sys
import logging
#from legacypipe.oneblob import one_blob
from legacypipe.oneblob import OneBlob
from astrometry.util.fits import fits_table
from tractor.factored_optimizer import GPUFriendlyOptimizer
from tractor import ProfileGalaxy, Tractor
from astrometry.util.plotutils import PlotSequence

import pickle
from time import time

# class MyOneBlob(OneBlob):
#     def __init__(self, *args, **kwargs):
#         self.gpu_optimizer = GPUFriendlyOptimizer()
#         super().__init__(*args, **kwargs)
# 
#     def tractor(self, tims, cat):
#         kwargs = self.trargs.copy()
#         print('Cat length', len(cat), 'type:', type(cat[0]))
#         if len(cat) == 1 and isinstance(cat[0], ProfileGalaxy):
#             kwargs.update(optimizer=self.gpu_optimizer)
#         tr = Tractor(tims, cat, **kwargs)
#         tr.freezeParams('images')
#         return tr

if __name__ == '__main__':
    lvl = logging.INFO
    logging.basicConfig(level=lvl, format='%(message)s', stream=sys.stdout)

    infn = 'oneblob-inputs-custom-185981p19474-10'
    xstr = open(infn, 'rb').read()

    from tractor.factored_optimizer import FactoredDenseOptimizer
    opt1 = FactoredDenseOptimizer()
    #opt1.ps = PlotSequence('fac')
    opt2 = GPUFriendlyOptimizer()
    #opt2.ps = PlotSequence('gpu')
    #opt2.ps_orig = PlotSequence('orig')
    for tag, opt, Ncopies in [
            ('gpufriendly', opt2, 100),
            ('factored', opt1, 1),
    ]:
        print()
        print('Optimizing with', tag, type(opt))
        print()

        X = pickle.loads(xstr)

        (nblob, iblob, Isrcs, brickwcs, bx0, by0, blobw, blobh, blobmask, timargs,
         srcs, bands, plots, ps, reoptimize, iterative, use_ceres, refmap,
         large_galaxies_force_pointsource, less_masking, frozen_galaxies) = X

        timargs = timargs * Ncopies

        from legacypipe.survey import LegacyEllipseWithPriors
        from tractor import DevGalaxy, Catalog
        print('Sources:', srcs)
        # Modify the first source to be a DevGalaxy (not PointSource)
        src = srcs[0]
        shape = LegacyEllipseWithPriors(-1., 0., 0.)
        dev = DevGalaxy(src.getPosition(), src.getBrightness(), shape).copy()
        srcs = [dev]
        print('Modified Sources:', srcs)

        print('%i sources, %i images, blob size %i x %i' % (len(Isrcs), len(timargs), blobw, blobh))

        blobwcs = brickwcs.get_subimage(bx0, by0, blobw, blobh)
        ob = OneBlob(nblob, blobwcs, blobmask, timargs, srcs, bands,
                     plots, ps, use_ceres, refmap,
                     large_galaxies_force_pointsource,
                     less_masking, frozen_galaxies)

        t0 = time()

        tr = Tractor(ob.tims, Catalog(*srcs), optimizer=opt)
        X = tr.optimizer.getLinearUpdateDirection(tr, shared_params=False)
        print('X', X)

        print('Took', time()-t0, 'sec')
