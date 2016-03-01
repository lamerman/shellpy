#!/usr/bin/env python
import sys
import os
import subprocess
from shellpython.preprocessor import preprocess_file
from argparse import ArgumentParser
import re


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
    shellpy_args, unknown_args = parser.parse_known_args()

    filename = shellpy_args.file
    filename_index = sys.argv.index(filename)
    # remove script arguments given before script name
    # comment out if want to keep them
    script_args = [x for x in unknown_args if x not in sys.argv[:filename_index]]

    processed_file = preprocess_file(filename, is_root_script=True)

    # include directory of the script to pythonpath
    new_env = os.environ.copy()
    new_env['PYTHONPATH'] = new_env.get("PYTHONPATH", '') + os.pathsep + os.path.dirname(filename)

    retcode = subprocess.call(processed_file + ' ' + ' '.join(script_args), shell=True, env=new_env)
    exit(retcode)


if __name__ == '__main__':
    main()
