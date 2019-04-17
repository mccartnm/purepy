"""
Python 3+ features testing
"""
from tests import common

from purepy import PureVirtualMeta, PureVirtualError, pure_virtual

class PureVirtualTypeTesting(common.PurePyTestCase):

    def setUp(self):
        """
        Build a minor class to compare against with type settings
        """
        class Py3TestClass(metaclass=PureVirtualMeta):
            @pure_virtual
            def foo(self, filepath: str, garb: bool = False):
                pass
        self._class = Py3TestClass

    def test_strict_signature(self):
        """
        Assert that, by default, we _must_ adhear to the type hints
        on our classes
        """
        with self.assertRaises(PureVirtualError):
            class WrongHintSignature(self._class):
                def foo(self, filepath: str, garb = False):
                    pass

        class WriteHintSignature(self._class):
            def foo(self, filepath: str, garb: bool = False):
                pass

    def test_loose_hints(self):
        """
        Test the ability to have custom hints on the types
        """
        loose_hint_pure_virtual = PureVirtualMeta.new(strict_types=False)

        class Base(metaclass=PureVirtualMeta):
            @loose_hint_pure_virtual
            def foo(self, filepath: str, garb: bool = False):
                pass

        class ShouldBeOkay(Base):
            def foo(self, filepath, garb = False):
                pass

        with self.assertRaises(PureVirtualError):
            # Should still fail on the defaults
            class ShouldFail(Base):
                def foo(self, filepath, garb = True):
                    pass
