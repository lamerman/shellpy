#!/usr/bin/env python
#shellpy-meta:{meta}

import sys
from shellpython.core import exe
from shellpython.importer import PreprocessorImporter

if __name__ == '__main__':
    sys.meta_path.insert(0, PreprocessorImporter())

