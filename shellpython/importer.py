import os
import sys
from importlib import import_module
from shellpython import locator
from shellpython import preprocessor


class PreprocessorImporter(object):

    def find_module(self, module_name, package_path):
        return self

    def load_module(self, module_name):
        sys.meta_path.remove(self)
        try:
            module = import_module(module_name)
        except ImportError:
            spy_module_path = locator.locate_spy_module(module_name)
            if spy_module_path is not None:
                new_module_path = preprocessor.preprocess_module(spy_module_path)
                new_module_pythonpath = os.path.split(new_module_path)[0]
                if new_module_pythonpath not in sys.path:
                    sys.path.append(new_module_pythonpath)

                module = import_module(module_name)
            else:
                raise

        sys.meta_path.append(self)

        return module
