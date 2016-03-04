import pickle
import base64
import sys

# prints all commands being executed
PRINT_ALL_COMMANDS = False

# prints stdout of every command executed
PRINT_STDOUT_ALWAYS = False

# prints stderr of every command executed
PRINT_STDERR_ALWAYS = False

# every error (returncode != 0) in executed commands will make the script stop
EXIT_ON_ERROR = False

# colorama is a plugin that makes output colored, this flag controls whether it is enabled
COLORAMA_ENABLED = True


def dumps():
    config_tuple = (PRINT_ALL_COMMANDS, PRINT_STDOUT_ALWAYS, PRINT_STDERR_ALWAYS, EXIT_ON_ERROR, COLORAMA_ENABLED)
    serialized_config = pickle.dumps(config_tuple)

    if sys.version_info[0] == 2:
        return base64.b64encode(serialized_config)
    else:
        return str(base64.b64encode(serialized_config), 'utf-8')


def loads(data):
    global PRINT_ALL_COMMANDS, PRINT_STDOUT_ALWAYS, PRINT_STDERR_ALWAYS, EXIT_ON_ERROR, COLORAMA_ENABLED

    if sys.version_info[0] == 2:
        serialized_config = base64.b64decode(data)
    else:
        serialized_config = base64.b64decode(bytes(data, 'utf-8'))

    config_tuple = pickle.loads(serialized_config)

    PRINT_ALL_COMMANDS, PRINT_STDOUT_ALWAYS, PRINT_STDERR_ALWAYS, EXIT_ON_ERROR, COLORAMA_ENABLED = config_tuple
