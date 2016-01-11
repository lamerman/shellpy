#!/usr/bin/env python
import os
import stat
import tempfile
import re
import getpass

# TODO: think about IDE. How to make generated modules visible
# TODO: remove old files from modules


code_both_pattern = re.compile("`([^`]*)`")
code_start_pattern = re.compile("`(.*)$")
spy_file_pattern = re.compile("(.*)\.spy$")


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


def preprocess_file(filepath, is_root_script):
    processed_lines = list()

    header_name = 'header_root.tpl' if is_root_script else 'header.tpl'
    header_filename = os.path.join(os.path.split(__file__)[0], header_name)

    with open(header_filename, 'r') as f:
        header_data = f.read()

    processed_lines.append(header_data)

    with open(filepath, 'r') as f:
        for line in f.readlines():
            line = code_both_pattern.sub(r"exe('\1'.format(**dict(locals(), **globals())))", line)
            line = code_start_pattern.sub(r"exe('\1'.format(**dict(locals(), **globals())))", line)
            processed_lines.append(line)

    new_filepath = spy_file_pattern.sub(r"\1.py", filepath)

    out_filename = translate_to_temp_path(new_filepath)

    if os.path.exists(out_filename):
        os.remove(out_filename)
        # TODO: maybe not remove but reuse if it's the same

    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename), mode=0700)

    with open(out_filename, 'w') as f:
        f.writelines(processed_lines)

    st = os.stat(out_filename)
    os.chmod(out_filename, st.st_mode | stat.S_IEXEC)
    # TODO: make executable only if source file is executable

    return out_filename
