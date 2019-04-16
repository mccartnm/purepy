"""
Minor internal utilities. Probably don't need these in your project
"""

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