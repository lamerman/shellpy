import os
import unittest
import re
from shellpython import preprocessor


class TestPreprocessorIntermediate(unittest.TestCase):
    def setUp(self):
        cur_dir = os.path.split(__file__)[0]
        self.test_dir = os.path.join(cur_dir, 'data', 'preprocessor')

    def test_process_and_compare_file(self):
        with open(os.path.join(self.test_dir, 'test.spy')) as code_f:
            imdt = preprocessor.preprocess_code_to_intermediate(code_f.read())

        with open(os.path.join(self.test_dir, 'test.imdt')) as imdt_etalon_f:
            imdt_etalon = imdt_etalon_f.read()

        statement_regex = re.compile(r'((.+\n)+)')

        imdt_matches = [[match[0]] for match in statement_regex.findall(imdt)]
        imdt_etalon_matches = [[match[0]] for match in statement_regex.findall(imdt_etalon)]

        self.assertEquals(len(imdt_matches), len(imdt_etalon_matches))

        zipped_matches = map(list.__add__, imdt_matches, imdt_etalon_matches)
        for matches in zipped_matches:
            self.assertEquals(matches[0], matches[1])

