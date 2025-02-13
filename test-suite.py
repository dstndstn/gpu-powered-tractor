import cupy
import pickle
import numpy as np
import pylab as plt
import fitsio
from tractor.brightness import NanoMaggies

from data_logger import log_data, data_log

tr = pickle.load(open('bad2.pickle','rb'))
tr.model_kwargs = {}
print('Got', tr)
tim = tr.images[0]
print('Image:', tim)

tr.images = [tim]
src = tr.catalog[0]
tr.modelMasks = [tr.modelMasks[0]]
#print('modelMasks:', tr.modelMasks)

# image is z band -- cut source to just z brightness
src.brightness = NanoMaggies(z=src.brightness.z)

print('Source:', src)

opt = tr.optimizer
from astrometry.util.plotutils import PlotSequence
opt.ps = PlotSequence('bad2')
opt.getSingleImageUpdateDirections(tr, shared_params=False)

print('Data log:', [k for k,v in data_log])

data_log = dict(data_log)
mod0_gpu = data_log['GPU.mod0']
mod0_cpu = data_log['Galaxy.getParamDerivatives.patch0']
print('mod0 cpu:', mod0_cpu)
print('mod0 gpu:', mod0_gpu.shape)

cgood = mod0_cpu.patch
ggood = mod0_gpu[0,:,:]

cgood = cgood.copy()
ggood = ggood.copy()
cgood[cgood == 0] = np.nan
ggood[ggood == 0] = np.nan
i,j = np.nonzero(np.isfinite(cgood))
i0 = min(i)
i1 = max(i)
j0 = min(j)
j1 = max(j)
cgood = cgood[i0:i1+1, j0:j1+1]
print('CPU mod0: good range x', j0, j1, 'y', i0, i1)
i,j = np.nonzero(np.isfinite(ggood))
gi0 = min(i)
gi1 = max(i)
gj0 = min(j)
gj1 = max(j)
ggood = ggood[gi0:gi1+1, gj0:gj1+1]
print('GPU mod0: good range x', gj0, gj1, 'y', gi0, gi1)

# HACK -- align on the brightest pixel
ci,cj = np.unravel_index(np.argmax(cgood), cgood.shape)
ch,cw = cgood.shape
i,j = np.unravel_index(np.argmax(ggood), ggood.shape)
slc = slice(i-ci, i-ci+ch), slice(j-cj, j-cj+cw)
ggood = ggood[slc]

plt.clf()
plt.subplot(1,3,1)
plt.imshow(cgood, interpolation='nearest', origin='lower')
plt.title('CPU mod0')
plt.colorbar()
plt.subplot(1,3,2)
plt.imshow(ggood, interpolation='nearest', origin='lower')
plt.title('GPU mod0')
plt.colorbar()
plt.subplot(1,3,3)
if cgood.shape == ggood.shape:
    diff = cgood - ggood
    mx = max(np.abs(diff[np.isfinite(diff)]))
    print('max diff:', mx)
    plt.imshow(diff, interpolation='nearest', origin='lower', vmin=-mx, vmax=mx)
    plt.colorbar()
    plt.title('CPU - GPU')
plt.savefig('mod0.png')

print('A matrix:')
c = fitsio.read('cpu-a-scaled.fits')
g = fitsio.read('gpu-a-scaled.fits')

c_A = c.copy()
g_A = g.copy()

c_planes = []
for i in range(c.shape[2]):
    nz = np.sum(c[:,:,i] != 0)
    print('CPU plane', i, ':', nz, 'non-zero')
    if nz > 0:
        c_planes.append(i)

c[c == 0] = np.nan
g[g == 0] = np.nan

print('CPU:', c.shape)
print('GPU:', g.shape)


for ii,ic in enumerate(c_planes):
    # Assume the GPU plane...
    ig = ii
    
    i,j = np.nonzero(np.isfinite(c[:,:,ic]))
    i0 = min(i)
    i1 = max(i)
    j0 = min(j)
    j1 = max(j)
    cgood = c[i0:i1+1, j0:j1+1, ic]
    print('CPU plane', ic, ': good range x', j0, j1, 'y', i0, i1)

    i,j = np.nonzero(np.isfinite(g[:,:,ig]))
    gi0 = min(i)
    gi1 = max(i)
    gj0 = min(j)
    gj1 = max(j)
    ggood = g[gi0:gi1+1, gj0:gj1+1, ig]
    print('GPU plane', ig, ': good range x', gj0, gj1, 'y', gi0, gi1)

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
