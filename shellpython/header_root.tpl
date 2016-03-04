#!/usr/bin/env python
#shellpy-meta:{meta}

import sys
import os
import shellpython.config
from shellpython.constants import *
from shellpython.core import exe, _print_stderr as shellpy_print_stderr
from shellpython.importer import PreprocessorImporter

if __name__ == '__main__':
    sys.meta_path.insert(0, PreprocessorImporter())

    if SHELLPY_PARAMS in os.environ:
        try:
            shellpython.config.loads(os.environ[SHELLPY_PARAMS])
        except Exception as e:
            shellpy_print_stderr('Could not load shellpy config: ' + str(e))
