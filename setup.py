import setuptools

import aiopentdb

with open('README.md') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    install_requires = requirements.readline()

setuptools.setup(
    name='aiopentdb',
    version=aiopentdb.__version__,
    description='Python async API wrapper for OpenTDB',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CyCanCode/aiopentdb',
    author='CyCanCode',
    license='MIT',
    classifiers=[],     # TODO
    keywords='',        # TODO
    project_urls={},    # TODO
    packages=['aiopentdb'],
    install_requires=install_requires,
    python_requires=''  # TODO
)
