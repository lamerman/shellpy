#!/usr/bin/env python

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

scriptName = 'shellpy'
if os.name == 'nt':
    scriptName = 'shellpy.py'

setup(name='shellpy',
      version='0.4.0',
      description='A convenient tool for shell scripting in python',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/shellpy/',
      download_url='https://github.com/lamerman/shellpy/tarball/0.4.0',
      keywords=['shell', 'bash', 'sh'],
      packages=['shellpython'],
      scripts=[scriptName],
      package_data={'shellpython': ['*.tpl']},
      install_requires=['colorama']
      )
