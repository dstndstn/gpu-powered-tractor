# generic version of tractor_math.py

# singleton
_client = None

class MathPipeClient(object):
    @classmethod
    def get(cls):
        global _client
        if _client is None:
            _client = MathPipeClient()
        return _client

    def __init__(self):
        self._math_pipe = None

    def set_pipe(self, p):
        self._math_pipe = p

    # General attribute access:
    # We want callers to be able to call arbitrarily-named functions
    # by going
    #   MathPipeClient.get().FUNCNAME(a,b,c,d=d,e=e)
    # which will hit this __getattr__ call to look up FUNCNAME.
    # We must return a callable that will perform the math-pipe action.
    def __getattr__(self, name):
        def callable(*args, **kwargs):
            return self.call_function(name, *args, **kwargs)
        return callable

    def call_function(self, name, *args, **kwargs):
        print('mathpipe client: calling function', name, 'with args', args, 'and kwargs', kwargs)
        # Here's the actual action!
        self._math_pipe.send((name, args, kwargs))
        r = self._math_pipe.recv()
        print('mathpipe client: returning result', r)
        return r

def mathpipe_client():
    return MathPipeClient.get()
