# Test for missing Mixture-of-Gaussians code in factored_optimizer.py
if __name__ == '__main__':
    from tractor.factored_optimizer import FactoredDenseOptimizer
    from tractor.factored_optimizer import GPUFriendlyOptimizer
    import numpy as np
    from astrometry.util.plotutils import PlotSequence
    
    opt1 = FactoredDenseOptimizer()
    opt2 = GPUFriendlyOptimizer()
    opt2.ps = PlotSequence('gpu')

    # Load image data from our saved pickle
    import pickle
    #from legacypipe.oneblob import create_tims
    infn = 'oneblob-inputs-custom-185981p19474-10'
    xstr = open(infn, 'rb').read()
    X = pickle.loads(xstr)
    (nblob, iblob, Isrcs, brickwcs, bx0, by0, blobw, blobh, blobmask, timargs,
     srcs, bands, plots, ps, reoptimize, iterative, use_ceres, refmap,
     large_galaxies_force_pointsource, less_masking, frozen_galaxies) = X
    blobwcs = brickwcs.get_subimage(bx0, by0, blobw, blobh)

    from legacypipe.survey import LegacyEllipseWithPriors
    from tractor import RaDecPos, NanoMaggies, DevGalaxy, Tractor, ModelMask
    from tractor import Image

    # Create tractor Image object ("tim")
    #tims = create_tims(blobwcs, blobmask, timargs)
    tims = []
    for (img, inverr, dq, twcs, wcsobj, pcal, sky, subpsf, name,
         band, sig1, imobj) in timargs:
        h,w = img.shape
        subpsf = subpsf.constantPsfAt(w/2., h/2.)
        tim = Image(data=img, inverr=inverr, wcs=twcs,
                    psf=subpsf, photocal=pcal, sky=sky, name=name)
        tim.band = band
        tim.sig1 = sig1
        tim.subwcs = wcsobj
        tim.meta = imobj
        tim.psf_sigma = imobj.fwhm / 2.35
        tim.dq = dq
        tims.append(tim)
        break
    tims = [tims[0]]

    # Create galaxy
    src = DevGalaxy(RaDecPos(185.97482, 19.48192),
                    NanoMaggies(i=1.),
                    LegacyEllipseWithPriors(0., 0.064774, 0.0617007))

    tr = Tractor(tims, [src])
    tr.freezeParam('images')
    tr.setModelMasks([{src:ModelMask(0, 0, tim.shape[1], tim.shape[0])}
                      for tim in tims])

    X1 = opt1.getLinearUpdateDirection(tr, shared_params=False)
    X2 = opt2.getLinearUpdateDirection(tr, shared_params=False)

    print('X1', X1)
    print('X2', X2)
    X2 = X2.get()

    dst = np.sum(X1 * X2) / (np.sqrt(np.sum(X1**2)) * np.sqrt(np.sum(X2**2)))
    print('Similarity:', dst)
