import unittest
import tempfile
import os
from shellpython.helpers import Dir


class TestDirectory(unittest.TestCase):

    def test_relative_dirs(self):
        cur_dir = os.path.split(__file__)[0]

        with Dir(os.path.join(cur_dir, 'data')):
            self.assertEqual(os.path.join(cur_dir, 'data'), os.getcwd())
            with Dir(os.path.join('locator')):
                self.assertEqual(os.path.join(cur_dir, 'data', 'locator'), os.getcwd())

    def test_absolute_dirs(self):
        with Dir(tempfile.gettempdir()):
            self.assertEqual(tempfile.gettempdir(), os.getcwd())
