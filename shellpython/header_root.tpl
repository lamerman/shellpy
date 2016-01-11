#!/usr/bin/env python
import sys
from shellpython.core import exe
from shellpython.importer import PreprocessorImporter


sys.meta_path.append(PreprocessorImporter())
