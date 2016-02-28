import unittest
import tempfile
import os
from os import path
from shellpython.helpers import Dir


class TestDirectory(unittest.TestCase):

    def test_relative_dirs(self):
        cur_dir = path.dirname(path.abspath(__file__))

        with Dir(path.join(cur_dir, 'data')):
            self.assertEqual(path.join(cur_dir, 'data'), os.getcwd())
            with Dir(path.join('locator')):
                self.assertEqual(path.join(cur_dir, 'data', 'locator'), os.getcwd())

    def test_absolute_dirs(self):
        with Dir(tempfile.gettempdir()):
            self.assertEqual(tempfile.gettempdir(), os.getcwd())
