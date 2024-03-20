# gpu-powered-tractor
Just a place to share files and docs about trying to get the Tractor working effectively on GPUs


## Single blob test case

This runs a single galaxy (this one: https://www.legacysurvey.org/viewer/?ra=185.9747&dec=19.4817&layer=ls-dr10&zoom=16).
It reads input from a pickle file, `/pscratch/sd/d/dstn/legacypipe-demo/oneblob-inputs-custom-185981p19474-10`

# On Perlmutter...

```
module use /global/common/software/desi/users/dstn/modulefiles/
module load tractor/perlmutter

git clone https://github.com/dstndstn/tractor.git tractor
cd tractor
python setup.py build_ext --inplace
export PYTHONPATH=$(pwd):${PYTHONPATH}
cd ..

python -m cProfile -o oneblob.pro run-one-blob.py
```

To explore the profile, I would copy that `oneblob.pro` to my laptop and then:
```
pyprof2calltree -i /tmp/oneblob.pro -o /tmp/oneblob.calltree
qcachegrind /tmp/oneblob.calltree
```

In production, we run cython on the tractor code, so that profile won't be exactly accurate, but it should at least give the ballpark.  I'm seeing about 45% of the total time going into `_realGetUnitFluxModelPatch()` (in `tractor/galaxy.py : ProfileGalaxy`).


