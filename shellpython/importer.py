import os
import sys
from importlib import import_module
from shellpython import locator
from shellpython import preprocessor


class PreprocessorImporter(object):
    """
    Every import of shellpy code requires first preprocessing of shellpy script into a usual python script
    and then import of it. To make it we need a hook for every import.
    When an import is required it first tries to import a module normally. In case an error arises it then tries
    to locate a shellpy module with the same name and preprocess it. After preprocessing the module is added to
    pythonpath and then imported
    """

    def find_module(self, module_name, package_path):
        return self

    def load_module(self, module_name):
        sys.meta_path.remove(self)

        spy_module_path = locator.locate_spy_module(module_name)
        spy_file_path = locator.locate_spy_file(module_name)

        if spy_module_path is not None:
            new_module_path = preprocessor.preprocess_module(spy_module_path)
            new_module_pythonpath = os.path.split(new_module_path)[0]

            if new_module_pythonpath not in sys.path:
                sys.path.append(new_module_pythonpath)

            module = import_module(module_name)

        elif spy_file_path is not None:
            new_module_path = preprocessor.preprocess_file(spy_file_path, is_root_script=False)
            new_module_pythonpath = os.path.split(new_module_path)[0]

            if new_module_pythonpath not in sys.path:
                sys.path.append(new_module_pythonpath)

            module = import_module(module_name)

        else:
            module = import_module(module_name)

        sys.meta_path.append(self)

        return module
