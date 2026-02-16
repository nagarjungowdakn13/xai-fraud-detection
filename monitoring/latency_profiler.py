"""Latency Profiler Decorators"""
import time
from functools import wraps

def time_block(name):
    def deco(fn):
        @wraps(fn)
        def inner(*a, **kw):
            start = time.time()
            r = fn(*a, **kw)
            dur = (time.time()-start)*1000
            print({'component': name, 'ms': round(dur,2)})
            return r
        return inner
    return deco
