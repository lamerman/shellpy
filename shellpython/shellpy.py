#!/usr/bin/env python
import sys
import os
import subprocess
from shellpython.preprocessor import preprocess_file
from argparse import ArgumentParser
import re


def main():
    def shellpyFile(fil):
        if not re.match('.+\.spy$', fil):
            parser.error('Shellpy can only run *.spy files')
        return fil

    parser = ArgumentParser(description='Shellpy, write shell scripts in Python easily',
            usage='%(prog)s [SHELLPY ARGS] shellpy_script.spy [SCRIPT ARGS]')
    parser.add_argument('file', help='path to spy file', type = shellpyFile)
    shellpy_args, unknown_args = parser.parse_known_args()

    filename = shellpy_args.file
    i = sys.argv.index(filename)
    #remove script arguments given before script name
    #comment out if want to keep them
    script_args = [ x for x in unknown_args if x not in sys.argv[:i]]

    processed_file = preprocess_file(filename, is_root_script=True)

    # include directory of the script to pythonpath
    new_env = os.environ.copy()
    new_env['PYTHONPATH'] = new_env.get("PYTHONPATH", '') + os.pathsep + os.path.split(filename)[0]

    retcode = subprocess.call(processed_file + ' ' + ' '.join(script_args), shell=True, env=new_env)
    exit(retcode)


if __name__ == '__main__':
    main()
