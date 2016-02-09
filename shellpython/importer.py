import os
import sys
from importlib import import_module
from shellpython import locator
from shellpython import preprocessor


class PreprocessorImporter(object):
    """
    Every import of shellpy code requires first preprocessing of shellpy script into a usual python script
    and then import of it. To make it we need a hook for every import with standard python hooks.
    See PEP-0302 https://www.python.org/dev/peps/pep-0302/ for more details

    When an import occurs the find module function will be called first. It tries to find a shell python module or
    file using the Locator class. If the search is successful and there is actually shellpy module or file with
    the name specified, the find_module function will return self as Loader. If nothing is found, None will be
    returned and the import mechanism of python will not be affected in any other way.
    So if something was found then loader will preprocess file or module and import it with standard python
    import
    """

    def find_module(self, module_name, package_path):
        """This function is part of interface defined in import hooks PEP-0302
        Given the name of the module its goal is to locate it. If shellpy module with the name was found,
        self is returned as Loader for this module. Otherwise None is returned and standard python import
        works as expected

        :param module_name: the module to locate
        :param package_path: part of interface, not used, see PEP-0302
        :return: self if shellpy module was found, None if not
        """
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
        """If the module was located it then is loaded by this function. It is also a part of PEP-0302 interface
        Loading means first preprocessing of shell python code if it is not processed already and the addition
        to system path and import.

        :param module_name: the name of the module to load
        :return: the module imported. This function assumes that it will import a module anyway since find_module
        already found the module
        """
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
