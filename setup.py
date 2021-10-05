import setuptools

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    install_requires = requirements.readline()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Framework :: AsyncIO',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]

keywords = [
    'aiopentdb',
    'opentdb',
    'trivia'
]

project_urls = {
    'Source': 'https://github.com/1Prototype1/aiopentdb',
    'Tracker': 'https://github.com/1Prototype1/aiopentdb/issues'
}

packages = ['aiopentdb']


setuptools.setup(
    name='aiopentdb',
    version='0.4.0',
    description='Async Python wrapper for the OpenTDB API',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/1Prototype1/aiopentdb',
    author='CyCanCode',
    maintainer='1Prototype1',
    license='MIT',
    classifiers=classifiers,
    keywords=' '.join(keywords),
    project_urls=project_urls,
    packages=packages,
    install_requires=install_requires,
    python_requires='~=3.6'
)
