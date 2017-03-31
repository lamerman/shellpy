#!/usr/bin/env python
import sys
import os
import re
import subprocess
import shellpython.config as config
from shellpython.preprocessor import preprocess_file
from argparse import ArgumentParser
from shellpython.constants import *


def main2():
    main(python_version=2)


def main3():
    main(python_version=3)


def main(python_version):
    custom_usage = '''%(prog)s [SHELLPY ARGS] file [SCRIPT ARGS]

For arguments help use:
    %(prog)s --help
    '''
    custom_epilog = '''github : github.com/lamerman/shellpy'''

    try:
        spy_file_index = next(index for index, arg in enumerate(sys.argv) if re.match('.+\.spy$', arg))
        shellpy_args = sys.argv[1:spy_file_index]
        script_args = sys.argv[spy_file_index + 1:]
    except StopIteration:
        shellpy_args = sys.argv[1:]
        spy_file_index = None

    parser = ArgumentParser(description='A tool for convenient shell scripting in python',
                            usage=custom_usage, epilog=custom_epilog)
    parser.add_argument('-v', '--verbose', help='increase output verbosity. Always print the command being executed',
                        action="store_true")
    parser.add_argument('-vv', help='even bigger output verbosity. All stdout and stderr of executed commands is '
                                    'printed', action="store_true")

    shellpy_args, _ = parser.parse_known_args(shellpy_args)

    if spy_file_index is None:
        exit('No *.spy file was specified. Only *.spy files are supported by the tool.')

    if shellpy_args.verbose or shellpy_args.vv:
        config.PRINT_ALL_COMMANDS = True

    if shellpy_args.vv:
        config.PRINT_STDOUT_ALWAYS = True
        config.PRINT_STDERR_ALWAYS = True

    filename = sys.argv[spy_file_index]

    processed_file = preprocess_file(filename, is_root_script=True, python_version=python_version)

    # include directory of the script to pythonpath
    new_env = os.environ.copy()
    new_env['PYTHONPATH'] = new_env.get("PYTHONPATH", '') + os.pathsep + os.path.dirname(filename)
    new_env[SHELLPY_PARAMS] = config.dumps()

    retcode = subprocess.call(processed_file + ' ' + ' '.join(script_args), shell=True, env=new_env)
    exit(retcode)


if __name__ == '__main__':
    main()
