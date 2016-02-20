#!/usr/bin/env python
import os
import time
from sys import stdin, stdout

print('Enter your name')
stdout.flush()
userinput = stdin.readline()

time.sleep(1)

print('Hello ' + userinput.rstrip(os.linesep))
print('End')
