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
            spy_file_path = locator.locate_spy_file(module_name)

            if spy_module_path is not None:
                new_file_path = preprocessor.preprocess_module(spy_module_path)
                new_file_pythonpath = os.path.split(new_file_path)[0]

                if new_file_pythonpath not in sys.path:
                    sys.path.append(new_file_pythonpath)

                module = import_module(module_name)

            elif spy_file_path is not None:
                new_file_path = preprocessor.preprocess_file(spy_file_path, is_root_script=False)
                new_file_pythonpath = os.path.split(new_file_path)[0]

                if new_file_pythonpath not in sys.path:
                    sys.path.append(new_file_pythonpath)

                module = import_module(module_name)

            else:
                raise

        sys.meta_path.append(self)

        return module
