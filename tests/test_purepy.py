from __future__ import absolute_import

import os
import sys

# Get to the right path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from purepy import PureVirtualMeta, PureVirtualError, pure_virtual
from purepy.util import add_metaclass, PY3

from tests import common

# ----------------------------------------------------------------------------------------------
# -- Basic Test Case
# ----------------------------------------------------------------------------------------------
class BasicPurePyTestCase(common.PurePyTestCase):
    """
    Test basic procedures of purepy
    """

    def setUp(self):
        """
        Create a generic class structure for the tests
        """

        @add_metaclass(PureVirtualMeta)
        class TestPure(object):
            @pure_virtual
            def foo(self, okay=None, **kwargs):
                raise NotImplementedError()

            @pure_virtual
            def bar(self, path):
                raise NotImplementedError()

        self._num_pv = 2
        self._class = TestPure

    def test_count_functions(self):
        """
        Test that we can grab each pv function
        """
        self.assertEqual(len(PureVirtualMeta.pure_virtual_functions(self._class)), self._num_pv)

    def test_cannot_create_pv_instance(self):
        """
        Test to make sure that, by default, PV classes cannot be created
        """
        with self.assertRaises(PureVirtualError):
            self._class()

    def test_class_failure_to_overload(self):
        """
        Test exception on creating class that has not overloaded functions
        """
        err = 'must be overloaded from base'
        with self.assertRaisesRegex(PureVirtualError, err):
            class FailureOverloadAll(self._class):
                pass

        with self.assertRaisesRegex(PureVirtualError, err):
            class FailureOverloadOne(self._class):
                def foo(self, okay=None, **kwargs):
                    pass

    def test_class_overload_ok(self):
        """
        Test properlly overloaded functions 
        """
        class Okay(self._class):
            def foo(self, okay=None, **kwargs):
                pass

            def bar(self, path):
                pass

    def test_basic_signature(self):
        """
        Test that simple (py2/3) signature alignment works by default
        """
        err = 'overload functions have the wrong signature'
        with self.assertRaisesRegex(PureVirtualError, err):
            class TestSignature(self._class):
                def foo(self, okay, **kwargs):
                    pass

                def bar(self, path):
                    pass

        with self.assertRaisesRegex(PureVirtualError, err):
            class TestSignatureTwo(self._class):
                def foo(self, okay=None):
                    pass

                def bar(self, path):
                    pass

    def test_custom_decortator(self):
        """
        Test the custom decortar of our PureVirtualMeta interface
        """
        alt_pv_decorator = PureVirtualMeta.new(strict_defaults=False)

        @add_metaclass(PureVirtualMeta)
        class AltBase(object):

            @alt_pv_decorator
            def foo(self, bar=None):
                pass

        # Still cannot change our argument names
        with self.assertRaises(PureVirtualError):
            class AltDerived(AltBase):
                def foo(self, spanner):
                    pass

        # But we can augment the default
        class AltDerived2(AltBase):
            def foo(self, bar="different default"):
                pass

        self.assertEqual(len(PureVirtualMeta.virtual_functions_from_id(alt_pv_decorator.id())), 1)


    def test_instance_loading_okay(self):
        """
        Test the abilities of the pv_allow_base_instance class variable
        """
        @add_metaclass(PureVirtualMeta)
        class OkayToCreate(object):
            pv_allow_base_instance = True

            @pure_virtual
            def okay_to_create(self):
                raise NotImplementedError()

        ok = OkayToCreate()

        @add_metaclass(PureVirtualMeta)
        class NotARealPureVirtual(object):

            def okay_to_create(self):
                raise NotImplementedError()

        not_a_pv = NotARealPureVirtual()

        self.assertTrue(PureVirtualMeta.is_pure_virtual_class(ok))
        self.assertFalse(PureVirtualMeta.is_pure_virtual_class(not_a_pv))

    def test_force_not_impl(self):
        """
        Test that even defined classes with a pure virtual function, by default
        are forced to a NotImplementedError() and show the ability to remove that
        restrcition
        """
        alt_pv_decorator = PureVirtualMeta.new(force_not_implemented=False)

        @add_metaclass(PureVirtualMeta)
        class ForceImpl(object):
            pv_allow_base_instance = True

            @pure_virtual
            def foo(self):
                return "Cannot get to me!"

            @alt_pv_decorator
            def bar(self):
                return "Get to me!"

        inst = ForceImpl()

        with self.assertRaises(NotImplementedError):
            print (inst.foo())

        self.assertEqual(inst.bar(), "Get to me!")

    def test_force_impl_restrict_names(self):
        """
        Select argument names are not allowed for pure_virtual functions that utilize
        forced not implemented wrapper
        """
        with self.assertRaisesRegex(NameError, "Cannot use '_func_'"):
            @add_metaclass(PureVirtualMeta)
            class ForceImpl(object):
                @pure_virtual
                def foo(self, _func_):
                    return None # cannot get here

        with self.assertRaisesRegex(NameError, "Cannot use '_impl_'"):
            @add_metaclass(PureVirtualMeta)
            class ForceImpl(object):
                @pure_virtual
                def foo(self, _impl_, *args):
                    return None # cannot get here


# ----------------------------------------------------------------------------------------------
# -- Main Function to run tests
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(BasicPurePyTestCase))

    if PY3:
        # Python 3 only - syntax and other changes that break on import
        from tests import test_py3
        suite.addTests(loader.loadTestsFromModule(test_py3))

    unittest.TextTestRunner(verbosity=2).run(suite)