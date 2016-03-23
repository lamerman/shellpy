from __future__ import print_function
import os
import sys
import subprocess
from os import environ as env
from shellpython import config

_colorama_intialized = False
_colorama_available = True
try:
    import colorama
    from colorama import Fore, Style
except ImportError:
    _colorama_available = False


def _is_colorama_enabled():
    return _colorama_available and config.COLORAMA_ENABLED


def _print_stdout(text):
    print(text)


def _print_stderr(text):
    print(text, file=sys.stderr)

# print all stdout of executed command
_PARAM_PRINT_STDOUT = 'p'

# print all stderr of executed command
_PARAM_PRINT_STDERR = 'e'

# runs command in interactive mode when user can read output line by line and send to stdin
_PARAM_INTERACTIVE = 'i'

# no throw mode. With this parameter user explicitly says that NonZeroReturnCodeError must not be thrown for this
# specific command. It may be useful if for some reason this command does not return 0 even for successful run
_PARAM_NO_THROW = 'n'


def exe(cmd, params):
    """This function runs after preprocessing of code. It actually executes commands with subprocess

    :param cmd: command to be executed with subprocess
    :param params: parameters passed before ` character, i.e. p`echo 1 which means print result of execution
    :return: result of execution. It may be either Result or InteractiveResult
    """

    global _colorama_intialized
    if _is_colorama_enabled() and not _colorama_intialized:
        _colorama_intialized = True
        colorama.init()

    if config.PRINT_ALL_COMMANDS:
        if _is_colorama_enabled():
            _print_stdout(Fore.GREEN + '>>> ' + cmd + Style.RESET_ALL)
        else:
            _print_stdout('>>> ' + cmd)

    if _is_param_set(params, _PARAM_INTERACTIVE):
        return _create_interactive_result(cmd, params)
    else:
        return _create_result(cmd, params)


def _is_param_set(params, param):
    return True if params.find(param) != -1 else False


class ShellpyError(Exception):
    """Base error for shell python
    """
    pass


class NonZeroReturnCodeError(ShellpyError):
    """This is thrown when the executed command does not return 0
    """
    def __init__(self, cmd, result):
        self.cmd = cmd
        self.result = result

    def __str__(self):
        if _is_colorama_enabled():
            return 'Command {red}\'{cmd}\'{end} failed with error code {code}, stderr output is {red}{stderr}{end}'\
                .format(red=Fore.RED, end=Style.RESET_ALL, cmd=self.cmd, code=self.result.returncode,
                        stderr=self.result.stderr)
        else:
            return 'Command \'{cmd}\' failed with error code {code}, stderr output is {stderr}'.format(
                    cmd=self.cmd, code=self.result.returncode, stderr=self.result.stderr)


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
                    _print_stdout(line)
                else:
                    _print_stdout(self._color + line + Style.RESET_ALL)

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

        print_stdout = _is_param_set(params, _PARAM_PRINT_STDOUT) or config.PRINT_STDOUT_ALWAYS
        self.stdout = Stream(process.stdout, sys.stdout.encoding, print_stdout)

        print_stderr = _is_param_set(params, _PARAM_PRINT_STDERR) or config.PRINT_STDERR_ALWAYS
        color = None if not _is_colorama_enabled() else Fore.RED
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

    To get the result stdout as string use str(Result) or Result.stdout or print Result
    To get output of stderr use Result.stderr()

    You can also iterate over lines of stdout like this: for line in Result:

    You can access underlying lines of result streams as Result.stdout_lines Result.stderr_lines.
    E.g. line_two = Result.stdout_lines[2]

    You can also compaire two results that will mean compaire of result stdouts
    """
    def __init__(self):
        self._stdout_lines = []
        self._stderr_lines = []
        self.returncode = None

    @property
    def stdout(self):
        """Stdout of Result as text
        """
        return os.linesep.join(self._stdout_lines)

    @property
    def stderr(self):
        """Stderr of Result as text
        """
        return os.linesep.join(self._stderr_lines)

    @property
    def stdout_lines(self):
        """List of all lines from stdout
        """
        return self._stdout_lines

    @property
    def stderr_lines(self):
        """List of all lines from stderr
        """
        return self._stderr_lines

    def _add_stdout_line(self, line):
        line = line.rstrip(os.linesep)
        self._stdout_lines.append(line)

    def _add_stderr_line(self, line):
        line = line.rstrip(os.linesep)
        self._stderr_lines.append(line)

    def __str__(self):
        return self.stdout

    def __iter__(self):
        return iter(self._stdout_lines)

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __bool__(self):
        return self.returncode == 0

    __nonzero__ = __bool__


def _create_result(cmd, params):
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=os.environ)

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

    if (_is_param_set(params, _PARAM_PRINT_STDOUT) or config.PRINT_STDOUT_ALWAYS) and len(result.stdout) > 0:
        _print_stdout(result.stdout)

    if (_is_param_set(params, _PARAM_PRINT_STDERR) or config.PRINT_STDERR_ALWAYS) and len(result.stderr) > 0:
        if _is_colorama_enabled():
            _print_stderr(Fore.RED + result.stderr + Style.RESET_ALL)
        else:
            _print_stderr(result.stderr)

    result.returncode = p.returncode

    if p.returncode != 0 and not _is_param_set(params, _PARAM_NO_THROW):
        raise NonZeroReturnCodeError(cmd, result)

    return result


def _create_interactive_result(cmd, params):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    result = InteractiveResult(p, params)

    return result
