import numpy as np

#import numpy.random.mtrand
#from numpy.random.mtrand import RandomState

class np_array_subclass(np.ndarray):
    def get(self):
        return self

    # https://numpy.org/doc/stable/user/basics.subclassing.html#simple-example-adding-an-extra-attribute-to-ndarray
    def __new__(subtype, shape, dtype=float, buffer=None, offset=0,
                strides=None, order=None, info=None):
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to InfoArray.__array_finalize__
        obj = super().__new__(subtype, shape, dtype,
                              buffer, offset, strides, order)
        # Finally, we must return the newly created object:
        return obj
    def __array_finalize__(self, obj):
        pass

#def nd_get(x):
#    return x
#np.ndarray.get = nd_get
np.ndarray = np_array_subclass

asarray = np.asarray
hypot = np.hypot
zeros = np.zeros
fft = np.fft
complex64 = np.complex64
array = np.array
dot = np.dot
einsum = np.einsum
ones = np.ones
arange = np.arange
tile = np.tile
exp = np.exp
pi = np.pi
newaxis = np.newaxis
logical_or = np.logical_or
atleast_1d = np.atleast_1d
logical_and = np.logical_and
sin = np.sin
pad = np.pad
conj = np.conj
real = np.real
float32 = np.float32
zeros_like = np.zeros_like
reshape = np.reshape
moveaxis = np.moveaxis
matmul = np.matmul
sqrt = np.sqrt
diagonal = np.diagonal

class duck(object):
    pass

def linalg_solve(a, b):
    print('linalg.solve: a', a.shape, 'b', b.shape)
    if len(a.shape) > 2:
        # A: (..., M, M)
        # B: (..., M)
        # X: (..., M)
        # But numpy only accepts
        # A: (..., M, M)
        # B: (..., M, K)
        # X: (..., M, K)
        b = b[..., :, np.newaxis]
        x = np.linalg.solve(a, b)
        return x[..., 0]
    return np.linalg.solve(a, b)

linalg = duck()
linalg.solve = linalg_solve
#linalg = np.linalg

