
import os
import sys

# Get to the right path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from purepy import PureVirtualMeta, PureVirtualError, pure_virtual

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

class BasicPurePyTestCase(unittest.TestCase):

    def setUp(self):
        @add_metaclass(PureVirtualMeta)
        class TestPure(object):
            @pure_virtual
            def foo(self, okay):
                raise NotImplementedError()
        self._class = TestPure

    def test_class_basic_pv_function(self):
        """ Initial Test """
        with self.assertRaises(PureVirtualError):
            class FailureOverload(self._class):
                pass


if __name__ == "__main__":
    unittest.main(verbosity=2)