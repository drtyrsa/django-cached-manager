#!/usr/bin/env python
# -*- coding:utf-8 -*-
from distutils.core import setup


setup(
    name = 'django-cached-manager',
    version = '0.1.0',
    license = 'BSD',
    description = 'Django models manager that encapsulates some common caching operations',
    long_description = open('README.rst').read(),
    author = 'Vlad Starostin',
    author_email = 'drtyrsa@yandex.ru',
    packages = ['cached_manager',
                'cached_manager.tests',
                'cached_manager.tests.utils'],
    classifiers = [
        'Development Status :: 1 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)