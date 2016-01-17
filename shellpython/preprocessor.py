#!/usr/bin/env python
import os
import stat
import tempfile
import re
import getpass

# TODO: think about IDE. How to make generated modules visible
# TODO: remove old files from modules
# TODO: what if user specifies his own interpreter in the first line


code_both_pattern = re.compile("`([^`]*)`")
code_start_pattern = re.compile("`(.*)$")
spy_file_pattern = re.compile("(.*)\.spy$")
mod_time_pattern = re.compile('#mtime:(.*)')


def get_username():
    return getpass.getuser()
    # TODO: what if function does not work
    # TODO: see whether getpass is available everywhere


def preprocess_module(module_path):
    for item in os.walk(module_path):
        path, dirs, files = item
        for file in files:
            if spy_file_pattern.match(file):
                filepath = os.path.join(path, file)
                preprocess_file(filepath, is_root_script=False)

    return translate_to_temp_path(module_path)


def translate_to_temp_path(path):
    absolute_path = os.path.abspath(path)
    relative_path = os.path.relpath(absolute_path, os.path.abspath(os.sep))
    # TODO: this will not work in win where root is C:\ and absolute_in_path is on D:\
    translated_path = os.path.join(tempfile.gettempdir(), 'shellpy', get_username(), relative_path)
    return translated_path


def is_compilation_needed(in_filepath, out_filepath):
    if not os.path.exists(out_filepath):
        return True

    in_mtime = os.path.getmtime(in_filepath)

    with open(out_filepath, 'r') as f:
        firstline = f.readline().strip()
        first_line_result = mod_time_pattern.search(firstline)
        if first_line_result:
            mtime = first_line_result.group(1)
            if str(in_mtime) == mtime:
                return False
        else:
            secondline = f.readline().strip()
            second_line_result = mod_time_pattern.search(secondline)
            if second_line_result:
                mtime = second_line_result.group(1)
                if str(in_mtime) == mtime:
                    return False
            else:
                raise RuntimeError("Either first or second line of file should contain source timestamp")

    return True


def get_header(filepath, is_root_script):
    header_name = 'header_root.tpl' if is_root_script else 'header.tpl'
    header_filename = os.path.join(os.path.split(__file__)[0], header_name)

    with open(header_filename, 'r') as f:
        header_data = f.read()
        mod_time = os.path.getmtime(filepath)
        header_data = header_data.replace('{SOURCE_MODIFICATION_DATE}', 'mtime:{}'.format(mod_time))
        return header_data


def preprocess_file(in_filepath, is_root_script):
    new_filepath = spy_file_pattern.sub(r"\1.py", in_filepath)
    out_filename = translate_to_temp_path(new_filepath)

    if not is_root_script and not is_compilation_needed(in_filepath, out_filename):
        # TODO: cache root also
        # TODO: if you don't compile but it's root, you need to change to exec
        return out_filename

    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename), mode=0700)

    processed_lines = list()

    header_data = get_header(in_filepath, is_root_script)
    processed_lines.append(header_data)

    with open(in_filepath, 'r') as f:
        for line in f.readlines():
            line = code_both_pattern.sub(r"exe('\1'.format(**dict(locals(), **globals())))", line)
            line = code_start_pattern.sub(r"exe('\1'.format(**dict(locals(), **globals())))", line)
            processed_lines.append(line)
            # TODO: possibly we may remove globals and locals where vars are not used

    with open(out_filename, 'w') as f:
        f.writelines(processed_lines)

    in_file_stat = os.stat(in_filepath)
    os.chmod(out_filename, in_file_stat.st_mode)

    if is_root_script:
        os.chmod(out_filename, in_file_stat.st_mode | stat.S_IEXEC)

    return out_filename
