import os


class Dir:
    """This class allows to execute commands in directories different from current like this

    with Dir('tmp'):
        `ls -l
    """

    def __init__(self, directory):
        self.current_dir = directory

    def __enter__(self):
        self.previous_dir = os.getcwd()
        os.chdir(self.current_dir)

    def __exit__(self, type, value, traceback):
        os.chdir(self.previous_dir)
