#!/usr/bin/env python
import os
from sys import stdin, stdout

print 'Enter your name'
stdout.flush()
userinput = stdin.readline()

print 'Hello ' + userinput.rstrip(os.linesep)
