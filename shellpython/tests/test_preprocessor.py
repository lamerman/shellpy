import unittest
import getpass
import tempfile
import os.path
import mock
from shellpython import preprocessor


class TestCodeStart(unittest.TestCase):
    def test_simple(self):
        cmd = 'x = `echo 1'
        intermediate = preprocessor._process_code_start(cmd)
        self.assertEqual(intermediate, 'x = start_shexe(echo 1)shexe()shexe')

    def test_very_simple(self):
        cmd = '`echo 1'
        intermediate = preprocessor._process_code_start(cmd)
        self.assertEqual(intermediate, 'start_shexe(echo 1)shexe()shexe')

    def test_with_param(self):
        cmd = 'x = p`echo 1'
        intermediate = preprocessor._process_code_start(cmd)
        self.assertEqual(intermediate, 'x = start_shexe(echo 1)shexe(p)shexe')

    def test_multiline(self):
        cmd = 'i = 1\nx = `echo 1\ni = 2'
        intermediate = preprocessor._process_code_start(cmd)
        self.assertEqual(intermediate, 'i = 1\nx = start_shexe(echo 1)shexe()shexe\ni = 2')

    def test_no_false_positive_both(self):
        cmd = 'x = `echo 1`'
        intermediate = preprocessor._process_code_start(cmd)
        self.assertEqual(intermediate, 'x = `echo 1`')


class TestCodeBoth(unittest.TestCase):
    def test_simple(self):
        cmd = 'x = `echo 1`'
        intermediate = preprocessor._process_code_both(cmd)
        self.assertEqual(intermediate, 'x = both_shexe(echo 1)shexe()shexe')

    def test_very_simple(self):
        cmd = '`echo 1`'
        intermediate = preprocessor._process_code_both(cmd)
        self.assertEqual(intermediate, 'both_shexe(echo 1)shexe()shexe')

    def test_with_param(self):
        cmd = 'x = p`echo 1`'
        intermediate = preprocessor._process_code_both(cmd)
        self.assertEqual(intermediate, 'x = both_shexe(echo 1)shexe(p)shexe')

    def test_multiline(self):
        cmd = 'i = 1\nx = `echo 1`\ni = 2'
        intermediate = preprocessor._process_code_both(cmd)
        self.assertEqual(intermediate, 'i = 1\nx = both_shexe(echo 1)shexe()shexe\ni = 2')

    def test_no_false_positive_start(self):
        cmd = 'x = `echo 1'
        intermediate = preprocessor._process_code_both(cmd)
        self.assertEqual(intermediate, 'x = `echo 1')


class TestLongLines(unittest.TestCase):
    def test_simple_two_lines(self):
        cmd = 'x = `echo Very \\\n long line'
        intermediate = preprocessor._process_long_lines(cmd)
        self.assertEqual(intermediate, 'x = longline_shexe(echo Very \\\n long line)shexe()shexe')

    def test_very_simple_two_lines(self):
        cmd = '`echo Very \\\n long line'
        intermediate = preprocessor._process_long_lines(cmd)
        self.assertEqual(intermediate, 'longline_shexe(echo Very \\\n long line)shexe()shexe')

    def test_simple_three_lines(self):
        cmd = 'x = `echo Very \\\n long \\\n line'
        intermediate = preprocessor._process_long_lines(cmd)
        self.assertEqual(intermediate, 'x = longline_shexe(echo Very \\\n long \\\n line)shexe()shexe')

    def test_simple_two_lines_with_param(self):
        cmd = 'x = p`echo Very \\\n long line'
        intermediate = preprocessor._process_long_lines(cmd)
        self.assertEqual(intermediate, 'x = longline_shexe(echo Very \\\n long line)shexe(p)shexe')

    def test_no_false_positive_start(self):
        cmd = 'x = `echo 1'
        intermediate = preprocessor._process_long_lines(cmd)
        self.assertEqual(intermediate, 'x = `echo 1')


class TestMultiline(unittest.TestCase):
    def test_simple_one_line(self):
        cmd = 'x = `\necho 1\n`'
        intermediate = preprocessor._process_multilines(cmd)
        self.assertEqual(intermediate, 'x = multiline_shexe(echo 1; \\\n)shexe()shexe')

    def test_simple_one_line_with_param(self):
        cmd = 'x = p`\necho 1\n`'
        intermediate = preprocessor._process_multilines(cmd)
        self.assertEqual(intermediate, 'x = multiline_shexe(echo 1; \\\n)shexe(p)shexe')

    def test_very_simple_one_line(self):
        cmd = '`\necho 1\n`'
        intermediate = preprocessor._process_multilines(cmd)
        self.assertEqual(intermediate, 'multiline_shexe(echo 1; \\\n)shexe()shexe')

    def test_simple_two_lines(self):
        cmd = 'x = `\necho 1\necho 2\n`'
        intermediate = preprocessor._process_multilines(cmd)
        self.assertEqual(intermediate, 'x = multiline_shexe(echo 1; \\\necho 2; \\\n)shexe()shexe')

    def test_no_false_positive_start(self):
        cmd = 'x = `echo 1'
        intermediate = preprocessor._process_multilines(cmd)
        self.assertEqual(intermediate, 'x = `echo 1')

    def test_no_false_positive_both(self):
        cmd = 'x = `echo 1`'
        intermediate = preprocessor._process_multilines(cmd)
        self.assertEqual(intermediate, 'x = `echo 1`')


class TestEscape(unittest.TestCase):
    def test_escape_nothing(self):
        intermediate = 'x = start_shexe(echo 1)shexe()shexe'
        escaped = preprocessor._escape(intermediate)
        self.assertEqual(escaped, intermediate)

    def test_escape_quote(self):
        intermediate = 'x = start_shexe(echo \'1\')shexe()shexe'
        escaped = preprocessor._escape(intermediate)
        self.assertEqual(escaped, 'x = start_shexe(echo \\\'1\\\')shexe()shexe')


class TestIntermediateToFinal(unittest.TestCase):
    def test_common(self):
        intermediate = 'x = int_shexe(expr)shexe(param)shexe'
        final = preprocessor._intermediate_to_final(intermediate)
        self.assertEqual(final, "x = exe('expr'.format(**dict(locals(), **globals())),'param')")


class TestFileOperations(unittest.TestCase):
    def test_translate_to_temp(self):
        username = getpass.getuser()
        translated_path = preprocessor._translate_to_temp_path('/code/test')

        expected_path = os.path.join(tempfile.gettempdir(), 'shellpy_' + username, 'code/test')

        self.assertEqual(translated_path, expected_path)


class TestMeta(unittest.TestCase):
    def setUp(self):
        cur_dir = os.path.split(__file__)[0]
        self.test_dir = os.path.join(cur_dir, 'data', 'preprocessor')

    @mock.patch('os.path.getmtime', return_value=1111111111.11)
    def test_is_compilation_needed_time_match(self, getmtime_mock_arg):
        compilation_needed = preprocessor._is_compilation_needed('mocked_spy_file',
                                                                 os.path.join(self.test_dir, 'meta.py'))
        self.assertFalse(compilation_needed)

    @mock.patch('os.path.getmtime', return_value=0)
    def test_is_compilation_needed_time_not_match(self, getmtime_mock_arg):
        compilation_needed = preprocessor._is_compilation_needed('mocked_spy_file',
                                                                 os.path.join(self.test_dir, 'meta.py'))
        self.assertTrue(compilation_needed)

    def test_is_compilation_needed_out_does_not_exist(self):
        compilation_needed = preprocessor._is_compilation_needed('mocked_spy_file',
                                                                 'non_existing_py_file')
        self.assertTrue(compilation_needed)


class TestEncoding(unittest.TestCase):

    def setUp(self):
        self.header_text = '''#!/usr/bin/env python
#shellpy-encoding
#shellpy-meta:{meta}

import sys
import os
'''

        self.header_text_with_encoding = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
#shellpy-meta:{meta}

import sys
import os
'''

    def test_no_encoding(self):
        script_text = '''print 1
'''
        header_text_with_encoding = preprocessor._add_encoding_to_header(self.header_text, script_text)
        self.assertEqual(header_text_with_encoding, self.header_text)

    def test_encoding_on_first_line(self):
        script_text = '''# -*- coding: utf-8 -*-
print 1
'''
        header_text_with_encoding = preprocessor._add_encoding_to_header(self.header_text, script_text)
        self.assertEqual(header_text_with_encoding, self.header_text_with_encoding)

    def test_encoding_on_second_line(self):
        script_text = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
print 1
'''
        header_text_with_encoding = preprocessor._add_encoding_to_header(self.header_text, script_text)
        self.assertEqual(header_text_with_encoding, self.header_text_with_encoding)

    def test_encoding_on_third_line(self):
        script_text = '''#!/usr/bin/env python
# some comment
# -*- coding: utf-8 -*-
print 1
'''
        header_text_with_encoding = preprocessor._add_encoding_to_header(self.header_text, script_text)
        self.assertEqual(header_text_with_encoding, self.header_text)


