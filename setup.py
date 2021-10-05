"""
    setup
    ~~~~~

    Setup for :mod:`aiopentdb`.

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

import setuptools

def read(file_path):
    with open(file_path) as file:
        return file.read()

setuptools.setup(
    name='aiopentdb',
    version='1.0.0',
    description='Async Python wrapper for the OpenTDB API',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    url='https://github.com/1Prototype1/aiopentdb',
    author='CyCanCode',
    maintainer='1Prototype1',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='opentdb aiopentdb trivia',
    project_urls={
        'Source': 'https://github.com/1Prototype1/aiopentdb',
        'Tracker': 'https://github.com/1Prototype1/aiopentdb/issues'
    },
    packages=['aiopentdb'],
    include_package_data=True,
    install_requires=read('requirements.txt').splitlines(),
    extras_require={
        'dev': read('requirements-dev.txt').splitlines()
    },
    python_requires='~=3.6'
)
