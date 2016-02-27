# shellpy
A tool for convenient shell scripting in Python. It allows you to write all your shell scripts in Python in a convenient way and in many cases replace Bash/Sh. 

[![Build Status](https://travis-ci.org/lamerman/shellpy.svg?branch=master)](https://travis-ci.org/lamerman/shellpy)
[![Join the chat at https://gitter.im/lamerman/shellpy](https://badges.gitter.im/lamerman/shellpy.svg)](https://gitter.im/lamerman/shellpy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![PyPI Wheel](http://badge.kloud51.com/pypi/w/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Status](http://badge.kloud51.com/pypi/s/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI License](http://badge.kloud51.com/pypi/l/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Format](http://badge.kloud51.com/pypi/f/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Py_versions](http://badge.kloud51.com/pypi/p/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Downloads](http://badge.kloud51.com/pypi/d/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Implementation](http://badge.kloud51.com/pypi/i/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Version](http://badge.kloud51.com/pypi/v/shellpy.svg)](https://pypi.python.org/pypi/shellpy)
[![PyPI Egg](http://badge.kloud51.com/pypi/e/shellpy.svg)](https://pypi.python.org/pypi/shellpy)

## Preface - Why do we need shell python?

For many people bash/sh seem to be pretty complicated. An example would be regular expressions, working with json/yaml/xml, named arguments parsing and so on. There are many things that are much easier in python to understand and work with.

## Introduction

Shell python has no differences from python except for one. Grave accent symbol (`) does not mean eval, it means execution of shell commands. So

    `ls -l`

will execute `ls -l` in shell. You can also skip one ` in the end of line

    `ls -l

and it will also be a correct syntax. It is also possible to write multiline expressions

    `
    echo test > test.txt
    cat test.txt
    `

and long lines

    `echo This is \
      a very long \
      line

Every shellpy exression returns a Result

    result = `ls -l

It can be either [Result](https://github.com/lamerman/shellpy/wiki/Simple-mode#result) or [InteractiveResult](https://github.com/lamerman/shellpy/wiki/Interactive-mode#interactive-result). Let's start with a simple Result. First you can check returncode of a command

    result = `ls -l
    print result.returncode

You can also get text from stdout or stderr

    result = `ls -l
    result_text = result.stdout
    result_error = result.stderr

You can iterate over lines of result stdout

    result = `ls -l
    for line in result:
        print line.upper()

and so on. 

It also has syntactic sugar for some operations like checking result for zero

    result = `ls -l
    if result:
        print 'Return code for ls -l was 0'

Or getting stdout

    result = `ls -l
    print result

## Integration with python and code reuse

As it was said before shellpython does not differ a lot from ordinary python. You can import python modules and use them as usual

    import os.path
    
    `mkdir /tmp/mydir
    os.path.exists('/tmp/mydir') # True

And you can do the same with shellpython modules. Suppose you have shellpy module `common` as in examples directory. So this is how it looks

    ls common/
    common.spy  __init__.spy

So you have directory `common` and two files inside: `__init__.spy` and `common.spy`. Looks like a python module right? Exactly. The only difference is file extension. For `__init__.spy` and other files it must be `.spy`. Let's look inside `common.spy`

    def common_func():
        return `echo 5

A simple function that returns [Result](https://github.com/lamerman/shellpy/wiki/Simple-mode#result) of `echo 5` execution. How is it used how in code? As same as in python

    from common.common import common_func
    
    print('Result of imported function is ' + str(common_func()))

Note that the `common` directory must be in pythonpath to be imported.

### How does import work?

It uses import hooks described in [PEP 0302 -- New Import Hooks](https://www.python.org/dev/peps/pep-0302/). So, whenever importer finds a shellpy module or a file with .spy extension and with the name that you import, it will try to first preprocess it from shellpy to python and then import it using standard python import. Once preprocessed, the file is cached in your system temp directory and the second time it will be just imported directly.

### Example

This script clones shellpython to temporary directory and finds the commit hash where README was created

```python

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

Two lines here are executed in shell ```git clone https://github.com/lamerman/shellpy.git``` and ```git log --pretty=oneline --grep='Create'```. The result of the second line is assigned to variable ```log``` and then we iterate over the result line by line in the for cycle

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

### Documentation

[Wiki](https://github.com/lamerman/shellpy/wiki)

### Compatibility

It works on Linux and Mac for both Python 2.x and 3.x. It should also work on Windows.

### Contact

Please contact me in gitter 
[![Join the chat at https://gitter.im/lamerman/shellpy](https://badges.gitter.im/lamerman/shellpy.svg)](https://gitter.im/lamerman/shellpy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) 
if you want to share your thoughts about the project or tell about possible improvements.
