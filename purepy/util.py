"""
Minor internal utilities. Probably don't need these in your project
"""

import sys
import inspect

PY3 = sys.version_info[0] >= 3

# Compatability for 2.7
if PY3:
    getfullargspec = inspect.getfullargspec
    signature = inspect.signature

else:
    getfullargspec = inspect.getargspec

    def _custom_sig(func):
        spec = getfullargspec(func)
        sig = ""
        defauts = []
        args = []
        if spec.defaults:
            args = spec.args[:len(spec.defaults)]
            defaults = zip(spec.args[len(spec.defaults):], spec.defaults)
        if args:
            sig = ", ".join(args)
        if defaults:
            sig += ", " + ", ".join(["{}={}".format(k,v) for k,v in defaults])
        if spec.varargs:
            sig += ", *" + spec.varargs
        if spec.keywords:
            sig += ", **" + spec.keywords
        return "({})".format(sig)

    signature = _custom_sig


def add_metaclass(metaclass):
    '''!
    Taken from the six module. Python 2 and 3 compatible.
    '''
    def wrapper(cls):
        """
        The actual wrapper. take the given class and return one that
        contains the proper metaclass.
        """
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper