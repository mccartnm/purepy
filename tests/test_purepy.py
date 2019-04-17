
import os
import sys

# Get to the right path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from purepy import PureVirtualMeta, PureVirtualError, pure_virtual
from purepy.util import add_metaclass

class BasicPurePyTestCase(unittest.TestCase):

    def setUp(self):
        @add_metaclass(PureVirtualMeta)
        class TestPure(object):
            @pure_virtual
            def foo(self, okay=None, **kwargs):
                raise NotImplementedError()
        self._class = TestPure

    def test_class_basic_pv_function(self):
        """ Initial Test """
        with self.assertRaises(PureVirtualError):
            class FailureOverload(self._class):
                pass


if __name__ == "__main__":
    unittest.main(verbosity=2)