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
        if module_name.find('.') == -1:
            root_module_name = module_name
        else:
            root_module_name = module_name.split('.')[0]

        spy_module_path = locator.locate_spy_module(root_module_name)
        spy_file_path = locator.locate_spy_file(root_module_name)

        if spy_module_path is not None or spy_file_path is not None:
            return self
        else:
            return None

    def load_module(self, module_name):
        sys.meta_path.remove(self)

        if module_name.find('.') == -1:
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
                raise ImportError("Unexpected error occured in importer. Neither shellpy module not file was found")

        else:
            module = import_module(module_name)

        sys.meta_path.insert(0, self)

        return module
