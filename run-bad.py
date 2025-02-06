import cupy
import pickle

#tr = pickle.load(open('bad.pickle','rb'))
tr = pickle.load(open('bad2.pickle','rb'))
tr.model_kwargs = {}
print('Got', tr)

tim = tr.images[0]
print('Image:', tim)

# print('Sky:', tim.getSky())
# src = tr.catalog[0]
# print('src:', src)
# print(dir(src))

opt = tr.optimizer
from astrometry.util.plotutils import PlotSequence
opt.ps = PlotSequence('bad2')
opt.getSingleImageUpdateDirections(tr, shared_params=False)

# import pylab as plt
# import fitsio
# c = fitsio.read('cpu-b.fits')
# g = fitsio.read('gpu-b.fits')
# plt.clf()
# plt.subplot(1,2,1)
# plt.imshow(c, interpolation='nearest', origin='lower')
# plt.title('CPU B')
# plt.colorbar()
# plt.subplot(1,2,2)
# plt.imshow(g, interpolation='nearest', origin='lower')
# plt.title('GPU B')
# plt.colorbar()
# plt.savefig('b.png')


# print('A matrix:')
# c = fitsio.read('cpu-a-scaled.fits')
# g = fitsio.read('gpu-a-scaled.fits')
# print('CPU:', c.shape)
# print('GPU:', g.shape)
# plt.clf()
# plt.subplot(1,2,1)
# plt.imshow(c[0,:,:], interpolation='nearest', origin='lower')
# plt.title('CPU A_0')
# plt.colorbar()
# plt.subplot(1,2,2)
# plt.imshow(g[0,:,:], interpolation='nearest', origin='lower')
# plt.title('GPU A_0')
# plt.colorbar()
# plt.savefig('a_0.png')


