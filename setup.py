#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from setuptools.command.easy_install import easy_install as base_easy_install


class easy_install(base_easy_install):
    """
    Private repo handler
    """

    def finalize_options(self):
        auth = os.getenv("CHEESESHOP_AUTH", '')
        if auth and not auth.endswith('@'):
            auth += '@'

        self.index_url = "http://{}lugati.eu:8083/simple".format(auth)
        self.no_find_links = True

        base_easy_install.finalize_options(self)


setup(
    name="python-humio",
    version="0.0.1",
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
