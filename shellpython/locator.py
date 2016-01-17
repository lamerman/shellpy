import sys
import os.path


def locate_spy_module(module_name):
    for python_path in sys.path:

        possible_module_path = os.path.join(python_path, module_name)
        if os.path.exists(possible_module_path):
            if os.path.exists(os.path.join(possible_module_path, '__init__.spy')):
                return possible_module_path

    return None


def locate_spy_file(module_name):
    for python_path in sys.path:

        possible_file_path = os.path.join(python_path, module_name + '.spy')
        if os.path.exists(possible_file_path):
            return possible_file_path

    return None
