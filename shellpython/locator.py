import sys
import os.path


def locate_spy_module(module_name):
    """Tries to find shellpy module on filesystem. Given a module name it tries to locate it in pythonpath. It looks
    for a module with the same name and __init__.spy inside of it

    :param module_name: Filename without extension
    :return: Path to shellpy file or None if not found
    """
    for python_path in sys.path:

        possible_module_path = os.path.join(python_path, module_name)
        if os.path.exists(possible_module_path):
            if os.path.exists(os.path.join(possible_module_path, '__init__.spy')):
                return possible_module_path

    return None


def locate_spy_file(file_name):
    """Tries to find shellpy file on filesystem. Given a filename without extension it tries to locate it with .spy
    extension in pythonpath

    :param file_name: Filename without extension
    :return: Path to shellpy file or None if not found
    """
    for python_path in sys.path:

        possible_file_path = os.path.join(python_path, file_name + '.spy')
        if os.path.exists(possible_file_path):
            return possible_file_path

    return None
