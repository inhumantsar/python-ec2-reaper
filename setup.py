#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('VERSION') as version_file:
    version = version_file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup_requirements = [
    'pytest-runner',
    # TODO(inhumantsar): put setup requirements (distutils extensions, etc.) here
]

with open('requirements_dev.txt') as f:
    requirements_dev = f.read().splitlines()


setup(
    name='ec2-reaper',
    version=version,
    description="CLI & module for terminating instances that match tag and age requirements.",
    long_description=readme + '\n\n' + history,
    author="Shaun Martin",
    author_email='shaun@samsite.ca',
    url='https://github.com/inhumantsar/python-ec2-reaper',
    packages=['ec2_reaper'],
    entry_points={
        'console_scripts': [
            'ec2-reaper=ec2_reaper.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='ec2-reaper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=requirements_dev+requirements,
    setup_requires=setup_requirements,
)
