#!/usr/bin/env python

from setuptools import setup

setup(
    name='nsbuild',
    packages=['nsbuild'],
    version='0.1.0',
    description='nsbuild',
    license='MIT',
    url='https://github.com/NeverScape/neverscape-auto-build',
    author='Austin Jackson',
    author_email='vesche@protonmail.com',
    entry_points={
        'console_scripts': [
            'nsbuild = nsbuild:main',
        ]
    },
    install_requires=['paramiko']
)