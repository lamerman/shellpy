#!/usr/bin/env python
"""
This script shows how to use shellpython directly from python without using the shellpy command
"""

import shellpython
shellpython.init()  # installs the shellpython import hook. Call uninit() to remove the hook if no longer needed

import shared  # imports shellpy module


def main():
    print(shared.shared_func()) # call to a function from shellpy module

if __name__ == '__main__':
    main()
