import os
import sys
import unittest
from shellpython import locator


class TestLocateModule(unittest.TestCase):
    def setUp(self):
        cur_dir = os.path.split(__file__)[0]
        self.test_dir = os.path.join(cur_dir, 'data', 'locator')

        sys.path.append(self.test_dir)

    def tearDown(self):
        sys.path.remove(self.test_dir)

    def test_files(self):
        self.assertIsNotNone(locator.locate_spy_file('testfilespy'))
        self.assertIsNone(locator.locate_spy_file('testfilepy'))
        self.assertIsNone(locator.locate_spy_file('non_existent_file'))
        self.assertIsNone(locator.locate_spy_file('testmodulespy'))

    def test_modules(self):
        self.assertIsNotNone(locator.locate_spy_module('testmodulespy'))
        self.assertIsNone(locator.locate_spy_module('testmodulepy'))
        self.assertIsNone(locator.locate_spy_module('testmoduleempty'))
        self.assertIsNone(locator.locate_spy_module('testfilepy'))
        self.assertIsNone(locator.locate_spy_module('non_existent_file'))
