#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='shellpy',
      version='0.3.4',
      description='A convenient tool for shell scripting in python',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/shellpy/',
      download_url='https://github.com/lamerman/shellpy/tarball/0.3.4',
      keywords=['shell', 'bash', 'sh'],
      packages=['shellpython'],
      scripts=['shellpy'],
      package_data={'shellpython': ['*.tpl']},
      install_requires=['colorama']
      )
