#!/usr/bin/env python
#{SOURCE_MODIFICATION_DATE}

import sys
from shellpython.core import exe
from shellpython.importer import PreprocessorImporter

if __name__ == '__main__':
    sys.meta_path.append(PreprocessorImporter())

