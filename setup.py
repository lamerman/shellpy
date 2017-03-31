#!/usr/bin/env python

try:
    from setuptools import setup

    args_for_setup = {'entry_points': {
        'console_scripts': {
            'shellpy = shellpython.shellpy:main2',
            'shellpy2 = shellpython.shellpy:main2',
            'shellpy3 = shellpython.shellpy:main3'
        }
    }}

except ImportError:
    from distutils.core import setup

    args_for_setup = {'scripts': ['shellpy']}


setup(name='shellpy',
      version='0.5.1',
      description='A convenient tool for shell scripting in python',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/shellpy/',
      download_url='https://github.com/lamerman/shellpy/tarball/0.5.1',
      keywords=['shell', 'bash', 'sh'],
      packages=['shellpython'],
      package_data={'shellpython': ['*.tpl']},
      install_requires=['colorama'],
      tests_require=['mock'],
      **args_for_setup
      )
