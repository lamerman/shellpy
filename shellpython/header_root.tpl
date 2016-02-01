#!/usr/bin/env python3
#shellpy-meta:{meta}

import sys
from shellpython.core import exe
from shellpython.importer import PreprocessorImporter

if __name__ == '__main__':
    sys.meta_path.append(PreprocessorImporter())

