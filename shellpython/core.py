import os
import sys
import subprocess
from shellpython import config

colorama_intialized = False
colorama_available = True
try:
    import colorama
    from colorama import Fore, Style
except ImportError:
    colorama_available = False


def is_colorama_enabled():
    return colorama_available and config.COLORAMA_ENABLED


PARAM_PRINT_STDOUT = 'p'
PARAM_PRINT_STDERR = 'e'
PARAM_INTERACTIVE = 'i'


def is_param_set(params, param):
    return True if params.find(param) != -1 else False


class Stream:
    def __init__(self, file, encoding, print_out_stream=False, color=None):
        self._file = file
        self._encoding = encoding
        self._print_out_stream = print_out_stream
        self._color = color

    def __iter__(self):
        return self

    def next(self):
        return self.sreadline()

    __next__ = next

    def sreadline(self):
        line = self._file.readline()
        if sys.version_info[0] == 3:
            line = line.decode(self._encoding)

        if line == '':
            raise StopIteration
        else:
            line = line.rstrip(os.linesep)
            if self._print_out_stream:
                if self._color is None:
                    print(line)
                else:
                    print(self._color + line + Style.RESET_ALL)

            return line

    def swriteline(self, text):
        text_with_linesep = text + os.linesep
        if sys.version_info[0] == 3:
            text_with_linesep = text_with_linesep.encode(self._encoding)

        self._file.write(text_with_linesep)
        self._file.flush()


class InteractiveResult:
    """Result of a shell command execution.

    To get the result as string use str(Result)
    To get lines use the Result.lines field
    You can also iterate over lines of result like this: for line in Result:
    You can compaire two results that will mean compaire of result strings
    """
    def __init__(self, process, params):
        self._process = process
        self._params = params
        self.stdin = Stream(process.stdin, sys.stdin.encoding)

        print_stdout = is_param_set(params, PARAM_PRINT_STDOUT) or config.PRINT_STDOUT_ALWAYS
        self.stdout = Stream(process.stdout, sys.stdout.encoding, print_stdout)

        print_stderr = is_param_set(params, PARAM_PRINT_STDERR)
        color = None if not is_colorama_enabled() else Fore.RED
        self.stderr = Stream(process.stderr, sys.stderr.encoding, print_stderr, color)

    def sreadline(self):
        return self.stdout.sreadline()

    def swriteline(self, text):
        self.stdin.swriteline(text)

    @property
    def returncode(self):
        self._process.wait()
        return self._process.returncode

    def __iter__(self):
        return iter(self.stdout)

    def __bool__(self):
        return self.returncode == 0

    __nonzero__ = __bool__


class Result:
    """Result of a shell command execution.

    To get the result as string use str(Result)
    To get lines use the Result.lines field
    You can also iterate over lines of result like this: for line in Result:
    You can compaire two results that will mean compaire of result strings
    """
    def __init__(self):
        self.stdout_lines = []
        self.stderr_lines = []
        self.returncode = None

    def stdout_text(self):
        return os.linesep.join(self.stdout_lines)

    def stderr_text(self):
        return os.linesep.join(self.stderr_lines)

    def _add_stdout_line(self, line):
        line = line.rstrip(os.linesep)
        self.stdout_lines.append(line)

    def _add_stderr_line(self, line):
        line = line.rstrip(os.linesep)
        self.stderr_lines.append(line)

    def __str__(self):
        return self.stdout_text()

    def __iter__(self):
        return iter(self.stdout_lines)

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __bool__(self):
        return self.returncode == 0

    __nonzero__ = __bool__


def create_result(cmd, params):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result = Result()

    for line in p.stdout.readlines():
        if sys.version_info[0] == 3:
            line = line.decode(sys.stdout.encoding)

        result._add_stdout_line(line)

    for line in p.stderr.readlines():
        if sys.version_info[0] == 3:
            line = line.decode(sys.stderr.encoding)

        result._add_stderr_line(line)

    p.wait()

    if is_param_set(params, PARAM_PRINT_STDOUT) or config.PRINT_STDOUT_ALWAYS:
        print(result.stdout_text())

    if is_param_set(params, PARAM_PRINT_STDERR):
        if is_colorama_enabled():
            print(Fore.RED + result.stderr_text() + Style.RESET_ALL)
        else:
            print(result.stderr_text())

    result.returncode = p.returncode

    if config.EXIT_ON_ERROR and p.returncode != 0:
        exit(p.returncode)

    return result


def create_interactive_result(cmd, params):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    result = InteractiveResult(p, params)

    return result


def exe(cmd, params):

    global colorama_intialized
    if is_colorama_enabled() and not colorama_intialized:
        colorama_intialized = True
        colorama.init()

    if config.PRINT_ALL_COMMANDS:
        if is_colorama_enabled():
            print(Fore.GREEN + '>>> ' + cmd + Style.RESET_ALL)
        else:
            print('>>> ' + cmd)

    if is_param_set(params, PARAM_INTERACTIVE):
        return create_interactive_result(cmd, params)
    else:
        return create_result(cmd, params)
