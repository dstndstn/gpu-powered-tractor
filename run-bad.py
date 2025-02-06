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

import numpy as np
import pylab as plt
import fitsio

print('A matrix:')
c = fitsio.read('cpu-a-scaled.fits')
g = fitsio.read('gpu-a-scaled.fits')

c_A = c.copy()
g_A = g.copy()

for i in range(c.shape[2]):
    print('CPU plane', i, ':', np.sum(c[:,:,i] != 0), 'non-zero')

c[c == 0] = np.nan
g[g == 0] = np.nan

print('CPU:', c.shape)
print('GPU:', g.shape)


for ii,(ic,ig) in enumerate([(0,0), (1,1), (5,2), (6,3)]):
    i,j = np.nonzero(np.isfinite(c[:,:,ic]))
    i0 = min(i)
    j0 = min(j)
    i1 = max(i)
    j1 = max(j)
    cgood = c[i0:i1+1, j0:j1+1, ic]
    print('CPU plane', ic, ': good range x', j0, j1, 'y', i0, i1)

    i,j = np.nonzero(np.isfinite(g[:,:,ig]))
    gi0 = min(i)
    gj0 = min(j)
    gi1 = max(i)
    gj1 = max(j)
    ggood = g[gi0:gi1+1, gj0:gj1+1, ig]
    print('GPU plane', ig, ': good range x', gi0, gi1, 'y', gj0, gj1)

    print('CPU good:', cgood.shape)
    print('GPU good:', ggood.shape)

    plt.clf()
    plt.subplot(1,3,1)
    plt.imshow(cgood, interpolation='nearest', origin='lower')
    plt.title('CPU A_%i' % ic)
    plt.colorbar()
    plt.subplot(1,3,2)
    plt.imshow(ggood, interpolation='nearest', origin='lower')
    plt.title('GPU A_%i' % ig)
    plt.colorbar()
    plt.subplot(1,3,3)
    diff = cgood - ggood
    mx = max(np.abs(diff[np.isfinite(diff)]))
    print('max diff:', mx)
    plt.imshow(diff, interpolation='nearest', origin='lower', vmin=-mx, vmax=mx)
    plt.title('CPU - GPU')
    plt.colorbar()
    plt.savefig('a_%i.png' % ii)

print('B vector:')
c = fitsio.read('cpu-b.fits')
g = fitsio.read('gpu-b.fits')

print('CPU:', c.shape)
print('GPU:', g.shape)

# let's use the non-zero regions of the A matrices to decide what region to cut out of B
i,j,_ = np.nonzero(c_A)
ci0 = min(i)
ci1 = max(i)
cj0 = min(j)
cj1 = max(j)
i,j,_ = np.nonzero(g_A)
gi0 = min(i)
gi1 = max(i)
gj0 = min(j)
gj1 = max(j)

print('Nonzero region of A: CPU: %i x %i' % (ci1-ci0, cj1-cj0))
print('Nonzero region of A: GPU: %i x %i' % (gi1-gi0, gj1-gj0))

cgood = c[ci0:ci1+1, cj0:cj1+1]
ggood = g[gi0:gi1+1, gj0:gj1+1]
cgood[cgood == 0] = np.nan
ggood[ggood == 0] = np.nan
plt.clf()
plt.subplot(1,3,1)
plt.imshow(cgood, interpolation='nearest', origin='lower')
plt.title('CPU B')
plt.colorbar()
plt.subplot(1,3,2)
plt.imshow(ggood, interpolation='nearest', origin='lower')
plt.title('GPU B')
plt.colorbar()
plt.subplot(1,3,3)
diff = cgood - ggood
mx = max(np.abs(diff[np.isfinite(diff)]))
print('max diff:', mx)
plt.imshow(diff, interpolation='nearest', origin='lower', vmin=-mx, vmax=mx)
plt.title('CPU - GPU')
plt.colorbar()
plt.savefig('b.png')

c_X = fitsio.read('cpu-x.fits')
g_X = fitsio.read('gpu-x.fits')

print('CPU X:', c_X)
print('GPU X:', g_X)

print('CPU X', c_X.shape, 'A', c_A.shape)
print('GPU X', g_X.shape, 'A', g_A.shape)

c_AX = np.dot(c_A, c_X)
g_AX = np.dot(g_A, g_X)

print('c_AX', c_AX.shape)
print('g_AX', g_AX.shape)

cgood = c_AX[ci0:ci1+1, cj0:cj1+1]
ggood = g_AX[gi0:gi1+1, gj0:gj1+1]
cgood[cgood == 0] = np.nan
ggood[ggood == 0] = np.nan
plt.clf()
plt.subplot(1,3,1)
plt.imshow(cgood, interpolation='nearest', origin='lower')
plt.title('CPU AX')
plt.colorbar()
plt.subplot(1,3,2)
plt.imshow(ggood, interpolation='nearest', origin='lower')
plt.title('GPU AX')
plt.colorbar()
plt.subplot(1,3,3)
diff = cgood - ggood
mx = max(np.abs(diff[np.isfinite(diff)]))
print('max diff:', mx)
plt.imshow(diff, interpolation='nearest', origin='lower', vmin=-mx, vmax=mx)
plt.title('CPU - GPU')
plt.colorbar()
plt.savefig('a_x.png')
