import os
import sys
import subprocess


PARAM_PRINT_STDOUT = 'p'
PARAM_PRINT_STDERR = 'e'
PARAM_INTERACTIVE = 'i'


def is_param_set(params, param):
    return True if params.find(param) != -1 else False


class Stream:
    def __init__(self, file, encoding, print_out_stream = False):
        self._file = file
        self._encoding = encoding
        self._printOutStream = print_out_stream

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
            if self._printOutStream:
                print(line)

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

        print_stdout = is_param_set(params, PARAM_PRINT_STDOUT)
        self.stdout = Stream(process.stdout, sys.stdout.encoding, print_stdout)

        print_stderr = is_param_set(params, PARAM_PRINT_STDERR)
        self.stderr = Stream(process.stderr, sys.stderr.encoding, print_stderr)

    def sreadline(self):
        return self.stdout.sreadline()

    def swriteline(self, text):
        self.stdin.swriteline(text)

    @property
    def returncode(self):
        self._process.wait()
        return self._process.returncode

    def __str__(self):
        return 'TODO'

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

    def add_stdout_line(self, line):
        line = line.rstrip(os.linesep)
        self.stdout_lines.append(line)

    def add_stderr_line(self, line):
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

        result.add_stdout_line(line)

    for line in p.stderr.readlines():
        if sys.version_info[0] == 3:
            line = line.decode(sys.stderr.encoding)

        result.add_stderr_line(line)

    p.wait()

    if is_param_set(params, PARAM_PRINT_STDOUT):
        print(result.stdout_text())

    if is_param_set(params, PARAM_PRINT_STDERR):
        print(result.stderr_text())

    result.returncode = p.returncode

    return result


def create_interactive_result(cmd, params):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    result = InteractiveResult(p, params)

    return result


def exe(cmd, params):
    if is_param_set(params, PARAM_INTERACTIVE):
        return create_interactive_result(cmd, params)
    else:
        return create_result(cmd, params)
