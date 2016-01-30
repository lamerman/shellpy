import os
import sys
import subprocess


class Stream:
    def __init__(self, file):
        self._file = file

    def __iter__(self):
        return self

    def next(self):
        return self.sreadline()

    def sreadline(self):
        line = self._file.readline()
        if line == '':
            raise StopIteration
        else:
            return line.rstrip(os.linesep)

    def swriteline(self, text):
        self._file.write(text + os.linesep)


class InteractiveResult:
    """Result of a shell command execution.

    To get the result as string use str(Result)
    To get lines use the Result.lines field
    You can also iterate over lines of result like this: for line in Result:
    You can compaire two results that will mean compaire of result strings
    """
    def __init__(self, process):
        self._process = process
        self.stdin = Stream(process.stdin)
        self.stdout = Stream(process.stdout)
        self.stderr = Stream(process.stderr)

    def sreadline(self):
        return self.stdout.sreadline()

    def swriteline(self, text):
        self.stdin.swriteline(text)

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

    if params.find('p') != -1:
        print(result.stdout_text())

    if params.find('e') != -1:
        print(result.stderr_text())

    result.returncode = p.returncode

    return result


def create_interactive_result(cmd, params):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    result = InteractiveResult(p)

    return result


def exe(cmd, params):
    if params.find('i') != -1:
        return create_interactive_result(cmd, params)
    else:
        return create_result(cmd, params)
