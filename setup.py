import setuptools

import aiopentdb

with open('README.md') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    install_requires = requirements.readline()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]

project_urls = {
    'Source': 'https://github.com/CyCanCode/aiopentdb',
    'Tracker': 'https://github.com/CyCanCode/aiopentdb/issues'
}

setuptools.setup(
    name='aiopentdb',
    version=aiopentdb.__version__,
    description='Async Python wrapper for OpenTDB API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CyCanCode/aiopentdb',
    author='CyCanCode',
    license='MIT',
    classifiers=classifiers,
    keywords='opentdb aiopentdb',
    project_urls=project_urls,
    packages=['aiopentdb'],
    install_requires=install_requires,
    python_requires='~=3.7',
    package_data={
        'aiopentdb': ['py.typed']
    }
)
