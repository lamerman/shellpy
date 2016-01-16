# shellpy
A tool for convenient shell scripting in Python

This tool allows you to write all your shell scripts in Python in a convenient way and forget about Bash/Sh. It lets you write scripts like this:
```python
import os
from common.code import common_func

for line in `ls -l | grep shell`:
    print `echo LINE IS: {line}

s = `ls -l | grep non_existent_string
if s.returncode == 0:
    print 'string found'
else:
    print 'string not found'

print common_func()
```

Use available python and libraries as usual:
```python
import os
```

Easily execute shell in your python code:
```python
s = `ls -l | grep non_existent_string
```

Or multiline (now in development)
```python
`
cp my.txt /tmp
ls -l /tmp
`
```

Iterate over ouput lines:
```python
for line in `ls -l | grep shell`:
```

Print output of shell commands:
```python
print `echo LINE IS: {line}
```

Capture return code:
```python
s = `ls -l | grep non_existent_string
if s.returncode == 0:
  ...
```

Reuse code written in shellpy in the very same way you reuse usual python code. You are free to create modules and files and import them as you normally import in Python
```python
from common.code import common_func
```
where ```common``` is a module in shellpy and code is ```code.spy``` file in that module with this content:
```python
def common_func():
    return `echo 5
```
