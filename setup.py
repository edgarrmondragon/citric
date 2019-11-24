#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests>=2.22.0',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest>=5',
    'requests-mock>=1.7.0',
]

setup(
    author="Edgar Ramírez Mondragón",
    author_email='edgarrm358@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description=("A client to the LimeSurvey Remote Control API 2, written in "
                 "modern Python."),
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='limette',
    name='limette',
    packages=find_packages(include=['limette', 'limette.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mrfunnyshoes/limette',
    version='1.0.2',
    zip_safe=False,
)
