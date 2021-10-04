import setuptools

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    install_requires = requirements.readline()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Framework :: AsyncIO',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]

project_urls = {
    'Source': 'https://github.com/1Prototype1/aiopentdb',
    'Tracker': 'https://github.com/1Prototype1/aiopentdb/issues'
}

setuptools.setup(
    name='aiopentdb',
    version='0.2.0',
    description='Async Python wrapper for OpenTDB API',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/1Prototype1/aiopentdb',
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
