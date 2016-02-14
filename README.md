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
