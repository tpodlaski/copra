#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['autobahn>=18.8.1', 'aiohttp>=3.4.4', 'python-dateutil', 'python-dotenv', 'asynctest']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Tony Podlaski",
    author_email='tony@podlaski.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Asyncronous Python REST and WebSocket Clients for the Coinbase Pro virtual currency trading platform.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='copra coinbase pro gdax api bitcoin litecoin etherium rest websocket client',
    name='copra',
    packages=['copra', 'copra.rest', 'copra.websocket'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/tpodlaski/copra',
    version='1.2.9',
    zip_safe=False,
)
