# shellpy
A tool for convenient shell scripting in Python

[![Build Status](https://travis-ci.org/lamerman/shellpy.svg?branch=master)](https://travis-ci.org/lamerman/shellpy)
[![Join the chat at https://gitter.im/lamerman/shellpy](https://badges.gitter.im/lamerman/shellpy.svg)](https://gitter.im/lamerman/shellpy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This tool allows you to write all your shell scripts in Python in a convenient way and in many cases replace Bash/Sh. It lets you write scripts like this:
```python

"""
This script clones shellpython to temporary directory and finds the commit hash where README was created
"""

import tempfile
import os.path
from shellpython.helpers import Dir

# We will make everything in temp directory. Dir helper allows you to change current directory
# withing 'with' block
with Dir(tempfile.gettempdir()):
    if not os.path.exists('shellpy'):
        # just executes shell command
        `git clone https://github.com/lamerman/shellpy.git

    # switch to newly created tempdirectory/shellpy
    with Dir('shellpy'):
        # here we capture result of shell execution. log here is an instance of Result class
        log = `git log --pretty=oneline --grep='Create'

        # shellpy allows you to iterate over lines in stdout with this syntactic sugar
        for line in log:
            if line.find('README.md'):
                hashcode = log.stdout.split(' ')[0]
                print hashcode
                exit(0)

        print 'The commit where the readme was created was not found'

exit(1)
```

As you can see, all expressions inside of grave accent ( ` ) symbol are executed in shell. And in python code you can capture result of this execution and perform action on it. 
For example:
```python
log = `git log --pretty=oneline --grep='Create'
```
This line will first execute ```git log --pretty=oneline --grep='Create'``` in shell and then assign the result to the ```log``` variable.
The result has the following properties:
- **stdout** the whole text from stdout of the executed process
- **stderr** the whole text from stderr of the executed process
- **returncode** returncode of the execution

Besides properties the result has some syntactic sugar:
- ```str(log)``` returns string of stdout
- ```if log:``` is equivalent to ```if log.returncode == 0``` that allows you to easily branch your code based on result of execution
- ```for line in log``` allows you to iterate over all lines of stdout
- ```log == '8fcedfs Create Readme'``` makes it easier to compaire output (stdout) of the process with some predefined text or the output of other command

### Ways to execute shell

As mentioned above all codeblocks inside of the grave accent ( ` ) symbol will be executed in shell. 

```result = `echo 1` ```

For simplicity it is also possible to leave the symbol only in the beginning of expression. Then the other rest of line will be considered as shell expression:

```result = `echo 1 ```

It is also possible to execute multiline expressions:

```
result = `
mkdir /tmp/music
cp *.mp3 > /tmp/music
`
```

And long line expressions:

```
result = `echo This is \
a very long line, \
very very long...
```

### How it all works

You could mention that the syntax in files is not a correct python syntax and to run it you need to start it with the ```shellpy``` script. Every script has ```.spy``` extension and being executed by ```shellpy``` it is first preprocessed to python and then the resulting python files are added to ```sys.path``` and imported. To import shellpy files the standard import hook is used described in [PEP 0302 -- New Import Hooks](https://www.python.org/dev/peps/pep-0302/)

### Integration with python

The script was designed to be easily integrated with python. Inside .spy script you can import all python libraries as in usual python and use them. There is not differences in syntax except for the one that the grave accent ( \` ) symbol is used not as ```eval``` but as shell execution, everything else is absolutelly the same.

Besides importing python modules, you can reuse and import shellpy modules/files in the very same way you do it for python. You only need to name your files with shellpython as *.spy and if you want to create a module, instead of putting ```__init__.py``` to directory, just put ```__init___.spy```

More information can be found in examples and documentation

### Installation

You can install it either with ```pip install shellpy``` or by cloning this repository and execution of ```setup.py install```. After that you will have ```shellpy``` command installed.

### Running

You can try shellpython by running examples after installation. Download this repository and run the following command in the root folder of the cloned repository:

```shellpy example/curl.spy```

```shellpy example/git.spy```

There is also so called allinone example which you can have a look at and execute like this:

```shellpy example/allinone/test.spy```

It is called all in one because it demonstrates all features available in shellpy. If you have python3 run instead:

```shellpy example/allinone/test3.spy```

### Is it reliable

Shellpython is covered with test and is tested with all major versions of python in Travis CI

### Documentation

[Wiki](https://github.com/lamerman/shellpy/wiki/A-guide-to-shell-python)
