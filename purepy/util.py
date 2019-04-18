"""
Minor internal utilities. Probably don't need these in your project
"""
from __future__ import print_function

import sys
import inspect
import itertools
import copy

PY3 = sys.version_info[0] >= 3

# Compatability for 2.7
if PY3:
    getfullargspec = inspect.getfullargspec
    signature = inspect.signature

else: # pragma: no cover
    getfullargspec = inspect.getargspec

    def _custom_sig(func):
        spec = getfullargspec(func)
        sig = ""
        defaults = []
        args = []
        if spec.defaults:
            args = spec.args[:len(spec.defaults)]
            defaults = zip(spec.args[len(spec.defaults):], spec.defaults)
        else:
            args = spec.args
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
    """
    Taken from the six module. Python 2 and 3 compatible.
    """
    def wrapper(cls):
        """
        The actual wrapper. take the given class and return one that contains the proper metaclass.
        """
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


# Atomic counter
_compiler_count = itertools.count()

def give_signature(original, impl):
    """
    Watered down version of the makefun package create_function to let us compare apples to apples when
    force_not_implemented is active
    """
    def _impl_call_string(spec):
        output = ""
        if spec.args:
            output = ", ".join(spec.args)
        if spec.varargs:
            output += ", *" + spec.varargs
        if hasattr(spec, 'keywords') and spec.keywords:
            output += ", **" + spec.keywords # pragma: no cover
        elif hasattr(spec, 'varkw') and spec.varkw:
            output += ", **" + spec.varkw
        return output

    def _clean_evaldict(ed, n, args):
        try:
            del ed[n]
        except KeyError:
            pass
        for d in args:
            try:
                del ed[d]
            except KeyError:
                pass
        return ed

    def _compile_function(n, args, body, ed):
        """
        Actually compile our function together
        """
        for d in args:
            if d in ('_func_', '_impl_'):
                raise NameError(
                    "Cannot use '{}' on virtual function when force_not_implemented is active".format(d)
                )

        filename = '<purepyfunc-{}>'.format(next(_compiler_count))
        try:
            code = compile(body, filename, 'single')
            exec(code, ed)
        except: # pragma: no cover
            # Not covering because we shouldn't get here
            print ("Error creating virtual wrapped function: ", file=sys.stderr)
            print (body, file=sys.stderr)
            raise

        return evaldict[n]

    try:
        frame = sys._getframe(2)
    except AttributeError: # pragma: no cover
        frame = None

    try:
        module_name = frame.f_globals.get('__name__', '?')

        evaldict = copy.copy(frame.f_globals)
        evaldict.update(frame.f_locals)
    except AttributeError: # pragma: no cover (py2)
        module_name = '?'
        evaldict = {}

    argspec = getfullargspec(original)
    name = original.__name__

    # TODO Possibly support generators and coroutines.
    # Not vital for the current state of purepy
    function_string = "def {}{}:\n    return _impl_({})\n".format(
        name, signature(original), _impl_call_string(argspec)
    )

    params = argspec.args
    if argspec.varargs:
        params += [argspec.varargs]
    if hasattr(argspec, 'keywords') and argspec.keywords:
        params += [argspec.keywords] # pragma: no cover (py2)
    if hasattr(argspec, 'varkw') and argspec.varkw:
        params += [argspec.varkw]

    _clean_evaldict(evaldict, name, params)
    evaldict['_impl_'] = impl    

    function = _compile_function(name, params, function_string, evaldict)
    function.__name__ = name
    function.__qualname__ = name
    function.__doc__ = original.__doc__
    function.__dict__ = original.__dict__
    function.__defaults__ = original.__defaults__
    if hasattr(original, '__annotations__'):
        function.__annotations__ = original.__annotations__
    function.__module__ = original.__module__

    return function
