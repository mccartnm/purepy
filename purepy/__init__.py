"""
Pure Virtual Python (purepy) is a toolkit for helping with virtual classes so we can handle
a more complex ABCMeta scenario and alert us to problems before possible deep runtime code
is executed.

Example:
    
    from purepy import PureVirtualMeta, pure_virtual

    class Interface(metaclass=PureVirtualMeta):

        @pure_virtual
        def save(self, filepath):
            raise NotImplementedError()

        @pure_virtual
        def load(self, filepath):
            raise NotImplementedError()

    class Overload(Interface):
        pure_virtual = PureVirtualMeta.new()

        def save(self, filepath):
            print "saving"

        def load(self, filepath):
            print "loading"

        @pure_virtual
        def blarg(self, foo, bar):
            raise NotImplementedError()

    class Foo(Overload):
        def blarg(self, foo, bar):
            pass
"""
from __future__ import absolute_import

import uuid
import inspect
from purepy import util
from functools import wraps

# -- :EXPORT:
class PureVirtualError(Exception):
    """ General Error for purepy """
    pass

# -- :EXPORT:
class PureVirtualMeta(type):
    """
    The metaclass that handles our virtual class.
    """
    _registry = {}
    def __init__(cls, name, bases, dct):
        """
        Construct the class, if this is a subclass, then assert that it's either
        another pure virtual class that we will eventually overload or it meets
        all the requirements for being instantiated.
        """
        if not hasattr(cls, '_pv_has_base_class'):
            # The base class (must be)
            cls._pv_has_base_class = True
            cls._pv_base_class = cls
        else:
            PureVirtualMeta._assert_subclass_viable(cls, bases)

    def __call__(cls, *args, **kwargs):
        """
        Whenever we create an instance of a class, assert that it has all functions required
        to operate. In the event that it doesn't, utilize the 
        """
        inst = super(PureVirtualMeta, cls).__call__(*args, **kwargs)
        if getattr(inst, 'pv_allow_base_instance', False):
            # If class variable defined, we can allow the pure virtual class to be made
            return inst

        functions = PureVirtualMeta.pure_virtual_functions(inst)
        if functions:
            functions = ', '.join(map(lambda x: x.__name__, functions))
            raise PureVirtualError("Cannot instantiate pure virtual class " +\
                                   "'{}' with pure virtual functions: ({})".format(
                                        inst.__class__.__name__,
                                        functions
                                    ))
        return inst

    # -- Class Methods (Publish Interface)

    @classmethod
    def new_class(cls, name, **kwargs):
        """
        When we want to begin a new class, this 
        """
        cls._registry[name] = []
        def pure_virtual(func, *args, **func_kwargs):
            """
            Decorator to splay across our pure virtual functions
            """
            func._pv_is_pure_virtual = True

            details = {
                "_pv_virtual_id" : name,
                "_pv_strict_types" : kwargs.get("strict_types", True),
                "_pv_strict_defaults" : kwargs.get("strict_defaults", True),
                "_pv_force_not_impl" : kwargs.get("force_not_implemented", True),
            }
            cls._registry.setdefault(name, []).append(func)

            if details['_pv_force_not_impl']:
                def not_impl_wrapper(*args, **kwargs):
                    raise NotImplementedError("Illegal call to pure virtual function {}".format(func.__name__))
                func = util.give_signature(func, not_impl_wrapper)

            for k,v in details.items():
                setattr(func, k, v)

            return func

        pure_virtual._pv_virtual_id = name
        pure_virtual.id = lambda: pure_virtual._pv_virtual_id

        return pure_virtual

    @classmethod
    def new(cls, **kwargs):
        """
        Simpler call for the new_class() above - handles the registry name internally
        :return: Decorator function that can be used at a per-class level.
        """
        def _get_uuid():
            this_id = uuid.uuid4()
            while this_id in cls._registry:
                # We should never really get here.
                this_id = uuid.uuid4() # pragma: no cover
            return this_id
        return cls.new_class(_get_uuid(), **kwargs)

    @classmethod
    def pure_virtual_functions(cls, instance):
        """
        :return: list[str] of functions that are marked as pure virtual
        """
        funcs = []
        for name, call in inspect.getmembers(instance, predicate=inspect.isroutine):
            if getattr(call, '_pv_is_pure_virtual', None):
                funcs.append(call)
        return funcs

    @classmethod
    def is_pure_virtual_class(cls, class_or_instance):
        """
        :return: bool True if there are any functions marked for pure_virtual
        """
        return (len(cls.pure_virtual_functions(class_or_instance)) > 0)

    @classmethod
    def virtual_functions_from_id(cls, identifier):
        """
        Get all virtual functions for a given identifier
        :param: identifier - str that points to our register.
        :return: list[callable] of pure virtual functions 
        """
        return cls._registry.get(identifier, [])

    # -- Private Functions

    @classmethod
    def _assert_subclass_viable(pv, cls, bases):
        """
        Internal function that does the in line subclass verification.
        This will raise a PureVirtualError if something is amiss
        :return: None
        """
        def _class_file():
            return (' ' + cls.__file__) if hasattr(cls, '__file__') else ''

        def _signature(name, proper, wrong):
            wrong_layout = util.signature(wrong)
            proper_layout = util.signature(proper)
            return "def {name}{wrong_layout}: -> def {name}{proper_layout}:".format(**locals())

        def _iterate(base):
            """
            Check each of the bases to do all assertion checks
            """
            must_overload = set()
            wrong_signature = set()

            for name, call in inspect.getmembers(base, predicate=inspect.isroutine):

                if getattr(call, '_pv_is_pure_virtual', None):
                    attr = getattr(cls, name)

                    # For override decorator
                    if getattr(attr, '_pv_override', False):
                        attr = attr.pv_overloaded_function

                    if call.__code__ is attr.__code__:
                        # Check 1: Have we overloaded all functions?
                        sig = util.signature(call)
                        must_overload.add("def {}{}".format(call.__name__, sig))
                    elif getattr(base, 'pv_explicit_args', True):
                        # Check 2: Do the arguments line up?
                        proper = util.getfullargspec(call)._asdict()
                        attr_sig = util.getfullargspec(attr)._asdict()

                        if not call._pv_strict_types and util.PY3:
                            proper.pop('annotations')
                            attr_sig.pop('annotations')
                        if not call._pv_strict_defaults:
                            proper.pop('defaults')
                            attr_sig.pop('defaults')

                        if proper != attr_sig:
                            wrong_signature.add(_signature(call.__name__, call, attr))

            if (len(must_overload) > 0) or (len(wrong_signature) > 0):
                error_message = "Virtual Class Declaration:\n"

                if must_overload:
                    error_message +=  ("- '{}'{}: The following pure virtual functions must be overloaded from base: '{}'" +\
                                       " before class can be used:\n    - {}{}").format(
                                          cls.__name__,
                                          _class_file(),
                                          base.__name__,
                                          '\n    - '.join(list(must_overload)),
                                          '\n' if len(wrong_signature) > 0 else ''
                                      )
                if wrong_signature:
                    error_message += ("- '{}'{}: The following overload functions have the wrong signature " +\
                                      "from base: '{}'\n    - {}").format(
                                          cls.__name__,
                                          _class_file(),
                                          base.__name__,
                                          "\n    - ".join(wrong_signature)
                                      )

                raise PureVirtualError(error_message)

        list(map(_iterate, bases)) # Cast to list for Python 3


# -- :EXPORT:
pure_virtual = PureVirtualMeta.new() # Default Global Register


# -- :EXPORT:
class override(object):
    """
    In the future this decorator may be able to do more but for now it's a
    simple passthrough developers can use to mark their functions as
    overloaded for ease-of-use
    """
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, function, *args, **kwargs):
        self._function = function

        @wraps(function)
        def _wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        _wrapper._pv_override = True
        _wrapper.pv_overloaded_function = self._function
        return _wrapper


if __name__ == "__main__": # pragma: no cover
    my_pure_virtual = PureVirtualMeta.new(strict_types=False, strict_defaults=False)

    @util.add_metaclass(PureVirtualMeta)
    class Interface(object):

        pv_allow_base_instance = True

        @my_pure_virtual
        def save(self, filepath=None):
            print ("glarb")

    class Overload(Interface):
        def save(self, filepath = "bar"):
            print ("foo")

    inst = Interface()
    inst.save()
