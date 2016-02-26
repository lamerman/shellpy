#!/usr/bin/env python
import sys
import os
import subprocess
from shellpython.preprocessor import preprocess_file


def main():
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        print('Shellpy, write shell scripts in Python easily')
        print('Usage: shellpy [*.spy script] [arguments]')
        exit(0)

    filename = sys.argv[1]

    if not filename.endswith('.spy'):
        print('Error: Shellpy can only run *.spy files')
        print('Usage: shellpy [*.spy script] [arguments]')
        exit(1)

    processed_file = preprocess_file(filename, is_root_script=True)

    # include directory of the script to pythonpath
    new_env = os.environ.copy()
    new_env['PYTHONPATH'] = new_env.get("PYTHONPATH", '') + os.pathsep + os.path.split(filename)[0]

    retcode = subprocess.call(processed_file + ' ' + ' '.join(sys.argv[2:]), shell=True, env=new_env)
    exit(retcode)


if __name__ == '__main__':
    main()
