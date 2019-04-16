"""
Pure Virtual Python (purepy) is a toolkit for helping with virtual classes so we can handle
a more complex ABCMeta scenario and alert us to problems before possible deep runtime code
is executed.

Example:
    
    from purepy import PureVirtual

    class Interface(metaclass=PureVirtual):
        pure_virtual = PureVirtual.new()

        @pure_virtual
        def save(self, filepath):
            raise NotImplementedError()

        @pure_virtual
        def load(self, filepath):
            raise NotImplementedError()

    class Overload(Interface):
        pure_virtual = PureVirtual.new()

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

import uuid
import public
import inspect

class PureVirtualError(Exception):
    """ General Error for purepy """
    pass

@public
class PureVirtual(type):
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
        if not hasattr(cls, '_has_base_class'):
            # The base class (must be)
            cls._has_base_class = True
        else:
            PureVirtual._assert_subclass_viable(cls, bases)

    def __call__(cls, *args, **kwargs):
        """
        Whenever we create an instance of a class, assert that it has all functions required
        to operate. In the event that it doesn't, utilize the 
        """
        inst = super(PureVirtual, cls).__call__(*args, **kwargs)
        if getattr(inst, 'pv_allow_base_instance', False):
            # If class variable defined, we can allow the pure virtual class to be made
            return inst

        functions = PureVirtual.pure_virtual_functions(inst)
        if functions:
            functions = ', '.join(functions)
            raise PureVirtualError("Cannot instantiate pure virtual class " +\
                                   f"'{inst.__class__.__name__}' with pure virtual functions: ({functions})")
        return inst

    # -- Class Methods (Publish Interface)

    @classmethod
    def new_class(cls, name):
        """
        When we want to begin a new class, this 
        """
        cls._registry[name] = []
        def pure_virtual(func, *args, **kwargs):
            func._is_pure_virtual = True
            func._pure_virtual_id = name
            cls._registry.setdefault(name, []).append(func)
            return func
        return pure_virtual

    @classmethod
    def new(cls):
        """
        Simpler call for the new_class() above - handles the registry name internally
        :return: Decorator function that can be used at a per-class level.
        """
        def _get_uuid():
            this_id = uuid.uuid4()
            while this_id in cls._registry:
                this_id = uuid.uuid4() # Should never really happen
            return this_id
        return cls.new_class(_get_uuid())

    @classmethod
    def pure_virtual_functions(cls, instance):
        """
        :return: list[str] of functions that are marked as pure virtual
        """
        funcs = []
        for name, call in inspect.getmembers(instance, predicate=inspect.isroutine):
            if getattr(call, '_is_pure_virtual', None):
                funcs.append(name)
        return funcs

    @classmethod
    def is_pure_virtual_class(cls, class_or_instance):
        """
        :return: bool True if there are any functions marked for pure_virtual
        """
        return (len(cls.pure_virtual_functions(class_or_instance)) > 0)

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
            wrong_layout = inspect.signature(wrong)
            proper_layout = inspect.signature(proper)
            return f"def {name}{wrong_layout}: -> def {name}{proper_layout}:"

        def _iterate(base):
            """
            Check each of the bases to do all assertion checks
            """
            must_overload = set()
            wrong_signature = set()

            for name, call in inspect.getmembers(base, predicate=inspect.isroutine):

                if getattr(call, '_is_pure_virtual', None):
                    attr = getattr(cls, name)
                    if call.__code__ is attr.__code__:
                        # Check 1: Have we overloaded all functions?
                        must_overload.add(call.__name__)
                    elif getattr(base, 'pv_explicit_args', True):
                        # Check 2: Do the arguments line up?
                        proper = inspect.getfullargspec(call)
                        attr_sig = inspect.getfullargspec(attr)
                        if proper != attr_sig:
                            wrong_signature.add(_signature(call.__name__, call, attr))

            if (len(must_overload) > 0) or (len(wrong_signature) > 0):
                error_message = "Pure Virtual Class Declaration:\n"

                if must_overload:
                    error_message +=  ("- '{}'{}: The following pure virtual functions must be overloaded from base: '{}'" +\
                                       " before class can be used:\n    -{}{}").format(
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
