#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from setuptools.command.easy_install import easy_install as easy_install

setup(
    name="python-humio",
    version="0.0.9",
    description="Pyhton Humio adapter.",
    long_description=open("README.md", 'r').read(),
    author="Sergey Grigorev",
    author_email="xors.nn@gmail.com",
    url="http://humio.com/",

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        'requests>=2,<3',
    ],
    classifiers=[
        'Environment :: Any',
        'Framework :: Any',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],

    cmdclass={
        'easy_install': easy_install
    }
)
