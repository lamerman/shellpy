#shellpy-python-executable
#shellpy-encoding
#shellpy-meta:{meta}

import os
import shellpython
import shellpython.config
from shellpython.constants import *
from shellpython.core import exe, NonZeroReturnCodeError, _print_stderr as shellpy_print_stderr

if __name__ == '__main__':
    shellpython.init()

    if SHELLPY_PARAMS in os.environ:
        try:
            shellpython.config.loads(os.environ[SHELLPY_PARAMS])
        except Exception as e:
            shellpy_print_stderr('Could not load shellpy config: ' + str(e))
