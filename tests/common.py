"""
Testing utilities
"""

import re
import unittest

from purepy.util import PY3

class PurePyTestCase(unittest.TestCase):

    # Python 2 / 3 compat
    def __init__(self, *args, **kwargs):
        super(PurePyTestCase, self).__init__(*args, **kwargs)
        if not PY3:
            self.assertRaisesRegex = self.assertRaisesRegexp
