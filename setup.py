#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='shellpy',
      version='0.5',
      description='Python Distribution Utilities',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/shellpy/',
      download_url='https://github.com/lamerman/shellpy/0.3.2',
      keywords=['shell', 'bash', 'sh'],
      packages=['shellpython'],
      scripts=['shellpy'],
      package_data={'shellpython': ['*.tpl']},
      install_requires=['colorama']
      )
