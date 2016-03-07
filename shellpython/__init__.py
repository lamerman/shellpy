import sys
from shellpython.importer import PreprocessorImporter

_importer = PreprocessorImporter()


def init():
    """Initialize shellpython by installing the import hook
    """
    if _importer not in sys.meta_path:
        sys.meta_path.insert(0, _importer)


def uninit():
    """Uninitialize shellpython by removing the import hook
    """
    sys.meta_path.remove(_importer)
