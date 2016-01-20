import os
import subprocess


class Result:
    """Result of a shell command execution.

    To get the result as string use str(Result)
    To get lines use the Result.lines field
    You can also iterate over lines of result like this: for line in Result:
    You can compaire two results that will mean compaire of result strings
    """
    def __init__(self):
        self.lines = []
        self.returncode = -1

    def add_line(self, line):
        line_no_linesep = line[:-1] if len(line) > 0 and line[-1] == os.linesep else line
        self.lines.append(line_no_linesep)

    def __str__(self):
        return os.linesep.join(self.lines)

    def __iter__(self):
        return iter(self.lines)

    def __eq__(self, other):
        return self.__str__() == other.__str__()


def exe(cmd):
    """Executes command in shell and returns Result of execution

    :param cmd: Command to execute
    :return: Result of execution
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    result = Result()

    for line in p.stdout.readlines():
        result.add_line(line)

    p.wait()

    result.returncode = p.returncode

    return result
