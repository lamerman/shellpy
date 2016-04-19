#!/usr/bin/env python
import os
import stat
import tempfile
import re
import getpass
import json

spy_file_pattern = re.compile(r'(.*)\.spy$')
shellpy_meta_pattern = re.compile(r'#shellpy-meta:(.*)')
shellpy_encoding_pattern = '#shellpy-encoding'


def preprocess_module(module_path):
    """The function compiles a module in shellpy to a python module, walking through all the shellpy files inside of
    the module and compiling all of them to python

    :param module_path: The path of module
    :return: The path of processed module
    """
    for item in os.walk(module_path):
        path, dirs, files = item
        for file in files:
            if spy_file_pattern.match(file):
                filepath = os.path.join(path, file)
                preprocess_file(filepath, is_root_script=False)

    return _translate_to_temp_path(module_path)


def preprocess_file(in_filepath, is_root_script, python_version=None):
    """Coverts a single shellpy file to python

    :param in_filepath: The path of shellpy file to be processed
    :param is_root_script: Shows whether the file being processed is a root file, which means the one
            that user executed
    :param python_version: version of python, needed to set correct header for root scripts
    :return: The path of python file that was created of shellpy script
    """

    new_filepath = spy_file_pattern.sub(r"\1.py", in_filepath)
    out_filename = _translate_to_temp_path(new_filepath)
    out_folder_path = os.path.dirname(out_filename)

    if not is_root_script and not _is_compilation_needed(in_filepath, out_filename):
        # TODO: cache root also
        # TODO: if you don't compile but it's root, you need to change to exec
        return out_filename

    if not os.path.exists(out_folder_path):
        os.makedirs(out_folder_path, mode=0o700)

    header_data = _get_header(in_filepath, is_root_script, python_version)

    with open(in_filepath, 'r') as f:
        code = f.read()

        out_file_data = _add_encoding_to_header(header_data, code)

        intermediate = _preprocess_code_to_intermediate(code)
        processed_code = _intermediate_to_final(intermediate)

        out_file_data += processed_code

    with open(out_filename, 'w') as f:
        f.write(out_file_data)

    in_file_stat = os.stat(in_filepath)
    os.chmod(out_filename, in_file_stat.st_mode)

    if is_root_script:
        os.chmod(out_filename, in_file_stat.st_mode | stat.S_IEXEC)

    return out_filename


def _get_username():
    """Returns the name of current user. The function is used in construction of the path for processed shellpy files on
    temp file system

    :return: The name of current user
    """
    try:
        n = getpass.getuser()
        return n
    except:
        return 'no_username_found'


def _translate_to_temp_path(path):
    """Compiled shellpy files are stored on temp filesystem on path like this /{tmp}/{user}/{real_path_of_file_on_fs}
    Every user will have its own copy of compiled shellpy files. Since we store them somewhere else relative to
    the place where they actually are, we need a translation function that would allow us to easily get path
    of compiled file

    :param path: The path to be translated
    :return: The translated path
    """
    absolute_path = os.path.abspath(path)
    relative_path = os.path.relpath(absolute_path, os.path.abspath(os.sep))
    # TODO: this will not work in win where root is C:\ and absolute_in_path
    # is on D:\
    translated_path = os.path.join(tempfile.gettempdir(), 'shellpy_' + _get_username(), relative_path)
    return translated_path


def _is_compilation_needed(in_filepath, out_filepath):
    """Shows whether compilation of input file is required. It may be not required if the output file did not change

    :param in_filepath: The path of shellpy file to be processed
    :param out_filepath: The path of the processed python file. It may exist or not.
    :return: True if compilation is needed, False otherwise
    """
    if not os.path.exists(out_filepath):
        return True

    in_mtime = os.path.getmtime(in_filepath)

    with open(out_filepath, 'r') as f:
        for i in range(0, 3):  # scan only for three first lines
            line = f.readline()
            line_result = shellpy_meta_pattern.search(line)
            if line_result:
                meta = line_result.group(1)
                meta = json.loads(meta)
                if str(in_mtime) == meta['mtime']:
                    return False

    return True


def _get_header(filepath, is_root_script, python_version):
    """To execute converted shellpy file we need to add a header to it. The header contains needed imports and
    required code

    :param filepath: A shellpy file that is being converted. It is needed to get modification time of it and save it
    to the created python file. Then this modification time will be used to find out whether recompilation is needed
    :param is_root_script: Shows whether the file being processed is a root file, which means the one
            that user executed
    :param python_version: version of python, needed to set correct header for root scripts
    :return: data of the header
    """
    header_name = 'header_root.tpl' if is_root_script else 'header.tpl'
    header_filename = os.path.join(os.path.dirname(__file__), header_name)

    with open(header_filename, 'r') as f:
        header_data = f.read()
        mod_time = os.path.getmtime(filepath)
        meta = {'mtime': str(mod_time)}

        header_data = header_data.replace('{meta}', json.dumps(meta))

        if is_root_script:
            executables = {
                2: '#!/usr/bin/env python',
                3: '#!/usr/bin/env python3'
            }
            header_data = header_data.replace('#shellpy-python-executable', executables[python_version])

        return header_data


def _preprocess_code_to_intermediate(code):
    """Before compiling to actual python code all expressions are converted to universal intermediate form
    It is very convenient as it is possible to perform common operations for all expressions
    The intemediate form looks like this:
    longline_shexe(echo 1)shexe(p)shexe

    :param code: code to convert to intermediate form
    :return: converted code
    """
    processed_code = _process_multilines(code)
    processed_code = _process_long_lines(processed_code)
    processed_code = _process_code_both(processed_code)
    processed_code = _process_code_start(processed_code)

    return _escape(processed_code)


def _process_multilines(script_data):
    """Converts a pyshell multiline expression to one line pyshell expression, each line of which is separated
    by semicolon. An example would be:
    f = `
    echo 1 > test.txt
    ls -l
    `

    :param script_data: the string of the whole script
    :return: the shellpy script with multiline expressions converted to intermediate form
    """
    code_multiline_pattern = re.compile(r'^([^`\n\r]*?)([a-z]*)`\s*?$[\n\r]{1,2}(.*?)`\s*?$', re.MULTILINE | re.DOTALL)

    script_data = code_multiline_pattern.sub(r'\1multiline_shexe(\3)shexe(\2)shexe', script_data)

    pattern = re.compile(r'multiline_shexe.*?shexe', re.DOTALL)

    new_script_data = script_data
    for match in pattern.finditer(script_data):
        original_str = script_data[match.start():match.end()]
        processed_str = re.sub(r'([\r\n]{1,2})', r'; \\\1', original_str)

        new_script_data = new_script_data.replace(
            original_str, processed_str)

    return new_script_data


def _process_long_lines(script_data):
    """Converts to python a pyshell expression that takes more than one line. An example would be:
    f = `echo The string \
        on several \
        lines

    :param script_data: the string of the whole script
    :return: the shellpy script converted to intermediate form
    """
    code_long_line_pattern = re.compile(r'([a-z]*)`(((.*?\\\s*?$)[\n\r]{1,2})+(.*$))', re.MULTILINE)
    new_script_data = code_long_line_pattern.sub(r'longline_shexe(\2)shexe(\1)shexe', script_data)
    return new_script_data


def _process_code_both(script_data):
    """Converts to python a pyshell script that has ` symbol both in the beginning of expression and in the end.
    An example would be:
    f = `echo 1`

    :param script_data: the string of the whole script
    :return: the shellpy script converted to intermediate form
    """
    code_both_pattern = re.compile(r'([a-z]*)`(.*?)`')
    new_script_data = code_both_pattern.sub(r'both_shexe(\2)shexe(\1)shexe', script_data)
    return new_script_data


def _process_code_start(script_data):
    """Converts to python a pyshell script that has ` symbol only in the beginning. An example would be:
    f = `echo 1

    :param script_data: the string of the whole script
    :return: the shellpy script converted to intermediate form
    """
    code_start_pattern = re.compile(r'^([^\n\r`]*?)([a-z]*)`([^`\n\r]+)$', re.MULTILINE)
    new_script_data = code_start_pattern.sub(r'\1start_shexe(\3)shexe(\2)shexe', script_data)
    return new_script_data


def _escape(script_data):
    """Escapes shell commands

    :param script_data: the string of the whole script
    :return: escaped script
    """
    pattern = re.compile(r'[a-z]*_shexe.*?shexe', re.DOTALL)

    new_script_data = script_data
    for match in pattern.finditer(script_data):
        original_str = script_data[match.start():match.end()]
        if original_str.find('\'') != -1:
            processed_str = original_str.replace('\'', '\\\'')

            new_script_data = new_script_data.replace(
                original_str, processed_str)

    return new_script_data


def _intermediate_to_final(script_data):
    """All shell blocks are first compiled to intermediate form. This part of code converts the intermediate
    to final python code

    :param script_data: the string of the whole script
    :return: python script ready to be executed
    """
    intermediate_pattern = re.compile(r'[a-z]*_shexe\((.*?)\)shexe\((.*?)\)shexe', re.MULTILINE | re.DOTALL)
    final_script = intermediate_pattern.sub(r"exe('\1'.format(**dict(locals(), **globals())),'\2')", script_data)
    return final_script


def _add_encoding_to_header(header_data, script_data):
    """PEP-0263 defines a way to specify python file encoding. If this encoding is present in first
    two lines of a shellpy script it will then be moved to the top generated output file

    :param script_data: the string of the whole script
    :return: the script with the encoding moved to top, if it's present
    """
    encoding_pattern = re.compile(r'^(#[-*\s]*coding[:=]\s*([-\w.]+)[-*\s]*)$')

    # we use \n here instead of os.linesep since \n is universal as it is present in all OSes
    # when \r\n returned by os.linesep may not work if you run against unix files from win
    first_two_lines = script_data.split('\n')[:2]
    for line in first_two_lines:
        encoding = encoding_pattern.search(line)
        if encoding is not None:
            break

    if not encoding:
        return header_data
    else:
        new_header_data = header_data.replace(shellpy_encoding_pattern, encoding.group(1))
        return new_header_data
