#!/usr/bin/env python
import sys
import os
import re
import subprocess
import shellpython.config as config
from shellpython.preprocessor import preprocess_file
from argparse import ArgumentParser
from shellpython.constants import *


def main():
    custom_usage = '''%(prog)s [SHELLPY ARGS] file [SCRIPT ARGS]

For arguments help use:
    %(prog)s --help
    '''
    custom_epilog = '''github : github.com/lamerman/shellpy'''

    def is_shellpy_file(fil):
        if not re.match('.+\.spy$', fil):
            parser.error('Shellpy can only run *.spy files')
        return fil

    parser = ArgumentParser(description='A tool for convenient shell scripting in python',
                            usage=custom_usage, epilog=custom_epilog)
    parser.add_argument('file', help='path to spy file', type=is_shellpy_file)
    parser.add_argument('-v', '--verbose', help='increase output verbosity. Always print the command being executed',
                        action="store_true")
    parser.add_argument('-vv', help='even bigger output verbosity. All stdout and stderr of executed commands is '
                                    'printed', action="store_true")
    parser.add_argument('-t', '--throw-on-error', help='Throw NonZeroReturnCodeError on every non zero output of '
                                                       'shell commands',
                        action="store_true")
    parser.add_argument('-x', '--experimental-mode', help='Runs shellpython in experimental mode. This is what could '
                                                          'be a normal mode in the future. This mode now enables '
                                                          'the throw-on-error flag', action="store_true")

    shellpy_args, unknown_args = parser.parse_known_args()

    if shellpy_args.verbose or shellpy_args.vv:
        config.PRINT_ALL_COMMANDS = True

    if shellpy_args.vv:
        config.PRINT_STDOUT_ALWAYS = True
        config.PRINT_STDERR_ALWAYS = True

    if shellpy_args.throw_on_error or shellpy_args.experimental_mode:
        config.EXIT_ON_ERROR = True

    filename = shellpy_args.file
    filename_index = sys.argv.index(filename)
    # remove script arguments given before script name
    # comment out if want to keep them
    script_args = [x for x in unknown_args if x not in sys.argv[:filename_index]]

    processed_file = preprocess_file(filename, is_root_script=True)

    # include directory of the script to pythonpath
    new_env = os.environ.copy()
    new_env['PYTHONPATH'] = new_env.get("PYTHONPATH", '') + os.pathsep + os.path.dirname(filename)
    new_env[SHELLPY_PARAMS] = config.dumps()

    retcode = subprocess.call(processed_file + ' ' + ' '.join(script_args), shell=True, env=new_env)
    exit(retcode)


if __name__ == '__main__':
    main()
